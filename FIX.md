# 🔧 修正履歴（FIX LOG）

> コード修正時の箇所と内容を簡潔に記録するファイルです。

---

### Phase 10 — 日次データ蓄積（CSV保存・自動コミット）
- **箇所**: `src/data_store.py`（新規）, `src/main.py`, `daily_report.yml`, `data/`
- **内容**:
  - `data_store.py` 新規作成: CSV蓄積（save_daily）・読取（load_recent, load_week_data）
  - `main.py` にデータ保存処理を追加（レポート送信後にCSV追記）
  - `daily_report.yml` にCSV自動コミット・プッシュステップを追加
  - 同日データの重複防止機能付き

---

### fix/import-path — GitHub Actionsでのインポートパスエラー修正
- **箇所**: `src/fetch_indicators.py` L251
- **原因**: `from src.fetch_detail import ECONOMIC_EVENTS` — `main.py` が `sys.path` に `src/` を追加して実行するため `src.` プレフィックスがあると `ModuleNotFoundError` になる
- **修正**: `from fetch_detail import ECONOMIC_EVENTS` に変更

---

### feature/morning-review — 毎朝の振り返り・見通し機能追加
- **箇所**: `daily_report.yml`, `fetch_indicators.py`, `generate_report.py`, `main.py`, `report.j2`
- **内容**:
  - cron を平日 08:30 JST（UTC 23:30）に変更
  - `fetch_review_and_outlook()` を新規作成：昨日の振り返り（月曜は金曜）＋今日の見通しを生成
  - `report.j2` に「振り返り」「見通し」セクションを追加
  - `generate_report()` / `build_template_context()` に review_data 引数を追加
  - `main.py` から振り返りデータを取得してレポートに反映

---

## 2026-03-14

### TODO.md — 事前準備チェックボックス更新
- **箇所**: `TODO.md` 事前準備セクション
- **内容**: GitHub Secrets（ESTAT_API_KEY / LINE_CHANNEL_TOKEN / LINE_USER_ID）登録完了につきチェック。DISCORD_WEBHOOK_URL は後回し。requirements.txt・README.md も作成済みのためチェック。

### Phase 1 — データ取得モジュール実装完了
- **箇所**: `src/fetch_indicators.py`, `tests/test_fetch.py`
- **内容**: 日銀IMAS API（政策金利・短観DI）、総務省e-Stat API（CPI）、Yahoo Finance（USD/JPY・EUR/JPY）の取得モジュールを実装。各APIにフォールバック処理あり。ユニットテスト4件作成。TODO.md Phase 1 を全チェック。

### Phase 2 — テンプレートエンジン実装完了
- **箇所**: `src/generate_report.py`, `templates/report.j2`
- **内容**: Jinja2テンプレートで植田総裁口調レポートを生成。金利変動（変化なし/引上げ/引下げ）・CPI変動（上昇/低下）・為替急変の6パターンのコメント自動選択を実装。アラートメッセージ生成（為替/金利変更/物価）も対応。TODO.md Phase 2 を全チェック。

### Phase 3 — 通知モジュール実装完了
- **箇所**: `src/notify.py`
- **内容**: LINE Messaging API（Push Message）とDiscord Webhookへの通知送信を実装。環境変数未設定時のスキップ処理・送信成功/失敗のログ出力を実装。アラート判定ロジック（為替±1.5円/金利変動/CPI±0.5%）を`check_alerts()`で実装。`send_all()`で全チャンネルへの一括送信対応。TODO.md Phase 3 を全チェック。

### Phase 4 — GitHub Actions CI/CD実装完了
- **箇所**: `.github/workflows/daily_report.yml`, `.github/workflows/test.yml`, `src/main.py`, `.gitignore`
- **内容**: 毎朝レポート配信ワークフロー（cron平日09:00 JST + workflow_dispatch）、PR時テスト自動実行ワークフローを作成。エントリーポイント`main.py`を実装（fetch→generate→notify）。`sys.path`修正でGitHub Actions上のimportパスを解決。`.gitignore`追加・`.DS_Store`除外。TODO.md Phase 4 を更新。

### BUG FIX — Quick Reply ボタンが詳細レポート返信後に消える問題
- **箇所**: `api/webhook.py`
- **原因**: Reply Message にQuick Replyボタンを付与していなかったため、詳細レポート返信後にボタンが消えていた
- **修正**: `reply_message()` で返信するメッセージにも `quickReply` を付与し、ボタンを常に表示するよう変更

### Phase 9 — 結合テスト・README更新
- **箇所**: `tests/test_integration.py`, `README.md`
- **内容**:
  - 結合テスト15件作成（全5カテゴリのE2Eフロー・テンプレートエラーチェック・署名検証・全角コロン対応）
  - README.mdをv2.0対応に全面更新（Quick Reply機能・Vercelデプロイ手順・ディレクトリ構成）
  - 全テスト43件通過を確認

### Phase 8 — LINE Webhook + Vercel Serverless Function
- **箇所**: `api/webhook.py`, `vercel.json`, `tests/test_webhook.py`
- **内容**:
  - `api/webhook.py`: LINE Webhook受信 → 署名検証 → `詳細:〇〇` コマンド解析 → Reply Message で詳細レポートを返信
  - `vercel.json`: Vercel Serverless Function の設定（`/api/webhook` ルート）
  - テスト8件作成（署名検証3件 + イベント処理5件）

### Phase 7 — Quick Reply ボタン対応
- **箇所**: `src/notify.py`, `src/main.py`, `templates/report.j2`
- **内容**:
  - `notify.py`: `send_line()` に `with_quick_reply` パラメータ追加。5つの選択ボタン（為替/金利/CPI/短観/注目）を Quick Reply として付与
  - `main.py`: 毎朝配信時に `send_all(report, with_quick_reply=True)` で Quick Reply 付きメッセージを送信
  - `report.j2`: メッセージ末尾に「詳しく知りたい項目をタップ ↓」案内文を追加

### Phase 6 — 詳細データ取得モジュール実装
- **箇所**: `src/fetch_detail.py`, `src/generate_detail.py`, `templates/detail_*.j2`, `tests/test_detail.py`
- **内容**:
  - `fetch_detail.py`: 5カテゴリ（為替/金利/CPI/短観/注目）の詳細データ取得を実装
  - `generate_detail.py`: Jinja2テンプレートによる詳細レポート生成。`parse_detail_command()`でユーザーメッセージ解析
  - テンプレート5種（`detail_forex.j2`等）を作成
  - テスト16件作成（データ取得・レポート生成・コマンド解析）

### Phase 5 — 日付・曜日表示の改善
- **箇所**: `src/fetch_indicators.py`, `templates/report.j2`, `src/generate_report.py`
- **内容**:
  - レポートヘッダー・為替時刻に曜日（月〜日）を追加（例：`2026年3月14日（金）`）
  - USD/JPYの前日比を常に表示するよう変更（アラート時のみ → 常時表示）
  - 短観日付を `2025-Q4` → `2025年Q4（12月調査）` にフォーマット改善
  - `%q`（無効なstrftime指令）のフォールバック修正

### BUG FIX — GitHub Actions実行時エラー修正
- **箇所**: `templates/report.j2` (11行目), `src/fetch_indicators.py` (99-114行目)
- **原因**: (1) Jinja2テンプレートで `{{ usdjpy_diff:+.2f }}` というPython f-string構文を使用していたが、Jinja2では `{{ "%+.2f"|format(usdjpy_diff) }}` が正しい構文。(2) e-Stat APIレスポンスのキー構造が想定と異なりKeyErrorが発生。
- **修正**: (1) テンプレートの書式指定をJinja2のformatフィルタに修正。(2) e-Stat APIのレスポンスパースを`.get()`チェーンで堅牢化。
