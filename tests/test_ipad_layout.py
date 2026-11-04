#!/usr/bin/env python3
"""iPad 表示のテスト（assert 付き）: 各 iPad サイズ・言語で、ボタンや表示が重ならず画面内に収まるか。

  python3 build.py && python3 tests/test_ipad_layout.py
"""
import asyncio, sys
from playwright.async_api import async_playwright
from common import URL, IPAD_UA, IPAD_SIZES, SENDAI, Mock, Check, init_script, need_build, RECTS_JS, overlap

COMBOS = [(s, l) for s in IPAD_SIZES for l in ('ja', 'en')] + [('split_third', 'ko'), ('split_half', 'ko'), ('air_landscape', 'zh')]
TEXT_RECT = """(id)=>{const e=document.getElementById(id);if(!e||getComputedStyle(e).display==='none'||!e.textContent.trim())return null;
  const r=document.createRange();r.selectNodeContents(e);const b=r.getBoundingClientRect();return [b.left,b.top,b.right,b.bottom]}"""


async def run_combo(b, size, lang, C, orbit=False):
    W, H = IPAD_SIZES[size]; tag = f'[{size} {W}x{H} {lang}]'
    ctx = await b.new_context(viewport={'width': W, 'height': H}, has_touch=True, is_mobile=True, user_agent=IPAD_UA)
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    mock = Mock(); mock.articles[('ja', '仙台城')] = ('仙台城はテスト用の城である。\n\n== 歴史 ==\nテスト用の歴史の文章である。テスト用の歴史の文章である。', 'Q1')
    mock.links[('ja', '仙台城', 'en')] = 'Sendai Castle'; mock.articles[('en', 'Sendai Castle')] = ('Sendai Castle is a test castle.\n\n== History ==\nThis is a test history paragraph for the castle.', 'Q1')
    await pg.route('**/*', mock.route)
    await pg.add_init_script(init_script(lang, coach_done=False))
    await pg.goto(URL); await pg.wait_for_timeout(300)

    # 1) 開始画面: 要素どうしが重ならない・上端も下端もスクロールで届く
    ids = ['agreeRow', 'bStart', 'langSel', 'bDemo', 'resetL', 'legalF']
    R = await pg.evaluate(RECTS_JS, ids)
    bad = [(a, c) for i, a in enumerate(ids) for c in ids[i + 1:] if overlap(R[a], R[c])]
    C.ok(not bad, f'{tag} 開始画面の要素が重ならない', bad)
    o = await pg.evaluate("""(()=>{const i=$('intro');i.scrollTop=0;const top=document.querySelector('#intro h1').getBoundingClientRect().top;
       i.scrollTop=i.scrollHeight;const bot=$('legalF').getBoundingClientRect().bottom;i.scrollTop=0;return [top,bot,getComputedStyle(i).overflowY]})()""")
    C.ok(o[0] >= 0 and o[1] <= H + 0.5 and o[2] == 'auto', f'{tag} 開始画面の上端（タイトル）と下端（著作権表示）に届く', o)

    # 2) 初回ガイド: 「はじめる」まで届く
    await pg.click('#bDemo'); await pg.wait_for_timeout(1200)
    c = await pg.evaluate("""(()=>{const c=$('coach');if(!c.classList.contains('show'))return null;c.scrollTop=c.scrollHeight;const b=$('coachOk').getBoundingClientRect();return [b.top,b.bottom]})()""")
    C.ok(c is not None and c[0] >= 0 and c[1] <= H + 0.5, f'{tag} 初回ガイドの「はじめる」が画面内', c)
    if c is not None: await pg.click('#coachOk')
    await pg.wait_for_timeout(400)

    # 3) AR 画面（デモ）: 右上ボタン群と HUD、下段の丸ボタンとデモ操作パネル・ヒントが重ならない
    async def ar_check(label):
        R = await pg.evaluate(RECTS_JS, ['hud', 'warn', 'bAlign', 'bTrain', 'bEye', 'bSnd', 'bSet', 'bPhoto', 'bDex', 'demo', 'boot'])
        R['hintText'] = await pg.evaluate(TEXT_RECT, 'hint')
        tops = [k for k in ('bAlign', 'bTrain', 'bEye', 'bSnd') if R[k]]
        bad = [(a, k) for a in ('hud', 'warn') for k in tops if overlap(R[a], R[k])]
        bad += [(a, k) for a in ('demo', 'hintText') for k in ('bSet', 'bPhoto', 'bDex') if overlap(R[a], R[k])]
        bad += [('hud', 'warn')] if overlap(R['hud'], R['warn']) else []
        bad += [('demo', 'hintText')] if overlap(R['demo'], R['hintText']) else []
        C.ok(not bad, f'{tag} {label}: 表示どうしが重ならない', bad)
        out = [k for k, v in R.items() if v and (v[0] < -0.5 or v[1] < -0.5 or v[2] > W + 0.5 or v[3] > H + 0.5)]
        C.ok(not out, f'{tag} {label}: 画面外にはみ出さない', out)
    await ar_check('AR(デモ)')
    # 実機相当: 目線・車窓ボタンも出し、警告（低精度）も表示した状態
    await pg.evaluate("S.demo=false;S.pos={...S.pos,acc:120}"); await pg.wait_for_timeout(700)
    await ar_check('AR(ボタン4個＋警告)')
    # 照準ラベルが上部の表示と重ならない
    h = await pg.evaluate(f"__geo.bearing({SENDAI[0]},{SENDAI[1]},38.2514,140.8566)")
    await pg.evaluate(f"S.demo=true;S.heading={h};S.pitch=0;lock(innerWidth/2,innerHeight/2)"); await pg.wait_for_timeout(350)
    R = await pg.evaluate(RECTS_JS, ['label', 'hud', 'warn', 'bAlign', 'bSnd'])
    bad = [k for k in ('hud', 'warn', 'bAlign', 'bSnd') if overlap(R['label'], R[k])]
    C.ok(R['label'] and not bad, f'{tag} 照準ラベルが上部の表示と重ならない', (R['label'], bad))
    await pg.evaluate("cancelLock()")

    # 4) 設定シート: 画面内に収まり「閉じる」に届く
    await pg.click('#bSet'); await pg.wait_for_timeout(500)
    s = await pg.evaluate("""(()=>{const sh=document.querySelector('#setSheet .sh'),b=sh.getBoundingClientRect();sh.scrollTop=sh.scrollHeight;const o=$('setOk').getBoundingClientRect();return [b.top,b.bottom,o.bottom]})()""")
    C.ok(s[0] >= -0.5 and s[1] <= H + 0.5 and s[2] <= H + 0.5, f'{tag} 設定シートが画面内で「閉じる」に届く', s)
    await pg.click('#setOk'); await pg.wait_for_timeout(300)

    # 5) 図鑑: 本が画面内・ページ位置が見出しの下（回転後も）・スワイプ用の touch-action
    await pg.evaluate("__dex.dexRecord({name:'仙台城',title:'仙台城',wl:'ja',lat:38.2514,lon:140.8566,r:250,h:120,d:2500},{intro:'仙台城は城である。',cards:[{h:'概要',t:'テスト'}]})")
    await pg.click('#bDex'); await pg.wait_for_timeout(1400)
    LAY = """(()=>{const b=document.querySelector('.book').getBoundingClientRect(),want=document.querySelector('.dx-head').offsetHeight+$('dxNav').offsetHeight;
      return [b.left,b.top,b.right,b.bottom,parseFloat($('dexPage').style.top),want,getComputedStyle($('dexPage')).touchAction,getComputedStyle(document.querySelector('.dx-card')).touchAction]})()"""
    d = await pg.evaluate(LAY)
    C.ok(d[0] >= 0 and d[1] >= 0 and d[2] <= W and d[3] <= H, f'{tag} 図鑑の本が画面内', d[:4])
    C.ok(abs(d[4] - d[5]) <= 1, f'{tag} 図鑑のページが見出しの直下', d[4:6])
    C.ok(d[6] == 'pan-y' and d[7] == 'manipulation', f'{tag} 図鑑: 横スワイプを奪わない・ダブルタップ拡大しない', d[6:])
    await pg.set_viewport_size({'width': H, 'height': W}); await pg.wait_for_timeout(500)    # 回転
    d = await pg.evaluate(LAY)
    C.ok(d[2] <= H and d[3] <= W and abs(d[4] - d[5]) <= 1, f'{tag} 回転後も図鑑のレイアウトが崩れない', d[:6])
    await pg.set_viewport_size({'width': W, 'height': H}); await pg.wait_for_timeout(300)
    await pg.click('#dxClose'); await pg.wait_for_timeout(1000)

    # 6) 解説カード: 地図の出典表示と重ならない・横長でも幅を抑える
    if orbit:
        await pg.evaluate("(()=>{const sp={...fallbackSpots()[0]};sp.d=2500;sp.b=247;S.sel=sp;S.pull=CFG.pullMax;launch();})()")
        await pg.wait_for_timeout(2500)
        await pg.wait_for_function("S.state==='orbit'", timeout=8000)
        k = await pg.evaluate("""(()=>{const c=$('card').getBoundingClientRect(),a=document.querySelector('.maplibregl-ctrl-attrib');const ab=a?a.getBoundingClientRect():null;
          return {card:[c.left,c.top,c.right,c.bottom],attr:ab&&ab.width?[ab.left,ab.top,ab.right,ab.bottom]:null}})()""")
        C.ok(k['attr'] is not None and not overlap(k['card'], k['attr']), f'{tag} 解説カードと地図の出典表示が重ならない', k)
        C.ok(k['card'][2] - k['card'][0] <= 761, f'{tag} 解説カードの幅が読みやすい範囲', k['card'])
        await pg.click('#bBack')
    C.ok(not errs, f'{tag} ページエラーなし', errs)
    await ctx.close()


async def old_ipados_angle(b, C):
    """iPadOS 16.3 以前（window.orientation も screen.orientation も無い）でも横持ちの向きを推定する"""
    for (W, H), X, want in [((1180, 820), [0, 0, 1], 90), ((1180, 820), [0, 0, -1], -90), ((820, 1180), [1, 0, 0], 0)]:
        ctx = await b.new_context(viewport={'width': W, 'height': H}, user_agent=IPAD_UA); pg = await ctx.new_page()
        await pg.route('**/*', Mock().route)
        await pg.add_init_script("try{delete window.orientation}catch(e){};Object.defineProperty(Screen.prototype,'orientation',{get:()=>undefined,configurable:true});" + init_script('ja'))
        await pg.goto(URL)
        got = await pg.evaluate("(X)=>{S.forceAngle=null;S.M={X,Y:[0,0,0],Z:[0,-1,0]};return [typeof window.orientation,typeof screen.orientation,scrAngle()]}", X)
        C.ok(got[2] == want, f'古い iPadOS: {W}x{H} 端末x軸{X} → 画面の角度 {want}', got)
        await ctx.close()


async def main():
    need_build(); C = Check('iPad 表示')
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await old_ipados_angle(b, C)
        for size, lang in COMBOS:
            await run_combo(b, size, lang, C, orbit=(lang == 'ja' and size in ('air_portrait', 'air_landscape', 'split_half', 'pro13_landscape')))
        await b.close()
    return C.done()

if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
