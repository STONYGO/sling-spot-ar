---
owner: claude-cloud
status: running
heartbeat: 2026-11-05T06:04:05+08:00
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
- `source` から `night/claude-ar` を作成。

## 途中
- テスト環境構築・既存テストの実行（これから）

## 次の一手
- `vendor/` に maplibre-gl@4.7.1 を導入して `build.py` を実行 → 既存テスト `tests/test*.py` を実行し、現状の失敗を把握する。

## 判断記録
- リポジトリ指定が無かったため、セッションで利用可能なリポジトリのうち AR・図鑑・オフライン・`source` ブランチ・`main` に公開物という条件に一致する `STONYGO/sling-spot-ar` を対象と判断した。
- 依頼文に「site/ の公開物（main ブランチ）」とあるが、`source` ブランチに `site/` ディレクトリは無い。`main` ブランチの公開物（index.html・sw.js・NOTICE.md 等）全体を「触らない対象」と解釈した。【要確認】
- 本ファイルの Frontmatter はタスク運用ルール（owner/status/heartbeat）を優先し、`status: unverified` は付けていない（`status` の意味が衝突するため）。
