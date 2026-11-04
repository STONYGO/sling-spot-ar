import asyncio, json, math, io
from PIL import Image
from playwright.async_api import async_playwright
LAT0,LON0=38.2601,140.8824
def elev(lat,lon):
    e=50.0
    # 西10km付近に南北の尾根(標高900m)
    dx=(lon-LON0)*111320*math.cos(LAT0*math.pi/180)
    if -10600<dx<-9400: e=900.0
    return e
def tile(z,x,y):
    n=2**z; im=Image.new('RGB',(256,256)); px=im.load()
    for j in range(0,256):
        latr=math.atan(math.sinh(math.pi*(1-2*(y+(j+.5)/256)/n))); lat=latr*180/math.pi
        for i in range(0,256):
            lon=(x+(i+.5)/256)/n*360-180; v=elev(lat,lon)+32768
            r=int(v//256); g=int(v%256); b=int((v-int(v))*256); px[i,j]=(r,g,b)
    bio=io.BytesIO(); im.save(bio,'PNG'); return bio.getvalue()
cache={}
k=111320*math.cos(LAT0*math.pi/180)
def ll(dx,dy): return {'lat':LAT0+dy/111320,'lon':LON0+dx/k}
# 東200mに高さ30mの建物（東500mの寺を遮る）／自分を囲む建物（屋内判定用）は別テスト
bldg=[ll(180,-40),ll(220,-40),ll(220,40),ll(180,40),ll(180,-40)]
home=[ll(-15,-15),ll(15,-15),ll(15,15),ll(-15,15),ll(-15,-15)]
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':820,'height':1180})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    state={'inside':False}
    async def route(r):
      u=r.request.url
      if u.startswith('file:'): return await r.continue_()
      H={'access-control-allow-origin':'*'}
      if 'terrarium' in u:
        z,x,y=[int(v) for v in u.split('terrarium/')[1].replace('.png','').split('/')]
        key=(z,x,y)
        if key not in cache: cache[key]=tile(z,x,y)
        return await r.fulfill(status=200,content_type='image/png',headers=H,body=cache[key])
      if 'overpass' in u:
        els=[{'type':'way','geometry':bldg,'tags':{'building':'yes','height':'30','name':'テストビル'}}]
        if state['inside']: els.append({'type':'way','geometry':home,'tags':{'building':'hotel','name':'ホテル'}})
        return await r.fulfill(status=200,content_type='application/json',headers=H,body=json.dumps({'elements':els}))
      if 'wikipedia' in u or 'wikidata' in u:
        return await r.fulfill(status=200,content_type='application/json',headers=H,body='{"query":{"geosearch":[]},"results":{"bindings":[]}}')
      await r.abort()
    await pg.route('**/*',route)
    await pg.add_init_script("try{localStorage.setItem('coach.v1','1');localStorage.setItem('terms.agreed','2026-11-04')}catch(e){}"); await pg.goto('file:///home/claude/proto/sling-spot-ar-prototype.html'); await pg.click('#bDemo'); await pg.wait_for_timeout(300)
    spots=[
      dict(name='見える山',**ll(0,20000),h=1000,r=1500,kind='mt'),
      dict(name='隠れ山',**ll(-30000,0),h=600,r=1500,kind='mt'),
      dict(name='高い山',**ll(-30000,3000),h=2500,r=1500,kind='mt'),
      dict(name='隠れ寺',**ll(500,0),h=20,r=60),
      dict(name='見える塔',**ll(0,-500),h=20,r=60),
    ]
    async def run(inside):
      state['inside']=inside
      return await pg.evaluate("""async(sp)=>{S.demo=false;S.pos={lat:%f,lon:%f,acc:10};S.spots=sp;S.visReady=false;
        await loadEnv(); computeVis(); return {vis:S.spots.map(s=>s.name+':'+(s.vis?'○':'×'+s.block)),dbg:S.debug.vis,env:S.debug.env,warn:envWarn()}}"""%(LAT0,LON0),spots)
    r1=await run(False); print(r1)
    # 遮られた方向を狙うと理由付きで弾かれる
    h=await pg.evaluate("__geo.bearing(%f,%f,%f,%f)"%(LAT0,LON0,ll(500,0)['lat'],ll(500,0)['lon']))
    res=await pg.evaluate(f"(()=>{{S.heading={h};S.pitch=2;const r=resolve(innerWidth/2,innerHeight/2);return [r.list.map(c=>c.name),r.hidden]}})()")
    print('aim east:',res)
    # 目線を100mにすると寺が見える
    await pg.evaluate("S.eyeH=100;computeVis()"); print('eye100:',await pg.evaluate("S.spots.map(s=>s.name+':'+(s.vis?'○':'×'))"))
    await pg.evaluate("S.eyeH=1.5")
    r2=await run(True); print('inside:',r2['dbg'],r2['warn'])
    await pg.evaluate("S.pos.acc=120"); print('lowacc:',await pg.evaluate("envWarn()"))
    print('errs',errs); await b.close()
asyncio.run(main())
