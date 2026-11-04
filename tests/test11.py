import asyncio, json, io
from PIL import Image
from playwright.async_api import async_playwright
def png(c):
    im=Image.new('RGB',(256,256),c); b=io.BytesIO(); im.save(b,'PNG'); return b.getvalue()
FT=png((128,10,0)); SAT=png((40,120,70))
INIT_BASE=r"""
try{localStorage.setItem('coach.v1','1');localStorage.setItem('terms.agreed','2026-11-04')}catch(e){}
setTimeout(()=>{ let h=90; setInterval(()=>{ const ev=new DeviceOrientationEvent('deviceorientation',{alpha:(360-h)%360,beta:88,gamma:0,absolute:false});
  Object.defineProperty(ev,'webkitCompassHeading',{value:h}); window.dispatchEvent(ev); },50); },800);
"""
async def run(scenario):
  async with async_playwright() as p:
    b=await p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
    ctx=await b.new_context(viewport={'width':820,'height':1180},has_touch=True,permissions=['geolocation','camera'],geolocation={'latitude':1.2834,'longitude':103.8607,'accuracy':12})
    pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    init=INIT_BASE
    if scenario=='hang_camera': init+="navigator.mediaDevices.getUserMedia=()=>new Promise(()=>{});"
    if scenario=='deny_motion': init+="DeviceOrientationEvent.requestPermission=()=>Promise.resolve('denied');"
    else: init+="DeviceOrientationEvent.requestPermission=()=>Promise.resolve('granted');"
    async def route(r):
      u=r.request.url; H={'access-control-allow-origin':'*'}
      if u.startswith('file:'): return await r.continue_()
      if 'terrarium' in u: return await r.fulfill(status=200,content_type='image/png',headers=H,body=FT)
      if 'arcgisonline' in u: return await r.fulfill(status=200,content_type='image/png',headers=H,body=SAT)
      if 'geosearch' in u: return await r.fulfill(status=200,content_type='application/json',headers=H,body=json.dumps({'query':{'geosearch':[{'title':'マリーナベイ・サンズ','lat':1.2834,'lon':103.8647}]}}))
      if 'wikidata' in u: return await r.fulfill(status=200,content_type='application/json',headers=H,body='{"results":{"bindings":[]}}')
      if 'overpass' in u: return await r.fulfill(status=200,content_type='application/json',headers=H,body='{"elements":[]}')
      if 'wikipedia' in u: return await r.fulfill(status=200,content_type='application/json',headers=H,body=json.dumps({'query':{'pages':{'1':{'extract':'マリーナベイ・サンズはシンガポールの統合型リゾートである。2010年に開業した。','fullurl':'x'}}}}))
      await r.abort()   # 地理院タイルは国外で失敗する想定
    await pg.route('**/*',route); await pg.add_init_script(init)
    await pg.goto('file:///home/claude/proto/sling-spot-ar-prototype.html'); await pg.wait_for_timeout(300)
    ver=await pg.evaluate("$('verTag').textContent")
    await pg.tap('#bStart'); await pg.wait_for_timeout(7000)
    o=await pg.evaluate("""({boot:[...document.querySelectorAll('#bootL div')].map(d=>d.textContent),bootShown:$('boot').style.display,camTap:$('camTap').style.display,
      camVis:$('cam').style.visibility,sky:$('sky').style.display,demo:S.demo,errbox:!!document.getElementById('errbox'),labels:(S.labels||[]).map(r=>r.c.s.name)})""")
    print('==',scenario,ver); [print(' ',k,v) for k,v in o.items()]
    if scenario=='normal':
      await pg.screenshot(path='r3_normal.png')
      r=await pg.evaluate("(()=>{const r=S.labels[0];return r?[(r.x0+r.x1)/2,(r.y0+r.y1)/2]:null})()")
      if r:
        await pg.mouse.move(*r); await pg.mouse.down(); await pg.wait_for_timeout(60)
        for i in range(12): await pg.mouse.move(r[0],r[1]+20+i*22); await pg.wait_for_timeout(12)
        await pg.mouse.up(); await pg.wait_for_timeout(9000)
        o2=await pg.evaluate("({state:S.state,photoVis:map.getLayoutProperty('photo','visibility'),mapErr:S.debug.mapErr||null,card:$('card').innerText.slice(0,40)})")
        print('  flight',o2); await pg.screenshot(path='r4_orbit_sg.png')
    if scenario=='hang_camera': await pg.screenshot(path='r5_hangcam.png')
    print('  pageerrors',errs); await b.close()
async def main():
  for sc in ['normal']: await run(sc)
asyncio.run(main())
