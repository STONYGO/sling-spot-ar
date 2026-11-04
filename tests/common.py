"""assert 付きテスト（test_ipad_layout / test_i18n / test_offline / test_dex）の共通部品。

- ビルド成果物 sling-spot-ar-prototype.html を file:// で開く（先に python3 build.py）。
- 外部通信はすべてモック（Wikipedia / Wikidata / Overpass / タイル）。ネットに出ない。
- 返す文章・座標はテスト用の架空データ（実在の記事内容ではない）。
"""
import io, json, os, pathlib, re, sys
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUILD = pathlib.Path(os.environ.get('SSAR_BUILD') or ROOT / 'sling-spot-ar-prototype.html')  # SSAR_BUILD で別のビルド（例: 修正前）も検査できる
URL = BUILD.as_uri()
H = {'access-control-allow-origin': '*'}
IPAD_UA = ('Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 '
           '(KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1')
# iPad の代表的な表示領域（CSS px）。Split View / Slide Over は横持ち時の幅
IPAD_SIZES = {
    'mini_portrait': (768, 1024), 'air_portrait': (820, 1180), 'air_landscape': (1180, 820),
    'pro13_portrait': (1024, 1366), 'pro13_landscape': (1366, 1024),
    'split_half': (590, 820), 'split_third': (375, 820),
}
SENDAI = (38.2601, 140.8824)


def png(rgb):
    im = Image.new('RGB', (256, 256), rgb); b = io.BytesIO(); im.save(b, 'PNG'); return b.getvalue()


FLAT = png((128, 10, 0))   # terrarium で標高約 10m の平地


def init_script(lang=None, agreed=True, coach_done=True, extra=''):
    js = 'try{'
    if lang: js += f"localStorage.setItem('lang','{lang}');"
    if agreed: js += "localStorage.setItem('terms.agreed','2026-11-04');"
    if coach_done: js += "localStorage.setItem('coach.v1','1');"
    return js + '}catch(e){}' + extra


class Mock:
    """外部 API のモック。言語ごとの geosearch 結果・記事・言語間リンクを設定できる。"""
    def __init__(self):
        self.online = True
        self.geo = {}        # lang -> [(title, lat, lon)]
        self.articles = {}   # (lang, title) -> (extract, qid)
        self.links = {}      # (from, title, to) -> title
        self.calls = []

    async def route(self, r):
        u = r.request.url
        if u.startswith('file:') or u.startswith('http://127.0.0.1') or u.startswith('http://localhost'):
            return await r.continue_()
        self.calls.append(u)
        if not self.online:
            return await r.abort()
        m = re.match(r'https://(\w+)\.wikipedia\.org/', u)
        if 'terrarium' in u:
            return await r.fulfill(status=200, content_type='image/png', headers=H, body=FLAT)
        if 'overpass' in u:
            return await r.fulfill(status=200, content_type='application/json', headers=H, body='{"elements":[]}')
        if 'wikidata' in u:
            return await r.fulfill(status=200, content_type='application/json', headers=H, body='{"results":{"bindings":[]}}')
        if m:
            from urllib.parse import urlparse, parse_qs, quote
            lang = m.group(1); q = parse_qs(urlparse(u).query)
            if 'geosearch' in u:
                gs = [{'title': t, 'lat': la, 'lon': lo} for t, la, lo in self.geo.get(lang, [])]
                return await r.fulfill(status=200, content_type='application/json', headers=H, body=json.dumps({'query': {'geosearch': gs}}))
            title = (q.get('titles') or [''])[0]
            if 'langlinks' in u:
                to = (q.get('lllang') or [''])[0]; v = self.links.get((lang, title, to))
                page = {'title': title, **({'langlinks': [{'lang': to, '*': v}]} if v else {})}
                return await r.fulfill(status=200, content_type='application/json', headers=H, body=json.dumps({'query': {'pages': {'1': page}}}))
            if 'prop=extracts' in u:
                a = self.articles.get((lang, title))
                page = {'title': title}
                if a:
                    page.update({'extract': a[0], 'fullurl': f'https://{lang}.wikipedia.org/wiki/' + quote(title.replace(' ', '_'))})
                    if a[1]: page['pageprops'] = {'wikibase_item': a[1]}
                else:
                    page['missing'] = ''
                return await r.fulfill(status=200, content_type='application/json', headers=H, body=json.dumps({'query': {'pages': {'1': page}}}))
            return await r.fulfill(status=200, content_type='application/json', headers=H, body='{"query":{}}')
        return await r.abort()   # 地図タイル等は使わない


class Check:
    def __init__(self, name):
        self.name = name; self.fails = []; self.n = 0

    def ok(self, cond, msg, detail=None):
        self.n += 1
        print(('  PASS ' if cond else '  FAIL ') + msg + ('' if cond or detail is None else f'  -> {detail}'))
        if not cond: self.fails.append(msg)
        return cond

    def done(self):
        print(f'== {self.name}: {self.n - len(self.fails)}/{self.n} passed')
        return 1 if self.fails else 0


def need_build():
    if not BUILD.exists():
        sys.exit('build first: python3 build.py')


# 画面上の要素の矩形（表示されていなければ None）
RECTS_JS = """(ids)=>Object.fromEntries(ids.map(id=>{const e=document.getElementById(id);if(!e)return [id,null];
  const cs=getComputedStyle(e);let p=e,shown=true;while(p&&p!==document.body){const c=getComputedStyle(p);if(c.display==='none'||c.visibility==='hidden'){shown=false;break}p=p.parentElement}
  const b=e.getBoundingClientRect();return [id,shown&&b.width>0&&b.height>0?[b.left,b.top,b.right,b.bottom]:null]}))"""


def overlap(a, b, pad=0):
    return a and b and not (a[2] <= b[0] + pad or b[2] <= a[0] + pad or a[3] <= b[1] + pad or b[3] <= a[1] + pad)
