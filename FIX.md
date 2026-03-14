# 🔧 修正履歴（FIX LOG）

> コード修正時の箇所と内容を簡潔に記録するファイルです。

---

## 2026-03-14

### TODO.md — 事前準備チェックボックス更新
- **箇所**: `TODO.md` 事前準備セクション
- **内容**: GitHub Secrets（ESTAT_API_KEY / LINE_CHANNEL_TOKEN / LINE_USER_ID）登録完了につきチェック。DISCORD_WEBHOOK_URL は後回し。requirements.txt・README.md も作成済みのためチェック。

### Phase 1 — データ取得モジュール実装完了
- **箇所**: `src/fetch_indicators.py`, `tests/test_fetch.py`
- **内容**: 日銀IMAS API（政策金利・短観DI）、総務省e-Stat API（CPI）、Yahoo Finance（USD/JPY・EUR/JPY）の取得モジュールを実装。各APIにフォールバック処理あり。ユニットテスト4件作成。TODO.md Phase 1 を全チェック。
