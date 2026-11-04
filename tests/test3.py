import asyncio, json
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':820,'height':1180})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    async def route(r):
      u=r.request.url
      if u.startswith('file:'): await r.continue_()
      elif 'wikipedia' in u or 'wikidata' in u: await r.fulfill(status=200,content_type='application/json',headers={'access-control-allow-origin':'*'},body='{"query":{"geosearch":[],"pages":{"1":{"extract":"テスト。説明。"}}},"results":{"bindings":[]}}')
      else: await r.abort()
    await pg.route('**/*',route)
    await pg.add_init_script("try{localStorage.setItem('coach.v1','1');localStorage.setItem('terms.agreed','2026-11-04')}catch(e){}"); await pg.goto('file:///home/claude/proto/sling-spot-ar-prototype.html'); await pg.click('#bDemo'); await pg.wait_for_timeout(200)
    h=await pg.evaluate("__geo.bearing(38.2601,140.8824,38.2514,140.8566)"); await pg.evaluate(f"S.heading={h}")
    y0=1000  # 画面下端近くでロック
    await pg.mouse.move(410,y0); await pg.mouse.down(); await pg.wait_for_timeout(450)
    for i in range(16): await pg.mouse.move(410-i*12,y0+i*10); await pg.wait_for_timeout(15)
    st=await pg.evaluate("[S.state,Math.round(S.gain*10)/10,Math.round(S.pull),S.armed]")
    await pg.screenshot(path='s5_low.png')
    await pg.mouse.up(); await pg.wait_for_timeout(300); st2=await pg.evaluate("S.state")
    await pg.screenshot(path='s6_fire.png')
    await pg.wait_for_timeout(4500); st3=await pg.evaluate("S.state")
    print(st,st2,st3,errs); await b.close()
asyncio.run(main())
