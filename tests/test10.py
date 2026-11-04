import asyncio, json, io, math
from PIL import Image
from playwright.async_api import async_playwright
def flat_tile():
    im=Image.new('RGB',(256,256),(128,10,0)); b=io.BytesIO(); im.save(b,'PNG'); return b.getvalue()  # 標高 ~10m
FT=flat_tile()
INIT=r"""
try{localStorage.removeItem('coach.v1');localStorage.setItem('terms.agreed','2026-11-04')}catch(e){}
window.__errs=[]; addEventListener('error',e=>__errs.push(String(e.message)+' @'+e.lineno)); addEventListener('unhandledrejection',e=>__errs.push('UR:'+String(e.reason&&e.reason.message||e.reason)));
// iOS風: 方位センサーは許可が必要・webkitCompassHeading付き
DeviceOrientationEvent.requestPermission=()=>Promise.resolve('granted');
setTimeout(()=>{ let h=0; setInterval(()=>{ const ev=new DeviceOrientationEvent('deviceorientation',{alpha:(360-h)%360,beta:88,gamma:0,absolute:false});
  Object.defineProperty(ev,'webkitCompassHeading',{value:h}); Object.defineProperty(ev,'webkitCompassAccuracy',{value:10}); window.dispatchEvent(ev); },50); },1500);
"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
    ctx=await b.new_context(viewport={'width':820,'height':1180},has_touch=True,permissions=['geolocation','camera'],geolocation={'latitude':1.2834,'longitude':103.8607,'accuracy':12},
       user_agent='Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0 Mobile/15E148 Safari/604.1')
    pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); cons=[]
    pg.on('console',lambda m: cons.append(m.text) if m.type=='error' else None)
    async def route(r):
      u=r.request.url; H={'access-control-allow-origin':'*'}
      if u.startswith('file:'): return await r.continue_()
      if 'terrarium' in u: return await r.fulfill(status=200,content_type='image/png',headers=H,body=FT)
      if 'geosearch' in u: return await r.fulfill(status=200,content_type='application/json',headers=H,body=json.dumps({'query':{'geosearch':[{'title':'マリーナベイ・サンズ','lat':1.2834,'lon':103.8607+0.004},{'title':'シンガポール・フライヤー','lat':1.2893,'lon':103.8631},{'title':'マーライオン','lat':1.2868,'lon':103.8545}]}}))
      if 'wikidata' in u: return await r.fulfill(status=200,content_type='application/json',headers=H,body='{"results":{"bindings":[]}}')
      if 'overpass' in u: return await r.fulfill(status=200,content_type='application/json',headers=H,body='{"elements":[]}')
      if 'wikipedia' in u: return await r.fulfill(status=200,content_type='application/json',headers=H,body=json.dumps({'query':{'pages':{'1':{'extract':'テスト。','fullurl':'x'}}}}))
      await r.abort()
    await pg.route('**/*',route); await pg.add_init_script(INIT)
    await pg.goto('file:///home/claude/proto/sling-spot-ar-prototype.html'); await pg.wait_for_timeout(500)
    await pg.screenshot(path='r0_intro.png')
    await pg.tap('#bStart'); await pg.wait_for_timeout(1200); await pg.screenshot(path='r1_after_start.png')
    st=await pg.evaluate("({coach:$('coach').classList.contains('show')})"); print('coach',st)
    if st['coach']: await pg.tap('#coachOk')
    await pg.wait_for_timeout(4000); await pg.screenshot(path='r2_running.png')
    info=await pg.evaluate("""({state:S.state,demo:S.demo,sensor:S.sensor,heading:Math.round(S.heading),pos:S.pos&&[S.pos.lat,S.pos.lon,S.pos.acc],spots:S.spots.length,vis:S.debug.vis,env:S.debug.env,
       cam:[$('cam').videoWidth,$('cam').videoHeight,$('cam').style.display,$('sky').style.display],labels:(S.labels||[]).map(r=>r.c.s.name),hud:$('hud').textContent,warn:$('warn').textContent,errs:__errs})""")
    for k,v in info.items(): print(k,v)
    print('pageerrors',errs); print('console errors',cons[:5])
    await b.close()
asyncio.run(main())
