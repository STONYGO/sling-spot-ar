# Sling Spot AR — source (© 2026 STONY & Co. All Rights Reserved.)

公開版（main ブランチの index.html）を生成するための元ファイル一式です。

## ビルド
```
cd vendor && npm install maplibre-gl@4.7.1 && cd ..
python3 build.py            # → sling-spot-ar-prototype.html（main の index.html として配置）
```
- `src/app.html` … アプリ本体（MapLibre は build.py で埋め込み）
- `legal/docs.js` … 規約・プライバシー・ライセンス・更新履歴（app.html に反映済みの原本）
- `sw.js` … オフライン用 Service Worker（main に配置）

## テスト（Playwright + Chromium）
`tests/test*.py` … 自動テスト。test6 は `python3 -m http.server 8765` を起動してから実行。
