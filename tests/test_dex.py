#!/usr/bin/env python3
"""スポット図鑑のテスト（assert 付き）。

  python3 build.py && python3 tests/test_dex.py
"""
import asyncio, json, sys, tempfile, pathlib
from playwright.async_api import async_playwright
from common import URL, SENDAI, Mock, Check, init_script, need_build

CASTLE = (38.2514, 140.8566)


async def new_page(b, lang='ja', mock=None, has_touch=False):
    ctx = await b.new_context(viewport={'width': 820, 'height': 1180}, has_touch=has_touch)
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    mock = mock or Mock(); await pg.route('**/*', mock.route)
    await pg.add_init_script(init_script(lang)); await pg.goto(URL); await pg.wait_for_timeout(250)
    return ctx, pg, errs, mock


async def fly(pg, sp):
    await pg.evaluate("(sp)=>{S.sel={...sp,d:2500,b:247};S.pull=CFG.pullMax;launch();}", sp)
    await pg.wait_for_function("S.state==='orbit'", timeout=9000); await pg.wait_for_timeout(200)
    await pg.evaluate("back()"); await pg.wait_for_timeout(200)


async def test_import_sanitize(b, C):
    ctx, pg, errs, _ = await new_page(b)
    await pg.click('#bDemo'); await pg.wait_for_timeout(400)
    evil = {'items': {
        'evil': {'name': '<img src=x onerror="window.__xss=1">', 'lat': 38.26, 'lon': 140.88, 'url': 'javascript:window.__xss=2',
                 'thumb': 'https://example.invalid/a.jpg")', 'genre': '???', 'tags': 'notarray', 'count': '5'},
        'nocoords': {'name': 'No coords'},
        'partial': {'name': 'Partial', 'lat': 38.27, 'lon': 140.89},
    }, 'tags': ['ok', 5, None], 'days': {'2026-11-01': 2, 'bad': 3}}
    f = pathlib.Path(tempfile.mkdtemp()) / 'dex.json'; f.write_text(json.dumps(evil))
    await pg.click('#bSet'); await pg.wait_for_timeout(300)
    await pg.set_input_files('#fImport', str(f)); await pg.wait_for_timeout(300)
    toast = await pg.evaluate("$('toast').textContent")
    C.ok('2' in toast, '読み込み: 座標の無い項目は取り込まず2件', toast)
    await pg.click('#setOk'); await pg.click('#bDex'); await pg.wait_for_timeout(1400)
    st = await pg.evaluate("""(()=>({cards:[...document.querySelectorAll('.dx-card .nm')].map(e=>e.textContent),imgs:document.querySelectorAll('#dexPage img').length,
      items:Object.values(__dex.DEX.d.items).map(i=>[i.id,i.genre,Array.isArray(i.tags),i.url,i.thumb,i.count]),days:__dex.DEX.d.days,tags:__dex.DEX.d.tags}))()""")
    C.ok(len(st['cards']) == 2 and st['imgs'] == 0, '読み込み: 名前の HTML はそのまま文字として表示（要素にならない）', st['cards'])
    ev = [i for i in st['items'] if i[0] == 'evil'][0]
    C.ok(ev[1] != '???' and ev[2] and ev[3] == '' and ev[4] == '' and ev[5] == 5, '読み込み: 不正なジャンル・タグ・URL を正規化', ev)
    C.ok('bad' not in st['days'] and st['tags'][-1] == 'ok', '読み込み: 日付・タグ一覧も検証', [st['days'], st['tags']])
    await pg.click('.dx-card'); await pg.wait_for_timeout(600)
    d = await pg.evaluate("""(()=>({js:[...document.querySelectorAll('#dexPage a')].some(a=>/^javascript:/i.test(a.getAttribute('href'))),xss:window.__xss||0}))()""")
    C.ok(not d['js'] and not d['xss'], '読み込み: javascript: のリンクを作らない・スクリプトが動かない', d)
    C.ok(not errs, '読み込み: ページエラーなし', errs)
    await ctx.close()


async def test_broken_local(b, C):
    ctx = await b.new_context(viewport={'width': 820, 'height': 1180}); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); await pg.route('**/*', Mock().route)
    broken = {'items': {'A': {'name': 'A', 'lat': 38.25, 'lon': 140.85}, 'B': {'name': 'B', 'lat': 38.24, 'lon': 140.86, 'genre': 'castle', 'tags': None, 'no': 7}}}
    await pg.add_init_script(init_script('ja') + f"try{{localStorage.setItem('slingdex.v1',{json.dumps(json.dumps(broken))})}}catch(e){{}}")
    await pg.goto(URL); await pg.click('#bDemo'); await pg.wait_for_timeout(400)
    await pg.click('#bDex'); await pg.wait_for_timeout(1400)
    n = await pg.evaluate("[document.querySelectorAll('.dx-card').length,Object.values(__dex.DEX.d.items).map(i=>i.no).sort((a,b)=>a-b),$('dexN').textContent]")
    C.ok(n[0] == 2 and n[1] == [7, 8] and not errs, '古い・壊れた記録（tags 欠落等）でも図鑑が開ける', [n, errs])
    await ctx.close()


async def test_delete_last_in_genre(b, C):
    ctx, pg, errs, _ = await new_page(b)
    await pg.click('#bDemo'); await pg.wait_for_timeout(400)
    await pg.evaluate("""(()=>{const r=(n,la,lo,i)=>__dex.dexRecord({name:n,title:n,wl:'ja',lat:la,lon:lo,d:100},{intro:i,cards:[{h:'概要',t:'テスト'}]});
      r('仙台城',38.2514,140.8566,'仙台城は城である。'); r('仙台駅',38.2601,140.8824,'仙台駅は駅である。');})()""")
    await pg.click('#bDex'); await pg.wait_for_timeout(1400)
    await pg.click('#dxTabs button[data-g=castle]'); await pg.wait_for_timeout(600)
    await pg.click('.dx-card'); await pg.wait_for_timeout(600)
    await pg.click('[data-act=del]'); await pg.click('[data-act=del]'); await pg.wait_for_timeout(700)
    st = await pg.evaluate("[DV.genre,document.querySelector('#dxTabs button.on')&&document.querySelector('#dxTabs button.on').dataset.g,document.querySelectorAll('.dx-card').length]")
    C.ok(st == ['all', 'all', 1], 'ジャンルの最後の1件を削除すると「すべて」に戻る', st)
    # タグでも同じ
    await pg.evaluate("__dex.DEX.d.items['仙台駅'].tags=['行った'];renderNav();DV.tag='行った';flipTo(listHTML(),1)"); await pg.wait_for_timeout(500)
    await pg.click('.dx-card'); await pg.wait_for_timeout(500); await pg.click('[data-act=del]'); await pg.click('[data-act=del]'); await pg.wait_for_timeout(700)
    st = await pg.evaluate("[DV.tag,$('dexPage').innerText.includes('まだ記録がありません')]")
    C.ok(st == [None, True], 'タグの最後の1件を削除するとタグの絞り込みも解除', st)
    C.ok(not errs, '削除: ページエラーなし', errs)
    await ctx.close()


async def test_cross_language(b, C):
    mock = Mock()
    mock.articles[('ja', '仙台城')] = ('仙台城はテスト用の城である。\n\n== 歴史 ==\nテスト用の歴史の文章。テスト用の歴史の文章。', 'Q1')
    mock.links[('ja', '仙台城', 'en')] = 'Sendai Castle'
    mock.articles[('en', 'Sendai Castle')] = ('Sendai Castle is a test castle.\n\n== History ==\nTest history paragraph for the castle.', 'Q1')
    mock.articles[('en', 'Aoba Castle')] = ('Aoba Castle is another name used as test data for the same castle.', 'Q1')
    mock.articles[('en', 'Test Tower')] = ('Test Tower is a tower used as test data.\n\n== History ==\nTest history paragraph about the tower.', 'Q2')
    ctx, pg, errs, _ = await new_page(b, 'ja', mock)
    await pg.click('#bDemo'); await pg.wait_for_timeout(400)
    await fly(pg, {'name': '仙台城', 'title': '仙台城', 'wl': 'ja', 'lat': CASTLE[0], 'lon': CASTLE[1], 'r': 250, 'h': 120})
    await pg.evaluate("applyLang('en')"); await pg.wait_for_timeout(300)
    await fly(pg, {'name': 'Aoba Castle', 'title': 'Aoba Castle', 'wl': 'en', 'lat': CASTLE[0] + 0.0003, 'lon': CASTLE[1], 'r': 120, 'h': 40})
    st = await pg.evaluate("""(()=>{const its=Object.values(__dex.DEX.d.items);return {n:its.length,c:its[0].count,qid:its[0].qid,alias:its[0].alias,names:its[0].names,
       has:__dex.dexHas({name:'Aoba Castle',title:'Aoba Castle'})}})()""")
    C.ok(st['n'] == 1 and st['c'] == 2 and st['qid'] == 'Q1', '別の言語の名前でも同じ場所（Wikidata ID 一致）は1件として数える', st)
    C.ok(st['has'] and 'Aoba Castle' in (st['alias'] or []), 'その言語の名前でもラベルに ✓（取得済み）が付く', st)
    await pg.click('#bDex'); await pg.wait_for_timeout(1400)
    nm = await pg.evaluate("document.querySelector('.dx-card .nm').textContent")
    C.ok(nm == 'Aoba Castle', '図鑑の表示名は今の言語での名前', nm)
    await pg.click('#dxClose'); await pg.wait_for_timeout(900)
    # 英語で記録したスポットを「もう一度飛ぶ」→ 英語の記事で解説（言語を記録している）
    await fly(pg, {'name': 'Test Tower', 'title': 'Test Tower', 'wl': 'en', 'lat': 38.262, 'lon': 140.88, 'r': 120, 'h': 40})
    await pg.click('#bDex'); await pg.wait_for_timeout(1400)
    await pg.evaluate("DV.detail='Test Tower';flipTo(detailHTML(__dex.DEX.d.items['Test Tower']),1)"); await pg.wait_for_timeout(500)
    await pg.click('[data-act=fly]'); await pg.wait_for_timeout(800)
    await pg.wait_for_function("S.state==='orbit'", timeout=9000)
    card = await pg.evaluate("S.cards.map(c=>c.t).join(' ')")
    C.ok('Test Tower is a tower' in card, '英語で記録したスポットも「もう一度飛ぶ」で解説が出る', card[:80])
    await pg.evaluate("back()")
    # 統合: 書き出したファイルを別端末（空の図鑑）に読み込むと同じ内容、Wikidata ID が同じ別名の項目は統合
    exp = await pg.evaluate("JSON.stringify(__dex.dexLoad())")
    n = await pg.evaluate("""(j)=>{localStorage.removeItem('slingdex.v1');__dex.DEX.d=null;const n1=__dexMerge(JSON.parse(j));
       const n2=__dexMerge({items:{'Sendai Castle':{name:'Sendai Castle',lat:38.2514,lon:140.8566,qid:'Q1',count:9,tags:['X']}}});
       const it=__dex.dexFind('仙台城');return [n1,n2,Object.keys(__dex.DEX.d.items).length,it.count,it.tags]}""", exp)
    C.ok(n[0] == 2 and n[1] == 0 and n[2] == 2 and n[3] == 9 and 'X' in n[4], '書き出し→読み込みで復元・同じ Wikidata ID は統合', n)
    C.ok(not errs, '言語またぎ: ページエラーなし', errs)
    await ctx.close()


async def test_offline_keep_summary(b, C):
    mock = Mock(); mock.articles[('ja', '仙台城')] = ('仙台城はテスト用の城である。テスト用の説明文。', 'Q1')
    ctx, pg, errs, _ = await new_page(b, 'ja', mock)
    await pg.click('#bDemo'); await pg.wait_for_timeout(400)
    sp = {'name': '仙台城', 'title': '仙台城', 'wl': 'ja', 'lat': CASTLE[0], 'lon': CASTLE[1], 'r': 250, 'h': 120}
    await fly(pg, sp); s1 = await pg.evaluate("__dex.DEX.d.items['仙台城'].summary")
    mock.online = False; await pg.evaluate("localStorage.removeItem('ex:ja:仙台城')")
    await fly(pg, sp); s2 = await pg.evaluate("[__dex.DEX.d.items['仙台城'].summary,__dex.DEX.d.items['仙台城'].count]")
    C.ok(s1 and s2[0] == s1 and s2[1] == 2, 'オフラインで再訪しても図鑑の要約を「取得できませんでした」で上書きしない', [s1, s2])
    C.ok(not errs, '再訪: ページエラーなし', errs)
    await ctx.close()


async def test_genres(b, C):
    ctx, pg, errs, _ = await new_page(b, 'ja')
    cases = {
        'ja': [('仙台城', '', 'castle'), ('大崎八幡宮', '', 'shrine'), ('瑞鳳殿', '瑞鳳殿は、宮城県仙台市にある伊達政宗の霊屋である', 'castle'), ('アスコット・ラッフルズ・プレース・シンガポール', '', 'other'),
               ('仙台駅', '', 'station'), ('定禅寺通', '定禅寺通は仙台市の通りである', 'street')],
        'en': [('Sendai Castle', '', 'castle'), ('Ōsaki Hachiman Shrine', '', 'shrine'), ('Sendai Station', '', 'station'), ('Sensō-ji', '', 'temple'), ('Jōzenji-dōri', '', 'street'),
               ('Zuihoden', 'Zuihōden is a mausoleum of a clan, used as test data.', 'castle'),
               ('Testplace', 'Testplace is a Shinto shrine located at the foot of Mount Test.', 'shrine'),
               ('Izumi', 'Izumi is a mountain used as test data. It has a lake.', 'mt')],
        'zh': [('仙台城', '', 'castle'), ('仙台站', '', 'station'), ('測試大樓', '', 'tower'), ('某甲', '某甲是位於日本宮城縣仙台市的神社。', 'shrine'), ('某乙', '某乙是一座測試用的摩天大樓。', 'tower')],
        'ko': [('센다이성', '', 'castle'), ('센다이역', '', 'station'), ('테스트 공원', '', 'park'), ('아무개', '아무개는 일본 미야기현 센다이시에 있는 신사이다.', 'shrine'),
               ('부산광역시', '', 'other'), ('학교 앞 지역', '', 'other')],
    }
    for lang, cs in cases.items():
        await pg.evaluate(f"LANG.cur='{lang}'")
        got = await pg.evaluate("(cs)=>cs.map(([n,i])=>__dex.genreOf({name:n},i))", [[n, i] for n, i, _ in cs])
        want = [w for _, _, w in cs]
        C.ok(got == want, f'[{lang}] 名前・解説文からジャンルを判定', [f'{c[0]}:{g}≠{w}' for c, g, w in zip(cs, got, want) if g != w])
    await ctx.close()


async def test_swipe(b, C):
    ctx, pg, errs, _ = await new_page(b, 'ja', has_touch=True)
    await pg.click('#bDemo'); await pg.wait_for_timeout(400)
    await pg.evaluate("""(()=>{const r=(n,la,lo,i)=>__dex.dexRecord({name:n,title:n,wl:'ja',lat:la,lon:lo,d:100},{intro:i,cards:[{h:'概要',t:'テスト'}]});
      r('仙台城',38.2514,140.8566,''); r('仙台駅',38.2601,140.8824,''); r('大崎八幡宮',38.2693,140.8491,'');})()""")
    await pg.click('#bDex'); await pg.wait_for_timeout(1400)
    # マウスで1枚のカードの上を横にドラッグ → ジャンルが変わり、カードの詳細は開かない
    box = await pg.evaluate("(()=>{const b=document.querySelector('.dx-card').getBoundingClientRect();return [b.left,b.top,b.width,b.height]})()")
    x0, y0 = box[0] + box[2] - 15, box[1] + box[3] / 2
    await pg.mouse.move(x0, y0); await pg.mouse.down()
    for i in range(1, 7): await pg.mouse.move(x0 - i * 16, y0); await pg.wait_for_timeout(16)
    await pg.mouse.up(); await pg.wait_for_timeout(700)
    st = await pg.evaluate("[DV.genre,DV.detail]")
    C.ok(st[0] != 'all' and st[1] is None, 'カード上の横スワイプでジャンル切替（詳細は開かない）', st)
    # タッチ（iPad）での横スワイプ
    await pg.evaluate("DV.genre='all';renderNav();flipTo(listHTML(),1)"); await pg.wait_for_timeout(600)
    cdp = await ctx.new_cdp_session(pg)
    y = (await pg.evaluate("$('dexPage').getBoundingClientRect().top")) + 300; x = 600
    await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x, 'y': y}]})
    for i in range(1, 11):
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x - i * 25, 'y': y}]}); await pg.wait_for_timeout(16)
    await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); await pg.wait_for_timeout(700)
    g = await pg.evaluate("DV.genre")
    C.ok(g != 'all', 'タッチの横スワイプでもジャンルが切り替わる（iPad）', g)
    C.ok(not errs, 'スワイプ: ページエラーなし', errs)
    await ctx.close()


async def main():
    need_build(); C = Check('図鑑')
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for f in (test_import_sanitize, test_broken_local, test_delete_last_in_genre, test_cross_language, test_offline_keep_summary, test_genres, test_swipe):
            print(f'-- {f.__name__}')
            try:
                await f(b, C)
            except Exception as e:
                C.ok(False, f'{f.__name__} が例外で中断', repr(e)[:300])
        await b.close()
    return C.done()

if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
