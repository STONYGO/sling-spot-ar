import asyncio, json
from playwright.async_api import async_playwright
EXT="仙台城は、宮城県仙台市青葉区にあった日本の城。別名は青葉城。\n\n== 歴史 ==\n1600年、伊達政宗が築城を開始した。\n"
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':820,'height':1180})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    async def route(r):
      u=r.request.url; H={'access-control-allow-origin':'*'}
      if u.startswith('file:'): return await r.continue_()
      if 'prop=extracts' in u: return await r.fulfill(status=200,content_type='application/json',headers=H,body=json.dumps({'query':{'pages':{'1':{'extract':EXT,'fullurl':'https://ja.wikipedia.org/wiki/x'}}}}))
      if 'wiki' in u or 'overpass' in u: return await r.fulfill(status=200,content_type='application/json',headers=H,body='{"query":{"geosearch":[]},"results":{"bindings":[]},"elements":[]}')
      await r.abort()
    await pg.route('**/*',route)
    await pg.add_init_script("try{localStorage.setItem('coach.v1','1');localStorage.setItem('terms.agreed','2026-11-04')}catch(e){}"); await pg.goto('file:///home/claude/proto/sling-spot-ar-prototype.html')
    g=await pg.evaluate("""[['仙台城',''],['大崎八幡宮',''],['瑞鳳殿','瑞鳳殿は、宮城県仙台市にある伊達政宗の霊屋である'],['泉ヶ岳',''],['アスコット・ラッフルズ・プレース・シンガポール',''],['仙台駅',''],['定禅寺通','定禅寺通は仙台市の通りである']].map(([n,i])=>n+':'+__dex.genreOf({name:n,kind:n==='泉ヶ岳'?'mt':''},i))""")
    print(g)
    await pg.click('#bDemo'); await pg.wait_for_timeout(200)
    async def shoot(target):
      h=await pg.evaluate(f"__geo.bearing(38.2601,140.8824,{target[0]},{target[1]})"); await pg.evaluate(f"S.heading={h};S.pitch=0")
      await pg.mouse.move(410,700); await pg.mouse.down(); await pg.wait_for_timeout(450)
      for i in range(12): await pg.mouse.move(410,720+i*25); await pg.wait_for_timeout(12)
      await pg.mouse.up(); await pg.wait_for_timeout(5600)
    await shoot((38.2514,140.8566))
    await pg.screenshot(path='s7_got.png')
    st=await pg.evaluate("[S.state,Object.values(__dex.DEX.d.items).map(i=>[i.no,i.name,i.genre,i.count])]"); print(st)
    await pg.click('#cTagB'); await pg.wait_for_timeout(300); await pg.click('#tsChips button:nth-child(3)'); await pg.fill('#tsIn','夜景'); await pg.click('#tsAdd'); await pg.click('#tsOk')
    print('tags',await pg.evaluate("S.curRec.tags"))
    await pg.click('#bBack'); await pg.wait_for_timeout(1200)
    await shoot((38.2693,140.8491)); await pg.click('#bBack'); await pg.wait_for_timeout(1200)
    await pg.click('#bDex'); await pg.wait_for_timeout(450); await pg.screenshot(path='s8_opening.png')
    await pg.wait_for_timeout(1200); await pg.screenshot(path='s9_list.png')
    await pg.click('.dx-card'); await pg.wait_for_timeout(700); await pg.screenshot(path='s10_detail.png')
    await pg.click('[data-act=back]'); await pg.wait_for_timeout(600)
    await pg.click('#dxTabs button:nth-child(2)'); await pg.wait_for_timeout(600); print('tab',await pg.evaluate("[DV.genre,document.querySelectorAll('.dx-card').length]"))
    await pg.click('.dx-card'); await pg.wait_for_timeout(600); await pg.click('[data-act=fly]'); await pg.wait_for_timeout(6500)
    print('refly',await pg.evaluate("[S.state,S.cur&&S.cur.name,Object.values(__dex.DEX.d.items).map(i=>i.count)]"))
    # 永続化: リロード後も残る
    print('before reload',await pg.evaluate("[Object.keys(localStorage), (localStorage.getItem('slingdex.v1')||'').length]"))
    await pg.reload(); await pg.wait_for_timeout(300); print('after reload',await pg.evaluate("Object.keys(localStorage)")); print('persist',await pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('slingdex.v1')).items)"))
    print('errs',errs); await b.close()
asyncio.run(main())
