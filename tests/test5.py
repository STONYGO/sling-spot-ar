import asyncio, json, math
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':820,'height':1180})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    async def route(r):
      u=r.request.url
      if u.startswith('file:'): return await r.continue_()
      H={'access-control-allow-origin':'*'}
      if 'wikipedia' in u or 'wikidata' in u or 'overpass' in u:
        return await r.fulfill(status=200,content_type='application/json',headers=H,body='{"query":{"geosearch":[]},"results":{"bindings":[]},"elements":[]}')
      await r.abort()
    await pg.route('**/*',route)
    await pg.add_init_script("try{localStorage.setItem('coach.v1','1');localStorage.setItem('terms.agreed','2026-11-04')}catch(e){}"); await pg.goto('file:///home/claude/proto/sling-spot-ar-prototype.html'); await pg.click('#bDemo'); await pg.wait_for_timeout(200)
    out=await pg.evaluate("""async()=>{
      S.demo=false; S.sensor=true; S.gotAbs=true; S.hAbsRaw=170; S.sensorOff=0; S.pitch=0;
      // ジャイロ座標系: 縦持ち・カメラが gyro方位10°を向く
      const a=10*Math.PI/180; S.hGyro=10; S.Mg={X:[Math.cos(a),-Math.sin(a),0],Y:[0,0,1],Z:[-Math.sin(a),-Math.cos(a),0]};
      S.M=S.Mg; S.forceAngle=0;
      const t=Date.now()-12000, r=[];
      // 東へ25m/s(90km/h)で走行
      for(let i=0;i<=12;i++){ __onFix({latitude:38.26,longitude:140.88+i*25/(111320*Math.cos(38.26*Math.PI/180)),accuracy:15,altitude:null,speed:25,heading:90},t+i*1000); }
      r.push(['moving',S.moving,'side',S.side,'C',Math.round(S.trainC),'heading',Math.round(S.heading)]);
      // 端末を右へ20°回す（ジャイロ）
      S.hGyro=30; updHeading(); r.push(['turned',Math.round(S.heading)]);
      const ray=rayAt(innerWidth/2,innerHeight/2); r.push(['rayAz',Math.round(ray.az)]);
      // 位置の遅れ補正: 2秒前のfixで50m前進
      S.pos.ts=Date.now()-2000; const P=posNow(); r.push(['extrap_m',Math.round(__geo.dist(S.pos.lat,S.pos.lon,P.lat,P.lon))]);
      // 真南(右窓)のスポットを狙う
      S.hGyro=10; updHeading(); S.visReady=false;
      const P2=posNow(); S.spots=[{name:'南の寺',lat:P2.lat-2000/111320,lon:P2.lon,r:120,h:30},{name:'北の山',lat:P2.lat+2000/111320,lon:P2.lon,r:120,h:30}];
      const rs=resolve(innerWidth/2,innerHeight/2); r.push(['pick',rs.list.map(c=>c.name)]);
      // 停車→20秒で自動終了
      const t2=Date.now(); for(let i=0;i<=22;i++)__onFix({latitude:38.26,longitude:140.89,accuracy:15,speed:0,heading:null},t2+i*1000);
      r.push(['stopped',S.moving]);
      return r;}""")
    for x in out: print(x)
    print('errs',errs); await b.close()
asyncio.run(main())
