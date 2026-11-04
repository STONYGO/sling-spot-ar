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

まとめて実行（Python の `playwright` と `Pillow` が必要。外部通信はすべてモック）:
```
python3 tests/run_all.py          # ビルド → 下記4本 → 既存テスト。失敗があれば終了コード 1
```
- `tests/test_ipad_layout.py` … iPad 各サイズ（縦・横・Split View・Slide Over）で表示が重ならない／画面内に収まる
- `tests/test_i18n.py` … 英語・中国語（繁體）・韓国語の画面に日本語が残っていない、`<html lang>`、端末言語の初期値
- `tests/test_offline.py` … 保存エリアの再利用（言語を変えても）、保存状態の表示、通信回復、Service Worker の更新
- `tests/test_dex.py` … 図鑑の読み込み検証（不正なファイル）、削除、言語をまたいだ同一スポット、ジャンル判定、スワイプ
- `tests/run_legacy.py` … 既存の test2〜test13 を実行（直書きパスを実行時だけ置換。日本語ロケールで起動）
- 修正前のビルドと比べたいときは `SSAR_BUILD=修正前の.html`（Service Worker は `SSAR_SW=修正前の sw.js`）を指定
