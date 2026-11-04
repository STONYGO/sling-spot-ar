import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page()
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    async def route(r):
      if r.request.url.startswith('file:'): return await r.continue_()
      await r.abort()   # 完全オフライン
    await pg.route('**/*',route)
    await pg.add_init_script("try{localStorage.setItem('coach.v1','1');localStorage.setItem('terms.agreed','2026-11-04')}catch(e){}")
    await pg.goto('file:///home/claude/proto/sling-spot-ar-prototype.html')
    r=await pg.evaluate("""async()=>{localStorage.setItem('area:ja',JSON.stringify({lat:38.26,lon:140.88,spots:[{name:'保存スポット',lat:38.27,lon:140.89,r:120,h:40}]}));
      localStorage.setItem('ex:ja:保存スポット',JSON.stringify({ex:'保存スポットは仙台の名所である。\\n\\n== 歴史 ==\\n昔からある。',url:'',thumb:''}));
      LANG.cur='ja'; S.pos={lat:38.2601,lon:140.8824,acc:10}; S.fetchCtr=null;S.fetching=0; await refreshSpots();
      const ex=await explain({name:'保存スポット',wl:'ja'}); return [S.spots.map(s=>s.name),S.debug.offline,ex.cards.map(c=>c.h)]}""")
    print(r,errs); await b.close()
asyncio.run(main())
