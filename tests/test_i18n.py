#!/usr/bin/env python3
"""多言語のテスト（assert 付き）: 英語・中国語（繁體）・韓国語で、画面に日本語が残っていないか。

  python3 build.py && python3 tests/test_i18n.py

判定: en/ko は「かな・漢字が無いこと」、zh は「かな・日本の新字体（図・駅・続 等）が無いこと」。
規約・プライバシー等の法務文書は zh/ko では英語版を表示する設計のため、会社名など許可した語を除いて「かなが無いこと」だけを見る。
"""
import asyncio, pathlib, re, sys
from playwright.async_api import async_playwright
from common import URL, ROOT, SENDAI, Mock, Check, init_script, need_build

KANA = re.compile(r'[぀-ヿㇰ-ㇿ]')
CJK = re.compile(r'[㐀-鿿]')
SHINJITAI = re.compile('[図覧駅鉄続録戻読説関発対応証写変転伝広囲経済検険験訳歴価営画会拡楽気区県権効号国歳雑実釈収従渋処称条状乗触数声静専戦総装蔵属帯単担団断遅庁聴点灯当独届廃売抜浜仏払弁歩宝満薬与様来乱竜両緑礼励霊齢労湾学恵桜絵軽]')
# 許可する語: 会社名・法務文書内のアプリ名・言語名、地図の出典表示「地理院タイル」（国土地理院の出典表記。訳さずそのまま表示）
ALLOW = ['STONY株式会社', 'Sling Spot AR（仮称）', '日本語', '中文（繁體）', '地理院タイル']
# 画面に見えている文字（select の選択肢・非表示要素は除く）
VIS_TEXT = """(sel)=>{const root=typeof sel==='string'?document.querySelector(sel):document.body;if(!root)return '';const out=[];
  const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;
  while((n=w.nextNode())){let p=n.parentElement,ok=true;while(p){if(p.tagName==='SELECT'||p.tagName==='SCRIPT'||p.tagName==='STYLE'){ok=false;break}const c=getComputedStyle(p);if(c.display==='none'||c.visibility==='hidden'){ok=false;break}p=p.parentElement}
    if(ok&&n.textContent.trim())out.push(n.textContent.trim())}
  for(const e of root.querySelectorAll('input[placeholder]'))out.push(e.placeholder);return out.join(' | ')}"""
SPOTS = {  # テスト用の架空の周辺スポット（各言語の Wikipedia が返す想定の名前）
    'en': [('Sendai Castle', 38.2525, 140.8558), ('Zuihoden Mausoleum', 38.2478, 140.8786), ('Aoba Test Park', 38.2560, 140.8700)],
    'zh': [('仙台城', 38.2525, 140.8558), ('青葉測試公園', 38.2560, 140.8700)],
    'ko': [('센다이성', 38.2525, 140.8558), ('아오바 테스트 공원', 38.2560, 140.8700)],
}
EXTRACT = {
    'en': ('Sendai Castle', 'Sendai Castle is a castle used as test data.\n\n== History ==\nThis paragraph is test data about the history of the castle.'),
    'zh': ('仙台城', '仙台城是測試用資料中的城堡。\n\n== 歷史 ==\n這一段是關於城堡歷史的測試用資料。'),
    'ko': ('센다이성', '센다이성은 테스트용 데이터의 성이다.\n\n== 역사 ==\n이 단락은 성의 역사에 관한 테스트용 데이터이다.'),
}


def bad_text(lang, s):
    for a in ALLOW: s = s.replace(a, '')
    if lang == 'zh':
        return sorted(set(KANA.findall(s) + SHINJITAI.findall(s)))
    return sorted(set(KANA.findall(s) + CJK.findall(s)))


async def run_lang(b, lang, C):
    tag = f'[{lang}]'
    ctx = await b.new_context(viewport={'width': 820, 'height': 1180}, has_touch=True)
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    mock = Mock(); mock.geo[lang] = SPOTS[lang]
    title, ext = EXTRACT[lang]; mock.links[('ja', '仙台城', lang)] = title; mock.articles[(lang, title)] = (ext, 'Q1')
    await pg.route('**/*', mock.route)
    await pg.add_init_script(init_script(lang, agreed=False, coach_done=False))
    await pg.goto(URL); await pg.wait_for_timeout(300)
    seen = {}

    async def grab(name, sel=None):
        seen[name] = await pg.evaluate(VIS_TEXT, sel)

    C.ok(await pg.evaluate("document.documentElement.lang") == {'en': 'en', 'zh': 'zh-Hant', 'ko': 'ko'}[lang], f'{tag} <html lang> が言語に合う')
    await grab('開始画面', '#intro')
    await pg.check('#agree'); await pg.click('#bDemo'); await pg.wait_for_timeout(1500)
    await grab('初回ガイド', '#coach'); await pg.click('#coachOk'); await pg.wait_for_timeout(300)
    names = await pg.evaluate("S.spots.map(s=>s.name)")
    await grab('AR画面', '#app')
    # 既定スポットは言語の名前になり、同じ場所が二重に出ない
    if lang == 'en':
        C.ok(names.count('Sendai Castle') == 1 and not ('Zuihōden' in names and 'Zuihoden Mausoleum' in names), f'{tag} 既定スポットが英語名で重複しない', names)
    C.ok('仙台城' not in names or lang == 'zh', f'{tag} 既定スポットが日本語名のまま出ない', names)
    # 照準 → 候補チップ
    h = await pg.evaluate(f"__geo.bearing({SENDAI[0]},{SENDAI[1]},38.2514,140.8566)")
    await pg.evaluate(f"S.heading={h};S.pitch=0;lock(innerWidth/2,innerHeight/2)"); await pg.wait_for_timeout(200)
    await grab('照準ラベル', '#label'); await pg.evaluate("enterChoose()"); await grab('候補', '#chips'); await pg.evaluate("cancelLock()")
    await pg.click('#bAlign'); await grab('方位合わせ', '#app'); await pg.click('#bAlign')
    # 実機相当（目線・車窓ボタン、警告、HUD）
    await pg.evaluate("S.demo=false;S.pos={...S.pos,acc:120};S.inside={};S.compAcc=35"); await pg.wait_for_timeout(700)
    await grab('警告・HUD', '#app')
    await pg.click('#bEye'); await grab('目線トースト', '#toast'); await pg.click('#bTrain'); await grab('車窓ボタン', '#topR')
    await pg.evaluate("S.demo=true;S.inside=null;S.compAcc=null;S.trainPref='auto';$('bTrain').textContent=t('trAuto');enterMoving();"); await grab('車窓トースト', '#toast')
    await pg.evaluate("exitMoving()"); await pg.wait_for_timeout(200)
    # 設定
    await pg.click('#bSet'); await pg.wait_for_timeout(400); await grab('設定', '#setSheet'); await pg.click('#setOk')
    # 飛んで解説（既定スポット「仙台城」→ 言語間リンクで各言語の記事）
    await pg.evaluate("(()=>{const sp={...fallbackSpots()[0]};sp.d=2500;sp.b=247;S.sel=sp;S.pull=CFG.pullMax;launch();})()")
    await pg.wait_for_function("S.state==='orbit'", timeout=9000); await pg.wait_for_timeout(300)
    await grab('図鑑登録', '#got'); await pg.wait_for_timeout(1600); await grab('解説カード', '#card'); await grab('解説ボタン', '#btns')
    card = await pg.evaluate("$('card').innerText")
    C.ok(title in card and ext.split('\n')[0][:6] in card, f'{tag} 解説カードがその言語の記事', card[:80])
    await pg.click('#cTagB'); await pg.wait_for_timeout(300); await grab('タグ編集', '#tagSheet'); await pg.click('#tsOk')
    await pg.click('#bBack'); await pg.wait_for_timeout(500)
    # 図鑑（一覧・実績・詳細・削除確認）
    await pg.click('#bDex'); await pg.wait_for_timeout(1500); await grab('図鑑一覧', '#dex')
    await pg.click('.dx-card'); await pg.wait_for_timeout(700); await pg.click('[data-act=del]'); await grab('図鑑詳細', '#dex')
    await pg.click('[data-act=back]'); await pg.wait_for_timeout(600); await pg.click('#dxClose'); await pg.wait_for_timeout(1000)
    # 写真から探す
    await pg.set_input_files('#fPhoto', str(ROOT / 'tests' / 'test_photo.jpg')); await pg.wait_for_timeout(1500)
    await grab('写真', '#photoV'); await pg.click('#phClose'); await pg.wait_for_timeout(300)
    # 規約等（zh/ko は英語版。かなが無いこと）
    await pg.click('#bSet'); await pg.wait_for_timeout(300); await pg.click('#setSheet [data-doc=privacy]'); await pg.wait_for_timeout(200)
    about = await pg.evaluate(VIS_TEXT, '#about'); await pg.click('#abClose')
    for nm, txt in seen.items():
        bad = bad_text(lang, txt)
        C.ok(not bad, f'{tag} {nm}に日本語が残っていない', f'{bad} :: {txt[:160]}')
    a = about
    for x in ALLOW: a = a.replace(x, '')
    C.ok(not KANA.findall(a), f'{tag} 規約・プライバシー画面に日本語（かな）が無い')
    C.ok(not errs, f'{tag} ページエラーなし', errs)
    await ctx.close()


async def boot_texts(b, lang, C):
    """実機モードの起動チェック表示（センサー・カメラ・位置）"""
    init = init_script(lang) + """
      DeviceOrientationEvent.requestPermission=()=>Promise.resolve('granted');
      setTimeout(()=>{ setInterval(()=>{ const ev=new DeviceOrientationEvent('deviceorientation',{alpha:0,beta:88,gamma:0,absolute:false});
        Object.defineProperty(ev,'webkitCompassHeading',{value:0}); window.dispatchEvent(ev); },60); },600);"""
    ctx = await b.new_context(viewport={'width': 820, 'height': 1180}, has_touch=True, permissions=['geolocation'], geolocation={'latitude': SENDAI[0], 'longitude': SENDAI[1], 'accuracy': 15})
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    mock = Mock(); mock.geo[lang] = SPOTS[lang]; await pg.route('**/*', mock.route)
    await pg.add_init_script(init); await pg.goto(URL); await pg.wait_for_timeout(300)
    await pg.click('#bStart'); await pg.wait_for_timeout(3500)
    txt = await pg.evaluate("[...document.querySelectorAll('#bootL div')].map(d=>d.textContent).join(' | ')+' | '+$('boot').querySelector('b').textContent")
    bad = bad_text(lang, txt)
    C.ok(not bad, f'[{lang}] 起動チェックに日本語が残っていない', f'{bad} :: {txt}')
    C.ok(not errs, f'[{lang}] 起動時のページエラーなし', errs)
    await ctx.close()


async def ja_regression(b, C):
    """日本語表示は従来どおり"""
    ctx = await b.new_context(viewport={'width': 820, 'height': 1180}); pg = await ctx.new_page()
    await pg.route('**/*', Mock().route); await pg.add_init_script(init_script('ja')); await pg.goto(URL); await pg.wait_for_timeout(300)
    got = await pg.evaluate("""[$('bStart').textContent,$('bDemo').textContent,document.querySelector('#intro h1').textContent,$('agreeTx').textContent,$('abLink').textContent,
      document.querySelector('#setSheet h3').textContent,$('bOff').textContent,$('offInfo').textContent,$('coachOk').textContent,document.documentElement.lang]""")
    want = ['開始（カメラ・位置・方位を許可）', 'デモモード（センサー不要・仙台駅周辺）', 'Sling Spot AR（仮称）', '利用規約とプライバシーポリシーに同意します', 'バージョン情報・規約',
            '⚙️ 設定 / Settings', 'この周辺を保存', '現在地の半径10kmを保存（スポット・解説・地形・地図）', 'はじめる', 'ja']
    C.ok(got == want, '[ja] 日本語の表示は従来どおり', [g for g, w in zip(got, want) if g != w])
    await pg.click('#bDemo'); await pg.wait_for_timeout(500)
    C.ok((await pg.evaluate("$('hud').textContent")).startswith('方位 0° 仰角 0° [デモ]'), '[ja] HUD は従来どおり')
    C.ok(await pg.evaluate("S.spots.map(s=>s.name).join()") == '仙台城,瑞鳳殿,大崎八幡宮,仙台駅,泉ヶ岳,蔵王連峰', '[ja] 既定スポット名は従来どおり')
    await ctx.close()


async def default_lang(b, C):
    """保存された言語が無いときは端末の言語に合わせる（韓国語・繁体字の端末が英語にならない）"""
    for loc, want in [('ko-KR', 'ko'), ('zh-TW', 'zh'), ('zh-HK', 'zh'), ('ja-JP', 'ja'), ('en-US', 'en'), ('fr-FR', 'en'), ('zh-CN', 'en')]:
        ctx = await b.new_context(locale=loc); pg = await ctx.new_page(); await pg.route('**/*', Mock().route)
        await pg.goto(URL); got = await pg.evaluate("LANG.cur")
        C.ok(got == want, f'端末の言語 {loc} → 表示 {want}', got); await ctx.close()


async def main():
    need_build(); C = Check('多言語')
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream'])
        await ja_regression(b, C)
        await default_lang(b, C)
        for lang in ('en', 'zh', 'ko'):
            await run_lang(b, lang, C)
            await boot_texts(b, lang, C)
        await b.close()
    return C.done()

if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
