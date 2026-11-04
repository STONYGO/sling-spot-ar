---
owner: claude-cloud
status: running
heartbeat: 2026-11-05T06:56:48+08:00
branch: night/claude-ar
base: source (3ad168b)
created: 2026-11-05
tags: [sling-spot-ar, 夜間無人タスク, HANDOFF]
---

# HANDOFF — Sling Spot AR 夜間タスク（claude-cloud）

## 依頼内容（要約）
- ブランチ `night/claude-ar`（`source` を起点）で作業。
- Playwright でテストを実行し、**iPad 表示／多言語／オフライン／図鑑** の不具合を修正。
- `main`（公開物 index.html 等）には触れない。成果は PR に留め、マージしない。

## 完了
- 着手前確認: `CLAUDE.md`・`HANDOFF.md`・`TASKS.md` はどのブランチにも存在しなかった → 本ファイルを新規作成。
- `source` から `night/claude-ar` を作成。`source` のビルド結果は `main` の index.html とビルド時刻以外一致することを確認。
- テスト環境: Python Playwright 1.63（環境の Chromium を使用）＋ maplibre-gl@4.7.1 でビルド成功。
- `tests/run_legacy.py` を追加（既存テストの直書きパス `/home/claude/proto` を実行時だけ置換して実行。既存スクリプトは無変更）。
- ベースライン: 既存 13 本中 12 本は完走。`test.py` は規約同意（v1.0-beta で追加）より前のテストで、ボタンが無効のため失敗（アプリの不具合ではない）。

## 確認できた不具合（修正予定）
### iPad 表示
- Split View（幅590px）・Slide Over（幅375px）で「🧭 方位合わせ」等の右上ボタンが左上の状態表示（HUD）に重なる。
- デモ操作パネルが下部の丸ボタン（⚙️🖼️📖）に重なる（iPad mini 縦 768px・Split View・Slide Over）。
- Slide Over で開始画面の「リセット」と著作権フッターが重なる。高さが足りないと開始画面が上下で切れてスクロールできない。
- 解説カードに地図の出典表示（Esri／地理院タイル）が重なる。横長画面でカードが全幅になり読みにくい。
- 図鑑: 回転・リサイズ時にページ位置を再計算しない／タッチのスワイプでジャンル切替ができない（touch-action 未指定）。
- ボタンの連続タップで iPad Safari がダブルタップ拡大する（touch-action: manipulation 未指定）。
### 多言語
- 英・中・韓でも、設定画面・図鑑・ガイド・開始画面本文・解説カード（方位・出典・タグ／図鑑／共有ボタン）・HUD・警告・トースト・起動チェック等が日本語のまま。`<html lang>` も ja 固定。
- 英語等では既定スポット（仙台城など）が日本語名のまま表示され、Wikipedia の英語名と二重に出る。
- 英・中・韓のスポットは図鑑のジャンル判定がほぼ「その他」になる。
### オフライン
- 言語ごとにしか保存エリアを参照しないため、日本語で保存→英語に切替えるとオフラインでスポットが出ない。
- 言語間リンク（langlinks）を保存しないため、オフラインで別言語の解説が出ない。
- 保存済み情報が再読み込み後に表示されない。通信回復時に再取得しない。
- Service Worker: 4秒以内に本体を取得できない回線では新しい版がキャッシュされず、古い版のまま更新されない。
### 図鑑
- 「読み込み」で不完全なファイルを読むと図鑑が開けなくなる（genre/tags 欠落でエラー）。`javascript:` URL がリンクに入り得る（セキュリティ）。
- あるジャンル（タグ）の最後の1件を削除すると、該当なし表示のままタブが選択されない。
- 同じ場所を言語を変えて訪れると別項目として二重登録される。

## 途中
- 上記の修正と、修正を検証する assertion 付き Playwright テストの追加（これから）

## 次の一手
- `src/app.html` の i18n 基盤（T 辞書拡張・data-i18n）→ iPad レイアウト → 図鑑 → オフライン（sw.js 含む）の順で修正し、都度テスト。

## 判断記録
- リポジトリ指定が無かったため、セッションで利用可能なリポジトリのうち AR・図鑑・オフライン・`source` ブランチ・`main` に公開物という条件に一致する `STONYGO/sling-spot-ar` を対象と判断した。
- 依頼文に「site/ の公開物（main ブランチ）」とあるが、`source` ブランチに `site/` ディレクトリは無い。`main` ブランチの公開物（index.html・sw.js・NOTICE.md 等）全体を「触らない対象」と解釈した。【要確認】
- 本ファイルの Frontmatter はタスク運用ルール（owner/status/heartbeat）を優先し、`status: unverified` は付けていない（`status` の意味が衝突するため）。
- 既存テスト（test*.py）は原作者の探索用スクリプトのため改変せず、ランナー側でパスを置換する方式にした。
- ビルド成果物（sling-spot-ar-prototype.html）と node_modules は `.gitignore` に追加し、コミットしない（`main` への反映は人の判断）。
