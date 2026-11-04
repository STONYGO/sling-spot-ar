import asyncio, json, io, struct, math
from PIL import Image
from playwright.async_api import async_playwright
def jpeg_with_exif(lat,lon,direction,f35):
    # 手組みのEXIF(リトルエンディアン) : IFD0 -> ExifIFD(f35) / GPS IFD
    def rat(v,den=1000000): return struct.pack('<II',int(round(v*den)),den)
    entries0=[]; data=b''
    # レイアウト: header(8) IFD0 at 8
    ifd0_n=2; ifd0_size=2+ifd0_n*12+4; exif_off=8+ifd0_size; exif_n=1; exif_size=2+exif_n*12+4
    gps_off=exif_off+exif_size; gps_n=5; gps_size=2+gps_n*12+4; dat=gps_off+gps_size
    def dms(x): d=int(x); m=int((x-d)*60); s=(x-d-m/60)*3600; return [d,m,s]
    lat_d=dms(abs(lat)); lon_d=dms(abs(lon))
    blob=b''.join(rat(v) for v in lat_d)+b''.join(rat(v) for v in lon_d)+rat(direction)
    def ent(tag,typ,cnt,val): return struct.pack('<HHI',tag,typ,cnt)+val
    ifd0=struct.pack('<H',ifd0_n)+ent(0x8769,4,1,struct.pack('<I',exif_off))+ent(0x8825,4,1,struct.pack('<I',gps_off))+struct.pack('<I',0)
    exif=struct.pack('<H',exif_n)+ent(0xA405,3,1,struct.pack('<HH',f35,0))+struct.pack('<I',0)
    gps=struct.pack('<H',gps_n)+ent(1,2,2,b'N\0\0\0')+ent(2,5,3,struct.pack('<I',dat))+ent(3,2,2,b'E\0\0\0')+ent(4,5,3,struct.pack('<I',dat+24))+ent(17,5,1,struct.pack('<I',dat+48))+struct.pack('<I',0)
    tiff=b'II*\0'+struct.pack('<I',8)+ifd0+exif+gps+blob
    app1=b'Exif\0\0'+tiff
    im=Image.new('RGB',(1600,1200),(120,170,220)); bio=io.BytesIO(); im.save(bio,'JPEG'); j=bio.getvalue()
    return j[:2]+b'\xff\xe1'+struct.pack('>H',len(app1)+2)+app1+j[2:]
open('/home/claude/proto/test_photo.jpg','wb').write(jpeg_with_exif(38.2601,140.8824,310.0,26))
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':820,'height':1180})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    calls=[]
    async def route(r):
      u=r.request.url; H={'access-control-allow-origin':'*'}
      if u.startswith('file:'): return await r.continue_()
      calls.append(u.split('?')[0])
      if 'langlinks' in u: return await r.fulfill(status=200,content_type='application/json',headers=H,body=json.dumps({'query':{'pages':{'1':{'langlinks':[{'*':'Sendai Castle'}]}}}}))
      if 'en.wikipedia.org' in u and 'prop=extracts' in u: return await r.fulfill(status=200,content_type='application/json',headers=H,body=json.dumps({'query':{'pages':{'1':{'extract':'Sendai Castle is a castle in Sendai. It was built by Date Masamune.\n\n== History ==\nConstruction began in 1600. It was completed in 1602.\n','fullurl':'https://en.wikipedia.org/wiki/Sendai_Castle'}}}}))
      if 'wiki' in u or 'overpass' in u: return await r.fulfill(status=200,content_type='application/json',headers=H,body='{"query":{"geosearch":[]},"results":{"bindings":[]},"elements":[]}')
      await r.abort()
    await pg.route('**/*',route)
    await pg.add_init_script("try{localStorage.setItem('coach.v1','1');localStorage.setItem('terms.agreed','2026-11-04')}catch(e){}")
    await pg.goto('file:///home/claude/proto/sling-spot-ar-prototype.html')
    out={}
    out['exif']=await pg.evaluate("""async()=>{const r=await fetch('file:///home/claude/proto/test_photo.jpg').catch(()=>null);return null}""")
    # EXIF解析
    data=list(open('/home/claude/proto/test_photo.jpg','rb').read())
    out['exif']=await pg.evaluate("(a)=>{const e=__parseExif(new Uint8Array(a).buffer);return [e.lat&&e.lat.toFixed(4),e.lon&&e.lon.toFixed(4),e.dir,e.f35]}",data)
    # 英語化
    await pg.select_option('#langSel','en')
    out['btn']=await pg.evaluate("$('bStart').textContent")
    await pg.click('#bDemo'); await pg.wait_for_timeout(300)
    out['hint']=await pg.evaluate("$('hint').textContent")
    h=await pg.evaluate("__geo.bearing(38.2601,140.8824,38.2514,140.8566)"); await pg.evaluate(f"S.heading={h};S.pitch=0")
    await pg.mouse.move(410,700); await pg.mouse.down(); await pg.wait_for_timeout(450)
    for i in range(12): await pg.mouse.move(410,720+i*25); await pg.wait_for_timeout(12)
    await pg.mouse.up(); await pg.wait_for_timeout(5800)
    out['enCards']=await pg.evaluate("[S.cards.map(c=>c.h),S.cards[0]&&S.cards[0].t.slice(0,30)]")
    out['got']=await pg.evaluate("$('gotT1').textContent")
    await pg.click('#bBack'); await pg.wait_for_timeout(800)
    await pg.evaluate("applyLang('ja')")
    # 写真モード
    await pg.set_input_files('#fPhoto','/home/claude/proto/test_photo.jpg'); await pg.wait_for_timeout(1500)
    out['photo']=await pg.evaluate("[$('photoV').classList.contains('show'),PH.lat.toFixed(3),Math.round(PH.dir),PH.f35,(PH.placed||[]).map(r=>r.c.s.name)]")
    await pg.screenshot(path='s14_photo.png')
    await pg.click('#phClose')
    # 書き出し→読み込み(マージ)
    out['merge']=await pg.evaluate("""(()=>{const inc={items:{'泉ヶ岳':{id:'泉ヶ岳',no:1,name:'泉ヶ岳',lat:38.34,lon:140.75,kind:'mt',h:1172,genre:'mt',tags:['行った'],first:1,count:3}},tags:['行った'],days:{'2026-11-01':2}};
       const n=__dexMerge(inc); const d=__dex.dexLoad(); return [n,Object.keys(d.items),d.items['泉ヶ岳'].no]})()""")
    out['merge2']=await pg.evaluate("__dexMerge({items:{'泉ヶ岳':{id:'泉ヶ岳',count:5,tags:['絶景'],first:1}}})+':'+__dex.dexLoad().items['泉ヶ岳'].count+':'+__dex.dexLoad().items['泉ヶ岳'].tags")
    # オフライン退避: 保存済みエリアから復元
    out['offline']=await pg.evaluate("""async()=>{localStorage.setItem('area:ja',JSON.stringify({lat:38.26,lon:140.88,spots:[{name:'保存スポット',lat:38.27,lon:140.89,r:120,h:40}]}));
       S.pos={lat:38.2601,lon:140.8824,acc:10}; S.fetchCtr=null;S.fetching=0; await page_refresh(); return 0}""".replace("await page_refresh();","")) 
    print('calls sample', sorted(set(c for c in calls))[:6])
    for k,v in out.items(): print(k,v)
    print('errs',errs); await b.close()
asyncio.run(main())
