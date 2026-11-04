#!/usr/bin/env python3
"""オフラインのテスト（assert 付き）: 保存エリアの再利用・言語切替時の代替・保存状態の表示・通信回復・Service Worker。

  python3 build.py && python3 tests/test_offline.py
  （SSAR_SW=別の sw.js で、その Service Worker を検査できる）
"""
import asyncio, http.server, os, pathlib, shutil, socketserver, sys, tempfile, threading, time
from playwright.async_api import async_playwright
from common import URL, ROOT, BUILD, SENDAI, Mock, Check, init_script, need_build

SW = pathlib.Path(os.environ.get('SSAR_SW') or ROOT / 'sw.js')


def mock_sendai():
    m = Mock()
    m.geo['ja'] = [('テスト公園', 38.2560, 140.8700), ('テスト美術館', 38.2580, 140.8750)]
    m.geo['en'] = [('Test Park', 38.2560, 140.8700)]
    m.articles[('ja', '仙台城')] = ('仙台城はテスト用の城である。\n\n== 歴史 ==\nテスト用の歴史の文章である。テスト用の歴史の文章である。', 'Q1')
    m.articles[('ja', 'テスト公園')] = ('テスト公園はテスト用の公園である。', 'Q2')
    m.links[('ja', '仙台城', 'en')] = 'Sendai Castle'
    m.articles[('en', 'Sendai Castle')] = ('Sendai Castle is a castle used as test data.\n\n== History ==\nTest history paragraph for the castle.', 'Q1')
    return m


async def app_offline(b, C):
    mock = mock_sendai()
    ctx = await b.new_context(viewport={'width': 820, 'height': 1180}); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); await pg.route('**/*', mock.route)
    await pg.add_init_script(init_script('ja')); await pg.goto(URL)
    await pg.click('#bDemo'); await pg.wait_for_timeout(800)
    # 1) 日本語で「この周辺を保存」
    await pg.evaluate("saveArea()"); await pg.wait_for_function("!$('bOff').disabled&&JSON.parse(localStorage.getItem('area:ja')||'{}').nEx!=null", timeout=60000)
    info = await pg.evaluate("[$('offInfo').textContent,JSON.parse(localStorage.getItem('area:ja')).spots.length]")
    C.ok(info[0].startswith('保存済み：') and info[1] > 0, 'この周辺を保存できる', info)
    # 2) 再読み込み後も「保存済み」と表示（従来は初期文に戻っていた）
    await pg.reload(); await pg.wait_for_timeout(300)
    C.ok((await pg.evaluate("$('offInfo').textContent")).startswith('保存済み：'), '再読み込み後も保存済みと表示される')
    # 3) オフライン＋英語に切替 → 日本語で保存したエリアを代わりに使う
    mock.online = False
    await pg.click('#bDemo'); await pg.wait_for_timeout(300)
    await pg.evaluate("applyLang('en')"); await pg.wait_for_function("S.debug.offline===true", timeout=8000)
    names = await pg.evaluate("S.spots.map(s=>s.name)")
    C.ok('テスト公園' in names and 'Sendai Castle' in names and '仙台城' not in names, 'オフライン・別言語でも保存エリアのスポットが出る（既定スポットは英語名）', names)
    C.ok((await pg.evaluate("$('offInfo').textContent")).startswith('Saved'), '保存状態の表示も英語', await pg.evaluate("$('offInfo').textContent"))
    # 4) 英語の記事を保存していなくても、保存済みの日本語の記事で解説（「取得できませんでした」にしない）
    r = await pg.evaluate("explain(fallbackSpots()[0]).then(r=>[r.lang,r.noex||false,r.cards.map(c=>c.t).join(' ').slice(0,30)])")
    C.ok(r[0] == 'ja' and not r[1] and 'テスト' in r[2], 'オフライン: 訳の記事が無いときは保存済みの元の言語の記事で解説', r)
    # 5) 英語でオンライン時に一度見た記事は、オフラインでも言語間リンクを保存してあるので英語で解説
    mock.online = True; await pg.evaluate("explain(fallbackSpots()[0])"); mock.online = False
    r = await pg.evaluate("explain(fallbackSpots()[0]).then(r=>[r.lang,r.noex||false,r.cards[0].t.slice(0,20)])")
    C.ok(r[0] == 'en' and not r[1] and r[2].startswith('Sendai Castle'), 'オフライン: 言語間リンクを保存して英語の記事にたどり着く', r)
    # 6) 通信が戻ったら取り直す
    mock.online = True; n0 = len(mock.calls)
    await pg.evaluate("window.dispatchEvent(new Event('online'))"); await pg.wait_for_timeout(800)
    C.ok(any('geosearch' in u for u in mock.calls[n0:]) and await pg.evaluate("S.debug.offline===false"), '通信回復で周辺スポットを再取得する')
    C.ok(not errs, 'オフライン(アプリ): ページエラーなし', errs)
    await ctx.close()


async def no_saved_data(b, C):
    """保存データの無い場所でオフライン → 起動チェックに「通信できません」と出す（従来は件数を ✓ で表示）"""
    mock = Mock(); mock.online = False
    ctx = await b.new_context(viewport={'width': 820, 'height': 1180}); pg = await ctx.new_page(); await pg.route('**/*', mock.route)
    await pg.add_init_script(init_script('ja')); await pg.goto(URL)
    r = await pg.evaluate("(async()=>{$('intro').style.display='none';S.demo=false;S.pos={lat:1.2834,lon:103.8607,acc:10};S.fetchCtr=null;S.fetching=0;await refreshSpots();return [BOOT.ok.spots,BOOT.spots[1]]})()")
    C.ok(r[0] is False and r[1] == '通信できません（保存データなし）', 'オフラインで保存データも無いときは起動チェックで ✗ 通信できません', r)
    await ctx.close()


class Srv:
    """Service Worker 検査用のローカル HTTP サーバー（index.html の応答を遅らせられる）"""
    def __init__(self, d):
        self.dir = d; self.delay = 0; me = self
        class H(http.server.SimpleHTTPRequestHandler):
            def __init__(s, *a, **k): super().__init__(*a, directory=str(me.dir), **k)
            def log_message(s, *a): pass
            def end_headers(s): s.send_header('Cache-Control', 'no-store'); super().end_headers()
            def do_GET(s):
                if s.path.split('?')[0] in ('/', '/index.html') and me.delay: time.sleep(me.delay)
                return super().do_GET()
        socketserver.ThreadingTCPServer.allow_reuse_address = True
        self.srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), H); self.srv.daemon_threads = True
        self.port = self.srv.server_address[1]; threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def write(self, ver):
        html = BUILD.read_text().replace('<head>', f'<head><meta name="ssar-test" content="{ver}">', 1)
        (self.dir / 'index.html').write_text(html)


async def service_worker(b, C):
    d = pathlib.Path(tempfile.mkdtemp(prefix='ssar-sw-')); shutil.copy(SW, d / 'sw.js')
    s = Srv(d); s.write('v1'); base = f'http://127.0.0.1:{s.port}/'
    ctx = await b.new_context(viewport={'width': 820, 'height': 1180})
    async def route(r):
        u = r.request.url
        return await (r.continue_() if u.startswith(base) else r.abort())
    await ctx.route('**/*', route)
    pg = await ctx.new_page(); await pg.add_init_script(init_script('ja'))
    await pg.goto(base)
    await pg.evaluate("navigator.serviceWorker.register('sw.js').then(()=>navigator.serviceWorker.ready)")
    await pg.reload(); await pg.wait_for_timeout(500)
    C.ok(await pg.evaluate("!!navigator.serviceWorker.controller"), 'SW: ページを制御している')
    # オフラインでも開ける
    await ctx.set_offline(True); await pg.reload(); await pg.wait_for_timeout(500)
    v = await pg.evaluate("(document.querySelector('meta[name=ssar-test]')||{}).content")
    C.ok(v == 'v1' and await pg.evaluate("!!document.getElementById('intro')"), 'SW: オフラインでもアプリが開く', v)
    await ctx.set_offline(False)
    # 回線が遅い（本体の応答が6秒）: 4秒で保存版を表示し、遅れて届いた新版は保存して次回から使う
    s.write('v2'); s.delay = 6
    t0 = time.time(); await pg.reload(); el = time.time() - t0
    v = await pg.evaluate("document.querySelector('meta[name=ssar-test]').content")
    C.ok(v == 'v1' and el < 5.8, 'SW: 応答が遅いときは保存版をすぐ表示（4秒）', [v, round(el, 1)])
    await pg.wait_for_timeout(4000)
    cached = await pg.evaluate("caches.open('ssar-app-v2').then(c=>c.match(location.href)).then(r=>r&&r.text()).then(t=>t&&(t.match(/name=\"ssar-test\" content=\"(v\\d)\"/)||[])[1])")
    C.ok(cached == 'v2', 'SW: 遅れて届いた新しい版をキャッシュに保存する（従来は古い版のまま）', cached)
    await pg.reload(); await pg.wait_for_timeout(300)   # 回線は遅いまま（6秒）
    C.ok(await pg.evaluate("document.querySelector('meta[name=ssar-test]').content") == 'v2', 'SW: 遅い回線のままでも次に開いたときは新しい版になる')
    s.delay = 0
    await ctx.close(); s.srv.shutdown()


async def main():
    need_build(); C = Check('オフライン')
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for f in (app_offline, no_saved_data, service_worker):
            print(f'-- {f.__name__}')
            try:
                await f(b, C)
            except Exception as e:
                C.ok(False, f'{f.__name__} が例外で中断', repr(e)[:300])
        await b.close()
    return C.done()

if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
