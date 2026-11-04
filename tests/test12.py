import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':820,'height':1180})
    async def route(r):
      if r.request.url.startswith('file:'): return await r.continue_()
      if 'wiki' in r.request.url: return await r.fulfill(status=200,content_type='application/json',headers={'access-control-allow-origin':'*'},body='{"query":{"geosearch":[]},"results":{"bindings":[]}}')
      await r.abort()
    await pg.route('**/*',route); await pg.add_init_script("try{localStorage.setItem('coach.v1','1');localStorage.setItem('terms.agreed','2026-11-04')}catch(e){}")
    await pg.goto('file:///home/claude/proto/sling-spot-ar-prototype.html'); await pg.click('#bDemo'); await pg.wait_for_timeout(300)
    await pg.evaluate("(()=>{const sp={name:'仙台城',lat:38.2514,lon:140.8566,r:250,h:120};sp.d=2500;sp.b=247;S.sel=sp;S.pull=CFG.pullMax;launch();})()")
    await pg.wait_for_timeout(500); print('JP photo layer:',await pg.evaluate("map.getLayoutProperty('photo','visibility')"))
    await b.close()
asyncio.run(main())
