// Sling Spot AR service worker: アプリ本体はネット優先、地図・地形タイルと画像はキャッシュ優先、APIはネット優先＋キャッシュ退避
const APP='ssar-app-v1', TILE='ssar-tiles-v1', API='ssar-api-v1';
self.addEventListener('install',e=>{ e.waitUntil(caches.open(APP).then(c=>c.addAll(['./','./index.html']))); self.skipWaiting(); });
self.addEventListener('activate',e=>{ e.waitUntil(self.clients.claim()); });
self.addEventListener('fetch',e=>{
  const req=e.request; if(req.method!=='GET')return; const u=new URL(req.url);
  if(u.origin===self.location.origin){
    e.respondWith(fetch(req).then(r=>{ const c=r.clone(); caches.open(APP).then(x=>x.put(req,c)); return r; }).catch(()=>caches.match(req).then(m=>m||caches.match('./index.html'))));
    return;
  }
  if(/cyberjapandata\.gsi\.go\.jp|elevation-tiles-prod|upload\.wikimedia\.org/.test(u.host+u.pathname)){
    e.respondWith(caches.open(TILE).then(async c=>{ const m=await c.match(req); if(m)return m; const r=await fetch(req); if(r.ok||r.type==='opaque')c.put(req,r.clone()); return r; }));
    return;
  }
  if(/wikipedia\.org|wikidata\.org|overpass-api\.de/.test(u.host)){
    e.respondWith(fetch(req).then(r=>{ if(r.ok){ const c=r.clone(); caches.open(API).then(x=>x.put(req,c)); } return r; }).catch(()=>caches.match(req)));
  }
});
