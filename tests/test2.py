import asyncio, json
from playwright.async_api import async_playwright
EXT="仙台城は、宮城県仙台市青葉区にあった日本の城。別名は青葉城。\n\n== 歴史 ==\n1600年、伊達政宗が築城を開始した。1602年に完成した。\n\n== 構造 ==\n本丸は青葉山に築かれた山城である。石垣が現存する。\n\n== アクセス ==\n仙台駅からバスで約20分。るーぷる仙台が便利。\n"
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    pg=await b.new_page(viewport={'width':1024,'height':768})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    async def route(r):
      u=r.request.url
      if 'prop=extracts' in u:
        await r.fulfill(status=200,content_type='application/json',headers={'access-control-allow-origin':'*'},body=json.dumps({'query':{'pages':{'1':{'extract':EXT,'fullurl':'https://ja.wikipedia.org/wiki/x'}}}}))
      elif 'geosearch' in u:
        await r.fulfill(status=200,content_type='application/json',headers={'access-control-allow-origin':'*'},body='{"query":{"geosearch":[{"title":"青葉山","lat":38.2530,"lon":140.8560}]}}')
      elif 'wikidata' in u:
        await r.fulfill(status=200,content_type='application/json',headers={'access-control-allow-origin':'*'},body=json.dumps({'results':{'bindings':[{'itemLabel':{'value':'船形山'},'title':{'value':'船形山'},'lat':{'value':'38.4547'},'lon':{'value':'140.6267'},'elev':{'value':'1500'}}]}}))
      elif u.startswith('file:'): await r.continue_()
      else: await r.abort()
    await pg.route('**/*',route)
    await pg.add_init_script("try{localStorage.setItem('coach.v1','1');localStorage.setItem('terms.agreed','2026-11-04')}catch(e){}"); await pg.goto('file:///home/claude/proto/sling-spot-ar-prototype.html')
    await pg.click('#bDemo'); await pg.wait_for_timeout(300)
    out={}
    out['fetch']=await pg.evaluate("S.debug.fetch")
    out['nSpots']=await pg.evaluate("S.spots.length")
    # 1) 回転行列: 縦持ち・正面北(alpha=0,beta=90) → 中央タップの方位0
    #    横持ち(θ=90): 端末上辺が西、画面が南向き → X=上, Y=西, Z=南
    out['ray']=await pg.evaluate("""(()=>{S.demo=false;S.sensorOff=0;S.userOff=0;
      const W=innerWidth,H=innerHeight,r=[];
      S.forceAngle=0; S.M={X:[1,0,0],Y:[0,0,1],Z:[0,-1,0]}; r.push(rayAt(W/2,H/2), rayAt(W/2+200,H/2), rayAt(W/2,H/2-200));
      S.forceAngle=90; S.M={X:[0,0,1],Y:[-1,0,0],Z:[0,-1,0]}; r.push(rayAt(W/2,H/2), rayAt(W/2+200,H/2), rayAt(W/2,H/2-200));
      S.demo=true; S.M=null; return r.map(o=>[Math.round(o.az),Math.round(o.el)]);})()""")
    # 2) 実際のイベントからの方位(縦持ち, alpha=270 → 方位90=東)
    out['event']=await pg.evaluate("""(()=>{S.demo=false;S.forceAngle=0;onOri(new DeviceOrientationEvent('deviceorientationabsolute',{alpha:270,beta:90,gamma:0,absolute:true}));const h=Math.round(S.heading),pt=Math.round(S.pitch);S.demo=true;S.M=null;return [h,pt];})()""")
    # 3) 解説の章立て
    out['cards']=await pg.evaluate("__buildCards(%s).map(c=>c.h)"%json.dumps(EXT))
    # 4) 候補選択フロー: 仙台城と青葉山がほぼ同方向
    h=await pg.evaluate("__geo.bearing(38.2601,140.8824,38.2514,140.8566)")
    await pg.evaluate(f"S.heading={h}")
    await pg.mouse.move(512,384); await pg.mouse.down(); await pg.wait_for_timeout(450)
    out['cand']=await pg.evaluate("S.cand.map(c=>c.name)")
    await pg.mouse.move(512,410); await pg.mouse.up(); await pg.wait_for_timeout(100)
    out['afterShort']=await pg.evaluate("S.state")
    await pg.screenshot(path='s3_choose.png')
    await pg.click('#chips button[data-i="1"]'); out['picked']=await pg.evaluate("[S.state,S.sel.name]")
    await pg.mouse.move(500,300); await pg.mouse.down(); await pg.wait_for_timeout(50)
    for y in range(310,560,25): await pg.mouse.move(500,y); await pg.wait_for_timeout(15)
    await pg.mouse.up(); await pg.wait_for_timeout(5500)
    out['orbit']=await pg.evaluate("[S.state,S.cards.map(c=>c.h)]")
    await pg.screenshot(path='s4_orbit_land.png')
    await pg.click('#bBack')
    # 5) 遠方の山(船形山)が狙える
    h2=await pg.evaluate("__geo.bearing(38.2601,140.8824,38.4547,140.6267)")
    await pg.evaluate(f"S.heading={h2};S.pitch=2")
    await pg.mouse.move(512,384); await pg.mouse.down(); await pg.wait_for_timeout(450)
    out['mt']=await pg.evaluate("S.sel&&[S.sel.name,Math.round(S.sel.d)]"); await pg.mouse.up()
    out['errs']=errs
    for k,v in out.items(): print(k,v)
    await b.close()
asyncio.run(main())
