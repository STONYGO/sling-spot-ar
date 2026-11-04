// Sling Spot AR service worker v2
// アプリ本体: ネット優先（4秒で応答がなければ保存版）／地図・地形タイルと画像: 保存版優先／API: ネット優先＋保存版に退避
const APP='ssar-app-v2', TILE='ssar-tiles-v2', API='ssar-api-v2', KEEP=[APP,TILE,API];
self.addEventListener('install',e=>{ e.waitUntil(caches.open(APP).then(c=>c.addAll(['./','./index.html'])).catch(()=>{})); self.skipWaiting(); });
self.addEventListener('activate',e=>{ e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>!KEEP.includes(k)).map(k=>caches.delete(k)))).then(()=>self.clients.claim())); });
const timeout=(p,ms)=>Promise.race([p,new Promise((_,rj)=>setTimeout(()=>rj(new Error('timeout')),ms))]);
self.addEventListener('fetch',e=>{
  const req=e.request; if(req.method!=='GET')return; const u=new URL(req.url);
  if(u.origin===self.location.origin){
    e.respondWith(timeout(fetch(req),4000).then(r=>{ if(r.ok){ const c=r.clone(); caches.open(APP).then(x=>x.put(req,c)); } return r; })
      .catch(()=>caches.match(req).then(m=>m||caches.match('./index.html')).then(m=>m||fetch(req))));
    return;
  }
  if(/cyberjapandata\.gsi\.go\.jp|elevation-tiles-prod|upload\.wikimedia\.org|server\.arcgisonline\.com/.test(u.host+u.pathname)){
    e.respondWith(caches.open(TILE).then(async c=>{
      const m=await c.match(req);
      if(m&&!(m.type==='opaque'&&req.mode==='cors'))return m;          // CORS要求に不透明レスポンスは返さない
      const r=await fetch(req); if(r.ok||(r.type==='opaque'&&req.mode!=='cors'))c.put(req,r.clone()); return r; }));
    return;
  }
  if(/wikipedia\.org|wikidata\.org|overpass-api\.de/.test(u.host)){
    e.respondWith(fetch(req).then(r=>{ if(r.ok){ const c=r.clone(); caches.open(API).then(x=>x.put(req,c)); } return r; }).catch(()=>caches.match(req).then(m=>m||Response.error())));
  }
});
