import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':820,'height':1180})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    async def route(r):
      if r.request.url.startswith('file:'): return await r.continue_()
      await r.abort()
    await pg.route('**/*',route)
    await pg.add_init_script("try{localStorage.setItem('lang','ja')}catch(e){}")
    await pg.goto('file:///home/claude/proto/sling-spot-ar-prototype.html'); await pg.wait_for_timeout(300)
    o={}
    o['disabledBefore']=await pg.evaluate("[$('bStart').disabled,$('bDemo').disabled]")
    o['footer']=await pg.evaluate("$('legalF').innerText.replace(/\\n/g,' / ')")
    await pg.screenshot(path='a0_intro.png')
    await pg.click('#agreeTx a[data-doc=terms]'); await pg.wait_for_timeout(200)
    o['termsOpen']=await pg.evaluate("[$('about').classList.contains('show'),$('abBody').querySelector('h3').textContent,$('abBody').innerText.includes('前橋地方裁判所')]")
    await pg.screenshot(path='a1_terms.png')
    await pg.click('#abTabs button[data-k=privacy]'); o['privacy']=await pg.evaluate("[$('abBody').querySelectorAll('.dt tr').length, $('abBody').innerText.includes('info@stony.jp')]")
    await pg.click('#abTabs button[data-k=lic]'); o['lic']=await pg.evaluate("[$('abBody').innerText.includes('OpenStreetMap'), $('abBody').querySelector('pre.lic').textContent.length]")
    await pg.click('#abTabs button[data-k=log]'); o['log']=await pg.evaluate("[$('abBody').querySelectorAll('.cl').length,$('abBody').innerText.split('\\n').slice(0,5).join(' | ')]")
    await pg.screenshot(path='a2_about.png')
    await pg.click('#abClose')
    await pg.check('#agree'); o['enabledAfter']=await pg.evaluate("[$('bStart').disabled,$('bDemo').disabled,localStorage.getItem('terms.agreed')]")
    await pg.reload(); await pg.wait_for_timeout(200); o['remembered']=await pg.evaluate("[$('agree').checked,$('bStart').disabled]")
    # 英語表示
    await pg.evaluate("applyLang('en')"); await pg.click('#legalF a'); o['en']=await pg.evaluate("$('abBody').querySelector('h3').textContent+' / '+$('abTabs').innerText.replace(/\\n/g,',')")
    await pg.click('#abTabs button[data-k=terms]'); o['enTerms']=await pg.evaluate("$('abBody').innerText.includes('Maebashi District Court')")
    await pg.click('#abClose'); await pg.evaluate("applyLang('ja')")
    # 設定画面から開く
    await pg.click('#bDemo'); await pg.wait_for_timeout(1200)
    if await pg.evaluate("$('coach').classList.contains('show')"): await pg.click('#coachOk')
    await pg.click('#bSet'); await pg.wait_for_timeout(200); await pg.screenshot(path='a3_settings.png')
    await pg.click('#setSheet [data-doc=lic]'); o['fromSettings']=await pg.evaluate("$('abBody').querySelector('h3').textContent")
    for k,v in o.items(): print(k,v)
    print('errs',errs); await b.close()
asyncio.run(main())
