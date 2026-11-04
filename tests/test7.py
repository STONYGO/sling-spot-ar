import asyncio, json
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':820,'height':1180})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    async def route(r):
      u=r.request.url; H={'access-control-allow-origin':'*'}
      if u.startswith('file:'): return await r.continue_()
      if 'prop=extracts' in u: return await r.fulfill(status=200,content_type='application/json',headers=H,body=json.dumps({'query':{'pages':{'1':{'extract':'泉ヶ岳は宮城県の山である。','fullurl':'https://ja.wikipedia.org/wiki/x'}}}}))
      if 'wiki' in u or 'overpass' in u: return await r.fulfill(status=200,content_type='application/json',headers=H,body='{"query":{"geosearch":[]},"results":{"bindings":[]},"elements":[]}')
      await r.abort()
    await pg.route('**/*',route)
    await pg.add_init_script("try{localStorage.setItem('terms.agreed','2026-11-04')}catch(e){}")
    await pg.goto('file:///home/claude/proto/sling-spot-ar-prototype.html')
    await pg.click('#bDemo'); await pg.wait_for_timeout(900)
    out={'coach':await pg.evaluate("$('coach').classList.contains('show')")}
    await pg.screenshot(path='s11_coach.png'); await pg.click('#coachOk')
    h=await pg.evaluate("__geo.bearing(38.2601,140.8824,38.3433,140.7558)"); await pg.evaluate(f"S.heading={h};S.pitch=1")
    await pg.wait_for_timeout(300)
    out['labels']=await pg.evaluate("S.labels.map(r=>r.c.s.name)")
    await pg.screenshot(path='s12_labels.png')
    # ラベルをタップ→そのまま引いて発射
    r=await pg.evaluate("(()=>{const r=S.labels.find(r=>r.c.s.name==='泉ヶ岳');return [(r.x0+r.x1)/2,(r.y0+r.y1)/2]})()")
    await pg.mouse.move(*r); await pg.mouse.down(); await pg.wait_for_timeout(80)
    out['tapLock']=await pg.evaluate("[S.state,S.sel&&S.sel.name]")
    for i in range(12): await pg.mouse.move(r[0],r[1]+20+i*22); await pg.wait_for_timeout(12)
    await pg.mouse.up(); await pg.wait_for_timeout(5600)
    out['flew']=await pg.evaluate("[S.state,S.cur&&S.cur.name]")
    await pg.click('#bBack'); await pg.wait_for_timeout(1000)
    out['gotMark']=await pg.evaluate("document.querySelector('#lbl').innerHTML.includes('✓')")
    # 方位合わせ: ドラッグでラベル移動
    x0=await pg.evaluate("S.labels.find(r=>r.c.s.name==='泉ヶ岳').c.pt.x")
    await pg.click('#bAlign'); await pg.mouse.move(400,600); await pg.mouse.down()
    for i in range(10): await pg.mouse.move(400+i*10,600); await pg.wait_for_timeout(10)
    await pg.mouse.up(); await pg.wait_for_timeout(200); await pg.click('#bAlign'); await pg.wait_for_timeout(200)
    x1=await pg.evaluate("S.labels.find(r=>r.c.s.name==='泉ヶ岳').c.pt.x"); out['alignShift']=round(x1-x0)
    # 図鑑: 連続日数・実績・共有ボタン
    await pg.click('#bDex'); await pg.wait_for_timeout(1500)
    out['dexHead']=await pg.evaluate("$('dxTitle').innerText.replace(/\\n/g,' ')")
    out['badges']=await pg.evaluate("[...document.querySelectorAll('.dx-badge')].map(b=>(b.classList.contains('lock')?'×':'○')+b.innerText)")
    await pg.screenshot(path='s13_dex.png')
    await pg.click('.dx-card'); await pg.wait_for_timeout(600); out['shareBtn']=await pg.evaluate("!!document.querySelector('[data-act=share]')")
    await pg.click('#dxClose'); await pg.wait_for_timeout(1000)
    # 車窓の自動案内
    out['announce']=await pg.evaluate("""new Promise(res=>{S.demo=false;S.moving=true;S.side=1;S.visReady=true;S.pos={lat:38.2601,lon:140.8824,acc:10,speed:20,course:0,ts:Date.now()};
      const P=S.pos; S.spots=[{name:'右の塔',lat:P.lat,lon:P.lon+1000/(111320*Math.cos(P.lat*Math.PI/180)),r:100,h:60},{name:'左の塔',lat:P.lat,lon:P.lon-1000/(111320*Math.cos(P.lat*Math.PI/180)),r:100,h:60}];
      setTimeout(()=>res([...S.announced]),2800)})""")
    for k,v in out.items(): print(k,v)
    print('errs',errs); await b.close()
asyncio.run(main())
