// ---------- 著作権・規約・バージョン情報 ----------
const APP={name:'Sling Spot AR（仮称）',ver:'1.0-beta',build:'__BUILD__',termsVer:'2026-11-04',copy:'© 2026 STONY & Co. All Rights Reserved.'};
const CO={ja:'STONY株式会社（STONY & Co.）',rep:'代表取締役 石北 直之',addr:'〒377-0008 群馬県渋川市渋川3910-9-3F',mail:'info@stony.jp'};
const CHANGELOG=[
 ['1.0-beta','2026-11-04',{ja:'著作権表示、利用規約、プライバシーポリシー（外部送信先の一覧を含む）、ライセンス・出典表示、バージョン情報と更新履歴を追加。初回起動時に規約への同意を確認。',en:'Added copyright notice, Terms of Use, Privacy Policy (with a list of external data recipients), licenses & attributions, and version info / changelog. Consent to the terms is requested on first launch.'}],
 ['0.9','2026-11-04',{ja:'日本国外で飛行先が真っ暗になる不具合を修正（世界の航空写真と空の表示）。起動手順を安定化（センサー許可を最優先、カメラの待ちすぎ防止、位置情報の並行取得）。起動チェックとエラーの画面表示、リセット機能を追加。',en:'Fixed the black screen after flying outside Japan (world imagery and sky). More robust startup (motion permission first, camera timeout, parallel GPS). Added startup checklist, on-screen error reports and a reset button.'}],
 ['0.8','2026-11-04',{ja:'多言語対応（日本語・英語・中国語〔繁体〕・韓国語）、写真から名前を特定する機能、図鑑の書き出し・読み込み、周辺のオフライン保存。',en:'Multilingual (Japanese, English, Chinese [Traditional], Korean), identify places in your photos, export/import of the collection, offline area save.'}],
 ['0.7','2026-11-04',{ja:'見えるスポットの名前を景色に常時表示（タップで照準）、ドラッグでの方位合わせ、車窓の自動案内、初回ガイド、共有、連続日数と実績バッジ。',en:'Always-on AR name labels (tap to aim), drag-to-align compass, train-window announcements, first-run guide, sharing, streaks and badges.'}],
 ['0.6','2026-11-04',{ja:'車窓モード（移動中はGPSの進行方向とジャイロで方位を推定）、スポット図鑑（自動登録・ジャンル分類・タグ・本を開くアニメーション）。',en:'Train-window mode (heading from GPS course + gyro while moving) and the Spot Collection (auto-record, genres, tags, book animation).'}],
 ['0.5','2026-11-03',{ja:'見通し判定（地形と建物に遮られたスポットを除外）、目線の高さ設定、屋内・低精度の警告。',en:'Line-of-sight check (hides spots blocked by terrain/buildings), eye-height setting, indoor/low-accuracy warnings.'}],
 ['0.4','2026-11-03',{ja:'効果音と音声解説を追加。スリングのY字を削除。',en:'Added sound effects and voice narration. Removed the Y-shaped fork.'}],
 ['0.3','2026-11-03',{ja:'パチンコ風の操作（全方向に引ける・軌道の予告・発射演出）。画面の端でも最大まで引けるように。',en:'Slingshot controls (pull in any direction, trajectory preview, launch effect); full power even near the screen edge.'}],
 ['0.2','2026-11-03',{ja:'iPadの横持ち、iOSの方位、遠くの山、解説の章立て、候補の選び直しによる方位補正。Webで公開。',en:'iPad landscape, iOS compass, distant mountains, sectioned guides, compass correction by picking candidates. Published on the web.'}],
 ['0.1','2026-11-03',{ja:'初版プロトタイプ（長押しで照準→引いて発射→飛行→360°周回しながら解説）。',en:'First prototype (long-press to aim → pull and release → fly → 360° orbit with a guide).'}]
];
function lg(){ return LANG.cur==='ja'?'ja':'en'; }
const DOCS={
 terms:{ja:()=>`<h3>利用規約</h3><p class="dd">制定日：2026年11月4日</p>
<p>この利用規約（以下「本規約」）は、${CO.ja}（以下「当社」）が提供する「${APP.name}」（以下「本サービス」）の利用条件を定めるものです。利用者は、本規約に同意のうえ本サービスを利用するものとします。</p>
<h4>第1条（本サービスの内容）</h4><p>本サービスは、端末のカメラ・位置情報・方位センサー等を用いて周辺のスポットを表示し、公開情報に基づく解説を提供する試験提供版（プロトタイプ）です。当社は、予告なく内容の変更・追加・停止を行うことがあります。</p>
<h4>第2条（安全な利用）</h4><p>利用者は、次の事項を守るものとします。<br>(1) 歩行中、自転車・自動車等の運転中に操作しないこと。車窓モードは乗客として利用すること。<br>(2) 駅のホーム、道路、崖、立入禁止区域、私有地等で危険な行為をしないこと。<br>(3) 周囲の人のプライバシーと施設のルールを尊重し、撮影が禁止された場所でカメラを使用しないこと。</p>
<h4>第3条（情報の正確性）</h4><p>本サービスが表示する名称・距離・標高・見通し・解説等は、Wikipedia等の第三者の情報と、端末による位置・方位の推定に基づく参考情報です。当社はその正確性・完全性・最新性を保証しません。防災・避難、登山の安全、医療、交通等の判断には使用しないでください。</p>
<h4>第4条（知的財産権）</h4><p>本サービスのプログラム、画面デザイン、名称、文章等に関する著作権その他の知的財産権は、当社または正当な権利者に帰属します。地図・地形・解説文等の第三者のコンテンツは、各提供元のライセンスに従います（「ライセンス・出典」を参照）。</p>
<h4>第5条（禁止事項）</h4><p>(1) 法令または公序良俗に反する行為<br>(2) 本サービスのプログラムの全部または一部を、当社の許諾なく複製・改変・再配布・販売・公開する行為<br>(3) 本サービスまたは外部サービスに過度な負荷をかける行為、自動化された大量アクセス<br>(4) 第三者の権利または利益を侵害する行為<br>(5) 当社の許諾のない営利目的での利用<br>(6) その他、当社が不適切と判断する行為</p>
<h4>第6条（外部サービス）</h4><p>本サービスは、Wikipedia、Wikidata、OpenStreetMap（Overpass API）、国土地理院、Esri、Amazon Web Services等の外部サービスを利用しています。外部サービスの停止・変更等により、本サービスの全部または一部を利用できない場合があります。</p>
<h4>第7条（免責）</h4><p>当社は、本サービスに事実上または法律上の瑕疵がないことを保証しません。当社は、本サービスの利用により利用者に生じた損害について、当社の故意または重大な過失による場合を除き、責任を負いません。法令により当社が責任を負う場合でも、当社の故意または重大な過失による場合を除き、その範囲は通常生ずべき直接の損害に限られます。</p>
<h4>第8条（本サービスの変更・終了）</h4><p>当社は、利用者への事前の通知なく、本サービスの内容を変更し、または提供を終了できるものとします。</p>
<h4>第9条（本規約の変更）</h4><p>当社は、必要に応じて本規約を変更できます。変更後の本規約は、本サービス内に掲示した時点から効力を生じます。重要な変更の場合は、本サービス内で改めて同意を求めます。</p>
<h4>第10条（準拠法・管轄）</h4><p>本規約は日本法に準拠します。本サービスに関して紛争が生じた場合は、前橋地方裁判所を第一審の専属的合意管轄裁判所とします。</p>
<h4>第11条（お問い合わせ）</h4><p>${CO.ja}<br>${CO.mail}</p>`,
  en:()=>`<h3>Terms of Use</h3><p class="dd">Effective: November 4, 2026</p>
<p>These Terms govern your use of "${APP.name}" (the "Service") provided by STONY & Co. (STONY株式会社, "we"). By using the Service you agree to these Terms. If these Terms are translated, the Japanese version prevails.</p>
<h4>1. The Service</h4><p>The Service uses your device's camera, location and motion sensors to show nearby places and provides guides based on public information. It is a prototype offered on a trial basis and may be changed or suspended without notice.</p>
<h4>2. Safe use</h4><p>(1) Do not operate the Service while walking, cycling or driving; use train-window mode only as a passenger. (2) Do not act dangerously on platforms, roads, cliffs, restricted areas or private property. (3) Respect other people's privacy and local rules; do not use the camera where photography is prohibited.</p>
<h4>3. Accuracy</h4><p>Names, distances, elevations, visibility and guides are reference information based on third-party sources such as Wikipedia and on your device's position/heading estimates. We do not guarantee their accuracy, completeness or timeliness. Do not rely on them for disaster response, mountain safety, medical or traffic decisions.</p>
<h4>4. Intellectual property</h4><p>Copyright and other rights in the Service's software, design, name and text belong to us or the rightful owners. Third-party content (maps, terrain, guide texts) is subject to its own license (see Licenses & Credits).</p>
<h4>5. Prohibited conduct</h4><p>(1) Illegal or immoral acts; (2) copying, modifying, redistributing, selling or publishing the Service's software in whole or in part without our permission; (3) placing excessive load on the Service or external services, including automated bulk access; (4) infringing others' rights; (5) commercial use without our permission; (6) other acts we deem inappropriate.</p>
<h4>6. External services</h4><p>The Service relies on Wikipedia, Wikidata, OpenStreetMap (Overpass API), the Geospatial Information Authority of Japan, Esri, Amazon Web Services and others. Parts of the Service may be unavailable if they change or stop.</p>
<h4>7. Disclaimer</h4><p>The Service is provided "as is". Except in cases of our willful misconduct or gross negligence, we are not liable for damages arising from your use of the Service; where liability is required by law, it is limited to ordinary and direct damages.</p>
<h4>8. Changes and termination</h4><p>We may change or terminate the Service without prior notice.</p>
<h4>9. Changes to these Terms</h4><p>We may amend these Terms. Amendments take effect when posted in the Service; for material changes we will ask for your consent again.</p>
<h4>10. Governing law and jurisdiction</h4><p>These Terms are governed by the laws of Japan. The Maebashi District Court shall have exclusive jurisdiction of first instance.</p>
<h4>11. Contact</h4><p>STONY & Co. — ${CO.mail}</p>`},
 privacy:{ja:()=>`<h3>プライバシーポリシー</h3><p class="dd">制定日：2026年11月4日</p>
<p>${CO.ja}（以下「当社」）は、「${APP.name}」（以下「本サービス」）における利用者情報の取扱いを、次のとおり定めます。</p>
<h4>1. 端末内で処理する情報</h4><p>当社は本サービスのためのサーバーを運用しておらず、次の情報を当社が受け取ることはありません。これらは利用者の端末内で処理されます。</p>
<ul><li><b>位置情報</b>：周辺スポットの検索、距離の計算、見通しの判定に使用します。</li><li><b>カメラ映像</b>：画面への表示のみに使用し、送信・保存しません。</li><li><b>端末の向き（方位・傾き）</b>：照準の計算に使用します。</li><li><b>選択した写真</b>：撮影位置・撮影方向（EXIF）を端末内で読み取り、名前の表示に使用します。写真そのものは送信しません。</li><li><b>図鑑の記録・タグ・設定・オフライン保存データ</b>：端末のブラウザ内（ローカルストレージ・キャッシュ）に保存します。</li></ul>
<h4>2. 外部への送信</h4><p>本サービスは機能の提供のため、利用者の端末から次の事業者へ直接通信します。通信に伴い、IPアドレス、ブラウザの種類、要求するURL（緯度経度を含む場合があります）等が各事業者に送られます。各事業者での取扱いは、それぞれのプライバシーポリシーに従います。</p>
<table class="dt"><tr><th>送信先</th><th>送信される主な情報</th><th>目的</th></tr>
<tr><td>Wikimedia Foundation（Wikipedia／Wikidata・米国）</td><td>現在地または写真の撮影地の緯度経度、スポット名</td><td>周辺スポットの検索、解説文・写真の取得</td></tr>
<tr><td>Overpass API（overpass-api.de・ドイツ）</td><td>緯度経度</td><td>周辺の建物データ（OpenStreetMap）の取得</td></tr>
<tr><td>国土地理院（日本）／Esri（米国）</td><td>表示する地図の範囲（タイル座標）</td><td>航空写真の表示</td></tr>
<tr><td>Amazon Web Services（米国）</td><td>表示・計算する範囲（タイル座標）</td><td>地形データの取得</td></tr>
<tr><td>GitHub（米国）</td><td>アクセス情報</td><td>本サービスの配信</td></tr></table>
<h4>3. 第三者への提供</h4><p>当社は、上記2の通信を除き、利用者の情報を第三者に提供しません。</p>
<h4>4. アクセス解析・広告</h4><p>本サービスは、アクセス解析ツール、広告、Cookieによる追跡を使用していません。</p>
<h4>5. 端末内データの削除</h4><p>ブラウザの「Webサイトデータの削除」で、図鑑を含む端末内のデータをすべて削除できます。図鑑を残したい場合は、事前に設定の「書き出し」で保存してください。</p>
<h4>6. 未成年の方の利用</h4><p>未成年の方は、保護者の同意を得たうえで利用してください。</p>
<h4>7. 改定</h4><p>本ポリシーを改定する場合は、本サービス内でお知らせします。</p>
<h4>8. お問い合わせ窓口</h4><p>${CO.ja}<br>${CO.rep}<br>${CO.addr}<br>${CO.mail}</p>`,
  en:()=>`<h3>Privacy Policy</h3><p class="dd">Effective: November 4, 2026</p>
<p>This policy explains how STONY & Co. (STONY株式会社, "we") handles information in "${APP.name}" (the "Service"). If translated, the Japanese version prevails.</p>
<h4>1. Information processed on your device</h4><p>We do not operate servers for the Service and do not receive the following information; it is processed only on your device.</p>
<ul><li><b>Location</b>: to search nearby places, compute distances and check visibility.</li><li><b>Camera image</b>: shown on screen only; never sent or stored.</li><li><b>Device orientation</b>: to compute where you aim.</li><li><b>Photos you select</b>: location/direction (EXIF) are read on the device; the photo itself is never sent.</li><li><b>Collection records, tags, settings, offline data</b>: stored in your browser (local storage/cache).</li></ul>
<h4>2. External transmission</h4><p>To provide its features, your device communicates directly with the providers below. Your IP address, browser type and the requested URL (which may include latitude/longitude) are sent to them. Each provider's privacy policy applies.</p>
<table class="dt"><tr><th>Recipient</th><th>Main data</th><th>Purpose</th></tr>
<tr><td>Wikimedia Foundation (Wikipedia/Wikidata, USA)</td><td>Latitude/longitude of you or your photo; place names</td><td>Nearby search; guide texts and images</td></tr>
<tr><td>Overpass API (overpass-api.de, Germany)</td><td>Latitude/longitude</td><td>Building data (OpenStreetMap)</td></tr>
<tr><td>GSI Japan / Esri (USA)</td><td>Map area (tile coordinates)</td><td>Aerial imagery</td></tr>
<tr><td>Amazon Web Services (USA)</td><td>Map area (tile coordinates)</td><td>Terrain data</td></tr>
<tr><td>GitHub (USA)</td><td>Access information</td><td>Delivering the Service</td></tr></table>
<h4>3. Third parties</h4><p>Except for the communications above, we do not provide your information to third parties.</p>
<h4>4. Analytics and ads</h4><p>The Service uses no analytics, advertising or tracking cookies.</p>
<h4>5. Deleting on-device data</h4><p>Clear website data in your browser to delete all on-device data, including your collection. Export your collection in Settings first if you want to keep it.</p>
<h4>6. Minors</h4><p>Minors should use the Service with a guardian's consent.</p>
<h4>7. Changes</h4><p>We will announce changes in the Service.</p>
<h4>8. Contact</h4><p>STONY & Co. (STONY株式会社)<br>Representative Director: Naoyuki Ishikita<br>3910-9-3F Shibukawa, Shibukawa-shi, Gunma 377-0008, Japan<br>${CO.mail}</p>`},
 lic:{ja:()=>licHTML('ja'),en:()=>licHTML('en')}
};
function licHTML(l){
  const J=l==='ja', rows=[
   [J?'解説文・写真':'Guide texts & images','Wikipedia — CC BY-SA 4.0',J?'各記事の執筆者による。本サービスは記事の一部を抜粋して表示し、各カードに出典を記載しています。写真は Wikimedia Commons の各ファイルのライセンスに従います。':'By the authors of each article. Excerpts are shown with a source link on each card. Images follow the license of each Wikimedia Commons file.','https://creativecommons.org/licenses/by-sa/4.0/deed.ja'],
   [J?'スポット・山のデータ':'Places & mountains','Wikidata — CC0 1.0','', 'https://www.wikidata.org/wiki/Wikidata:Licensing'],
   [J?'建物データ':'Buildings','© OpenStreetMap contributors — ODbL 1.0',J?'Overpass API 経由で取得し、見通しの判定に使用。':'Retrieved via the Overpass API and used for visibility checks.','https://www.openstreetmap.org/copyright'],
   [J?'航空写真（日本国内）':'Aerial imagery (Japan)',J?'地理院タイル（シームレス空中写真）出典：国土地理院':'GSI Tiles (Seamless aerial photos) — Geospatial Information Authority of Japan','','https://maps.gsi.go.jp/development/ichiran.html'],
   [J?'航空写真（日本国外）':'Aerial imagery (outside Japan)','Esri World Imagery','Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community','https://www.esri.com/en-us/legal/terms/full-master-agreement'],
   [J?'地形データ':'Terrain','Terrain Tiles (Mapzen / Tilezen, AWS Open Data)','SRTM, GMTED2010, ETOPO1, NED '+(J?'ほか':'and others'),'https://github.com/tilezen/joerd/blob/master/docs/attribution.md'],
   [J?'地図の描画':'Map rendering','MapLibre GL JS v4.7.1 — BSD 3-Clause License',J?'下記にライセンス全文を掲載。':'Full license text below.','https://github.com/maplibre/maplibre-gl-js'],
   [J?'音声':'Voice',J?'端末の音声合成機能（Web Speech API）':'Device text-to-speech (Web Speech API)','','']
  ];
  return `<h3>${J?'ライセンス・出典':'Licenses & Credits'}</h3><table class="dt">${rows.map(r=>`<tr><th>${r[0]}</th><td><b>${r[1]}</b>${r[2]?'<br>'+r[2]:''}${r[3]?`<br><a href="${r[3]}" target="_blank" rel="noopener">${J?'詳細':'Details'}</a>`:''}</td></tr>`).join('')}</table>
  <details><summary>MapLibre GL JS — License</summary><pre class="lic">${esc(document.getElementById('licMaplibre').textContent)}</pre></details>
  <p class="dd">${J?'本サービスのプログラム・デザインの著作権はSTONY & Co.に帰属します。':'The Service’s software and design are copyright of STONY & Co.'}<br>${APP.copy}</p>`;
}
function logHTML(){
  const J=lg()==='ja';
  return `<h3>${J?'バージョン情報':'About'}</h3>
  <div class="ab"><div class="abic">🧭</div><div><b>${APP.name}</b><br>${J?'バージョン':'Version'} ${APP.ver}<br><span class="dd">${J?'ビルド':'Build'} ${APP.build}</span></div></div>
  <p class="dd">${APP.copy}<br>${J?'提供':'Provided by'}：${J?CO.ja:'STONY & Co. (STONY株式会社)'}</p>
  <h4>${J?'更新履歴':'Changelog'}</h4>${CHANGELOG.map(([v,d,t])=>`<div class="cl"><b>v${v}</b> <span class="dd">${d}</span><br>${t[lg()]}</div>`).join('')}`;
}
let docTab='log';
function openAbout(tab){
  docTab=tab||'log'; const J=lg()==='ja';
  const tabs=[['log',J?'バージョン':'About'],['terms',J?'利用規約':'Terms'],['privacy',J?'プライバシー':'Privacy'],['lic',J?'ライセンス':'Licenses']];
  $('abTabs').innerHTML=tabs.map(([k,n])=>`<button data-k="${k}" class="${k===docTab?'on':''}">${n}</button>`).join('');
  $('abTabs').querySelectorAll('button').forEach(b=>b.onclick=()=>openAbout(b.dataset.k));
  $('abBody').innerHTML=docTab==='log'?logHTML():DOCS[docTab][lg()]();
  $('abBody').scrollTop=0; $('about').classList.add('show');
}
$('abClose').onclick=()=>$('about').classList.remove('show');
document.addEventListener('click',e=>{ const a=e.target.closest('[data-doc]'); if(a){ e.preventDefault(); openAbout(a.dataset.doc); } });
// ---------- 初回の規約同意 ----------
function termsAgreed(){ try{ return localStorage.getItem('terms.agreed')===APP.termsVer; }catch(e){ return false; } }
function syncAgree(){ const ok=$('agree').checked; ['bStart','bDemo'].forEach(id=>{ $(id).disabled=!ok; $(id).style.opacity=ok?1:.45; }); }
$('agree').checked=termsAgreed(); syncAgree();
$('agree').onchange=()=>{ try{ if($('agree').checked)localStorage.setItem('terms.agreed',APP.termsVer); else localStorage.removeItem('terms.agreed'); }catch(e){} syncAgree(); };
$('verTag').textContent='v'+APP.ver;
