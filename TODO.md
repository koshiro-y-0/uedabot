# 🏦 植田総裁Bot — 開発TODOリスト

> 各フェーズはGitHubブランチを分けて開発し、PRでmainにマージする現場型ワークフローで進めます。

---

## 事前準備

- [x] GitHub Secretsに環境変数を登録する
  - [x] `ESTAT_API_KEY`（e-stat.go.jp で無料登録して取得）
  - [x] `LINE_CHANNEL_TOKEN`（LINE Developers で取得）
  - [x] `LINE_USER_ID`（LINE Developers コンソールで確認）
  - [ ] `DISCORD_WEBHOOK_URL`（Discordサーバー設定で生成）※後回し
- [x] `requirements.txt` を作成する
- [x] `README.md` を作成する（プロジェクト概要・セットアップ手順）

---

## Phase 1：データ取得（ブランチ: `feature/fetch-indicators`）

### 日銀 IMAS API
- [x] 日銀IMAS APIの仕様確認（エンドポイント・パラメータ）
- [x] 政策金利データの取得・パース実装
- [x] 短観（大企業製造業DI）データの取得・パース実装
- [x] 取得データをDataFrameに整形する処理を実装

### 総務省 e-Stat API
- [x] e-Stat APIの仕様確認（エンドポイント・statsDataId）
- [x] CPI（消費者物価指数）総合・コアの取得実装
- [x] 最新月のデータのみ抽出するロジックを実装

### Yahoo Finance（為替）
- [x] `yfinance` ライブラリの調査・採用可否確認
- [x] USD/JPY・EUR/JPY のリアルタイムレート取得実装
- [x] 前日比の計算ロジックを実装

### 成果物
- [x] `src/fetch_indicators.py` を作成・PR提出
- [x] `tests/test_fetch.py` を作成（各API取得のユニットテスト）

---

## Phase 2：テンプレートエンジン（ブランチ: `feature/template-engine`）

### Jinja2テンプレート
- [x] `templates/report.j2` を作成（通知メッセージのひな形）
- [x] 植田総裁口調テンプレート文を全パターン定義する
  - [x] 金利：変化なし
  - [x] 金利：引上げ
  - [x] 金利：引下げ
  - [x] CPI：上昇
  - [x] CPI：低下
  - [x] 為替：急変（±1.5円以上）

### レポート生成ロジック
- [x] `src/generate_report.py` を作成
- [x] `fetch_indicators.py` から取得したデータをテンプレートに埋め込む処理を実装
- [x] 指標の条件分岐（金利変動・CPI変動）でテンプレートを切り替えるロジックを実装
- [x] 生成されたレポートのフォーマット確認（手動テスト）

### 成果物
- [x] `src/generate_report.py` を作成・PR提出
- [x] `templates/report.j2` を作成・PR提出

---

## Phase 3：通知モジュール（ブランチ: `feature/notify`）

### LINE Messaging API
- [x] LINE Messaging API の Push Message 実装
- [x] 環境変数（`LINE_CHANNEL_TOKEN`・`LINE_USER_ID`）から認証情報を読み込む処理を実装
- [x] 送信成功・失敗のログ出力を実装

### Discord Webhook
- [x] Discord Webhook への POST リクエスト実装
- [x] 環境変数（`DISCORD_WEBHOOK_URL`）から読み込む処理を実装

### アラートロジック
- [x] 為替アラート：USD/JPY が前日比 ±1.5円以上で緊急通知
- [x] 政策変更アラート：金利変動時に即時通知
- [x] 物価動向アラート：CPI が前月比 ±0.5%以上で通知
- [x] アラートと通常レポートを一元管理する `notify.py` を実装

### 成果物
- [x] `src/notify.py` を作成・PR提出
- [ ] 通知テスト（ローカルで手動実行して動作確認）※Phase 4で実施

---

## Phase 4：GitHub Actions / CI/CD（ブランチ: `feature/github-actions`）

### ワークフロー設定
- [x] `.github/workflows/daily_report.yml` を作成
  - [x] cron スケジュール設定（平日 09:00 JST = UTC 00:00）
  - [x] Python 環境セットアップ（`actions/setup-python`）
  - [x] 依存ライブラリインストール（`pip install -r requirements.txt`）
  - [x] `fetch_indicators.py` → `generate_report.py` → `notify.py` の順で実行

### テスト・品質管理
- [x] GitHub Actions でのテスト自動実行を設定（PR時にテストが走るようにする）
- [ ] `pytest` で全テストが通ることを確認 ※マージ後に手動トリガーで確認
- [x] ワークフローの手動実行（`workflow_dispatch`）を追加してデバッグできるようにする

### 最終確認
- [ ] 本番環境（GitHub Actions）での動作確認（手動トリガーで1回実行）
- [ ] LINE または Discord に正しくメッセージが届くことを確認
- [ ] エラー時のログ確認方法をREADMEに追記

### 成果物
- [x] `.github/workflows/daily_report.yml` を作成・PR提出
- [ ] 全体の動作確認完了

---

## Phase 5：日付・曜日表示の改善（ブランチ: `feature/date-format`）

- [x] `fetch_indicators.py` の日付フォーマットに曜日を追加（例：`2026年3月14日（金）`）
- [x] `report.j2` に日付・曜日・前日比情報を追加
- [x] 短観の日付表示を改善（`2025-Q4` → `2025年Q4（12月調査）`）
- [x] USD/JPYの前日比を常に表示するよう修正
- [ ] PR提出

---

## Phase 6：詳細データ取得モジュール（ブランチ: `feature/detail-data`）

- [x] `src/fetch_detail.py` を作成
  - [x] 為替5日間推移・週間高値/安値の取得
  - [x] CPI詳細（総合/コア/食料エネルギー除く）の取得
  - [x] 短観詳細（製造業/非製造業DI比較）の取得
  - [x] 経済イベントカレンダー（定数定義）
- [x] `src/generate_detail.py` を作成（詳細レポート生成）
- [x] `templates/detail_*.j2` テンプレート5種を作成
- [x] `tests/test_detail.py` を作成
- [ ] PR提出

---

## Phase 7：Quick Reply ボタン対応（ブランチ: `feature/quick-reply`）

- [x] `notify.py` を改修 — Quick Reply ボタン付き Push Message に対応
- [x] 5つの選択ボタン（為替詳細/金利詳細/CPI詳細/短観詳細/今日の注目）を実装
- [ ] GitHub Actions からの毎朝配信で Quick Reply が表示されることを確認
- [ ] PR提出

---

## Phase 8：LINE Webhook + Vercel（ブランチ: `feature/webhook`）

- [x] `api/webhook.py` を作成（Vercel Serverless Function）
- [x] LINE Webhook の署名検証（`LINE_CHANNEL_SECRET`）を実装
- [x] ユーザーメッセージ `詳細:〇〇` の解析 → Reply Message で詳細情報を返す処理を実装
- [x] `vercel.json` 設定ファイルを作成
- [ ] Vercel にデプロイ・LINE Developers で Webhook URL を設定
- [ ] `LINE_CHANNEL_SECRET` を GitHub Secrets に追加
- [ ] PR提出

---

## Phase 9：詳細テンプレート・結合テスト（ブランチ: `feature/detail-templates`）

- [x] 全5種の詳細テンプレートの仕上げ・動作確認
- [x] Webhook → 詳細取得 → Reply の一連フローをテスト
- [x] README.md にv2.0の使い方を追記
- [x] 全体の動作確認完了（43テスト全通過）
- [ ] PR提出

---

## Phase 10：日次データ蓄積（ブランチ: `feature/data-store`）

- [ ] `data/` ディレクトリを作成
- [ ] `src/data_store.py` を作成
  - [ ] 日次指標データをCSVに追記保存する関数
  - [ ] CSVから指定期間のデータを読み取る関数
  - [ ] CSVが存在しない場合の初期化処理
- [ ] `main.py` を改修 — レポート送信後にCSV保存を呼び出す
- [ ] `daily_report.yml` を改修 — CSV保存後に `git commit & push` を追加
- [ ] `tests/test_data_store.py` を作成
- [ ] PR提出

---

## Phase 11：週間サマリー＋チャート画像（ブランチ: `feature/weekly-summary`）

- [x] `src/generate_weekly.py` を作成
  - [x] CSVから今週5日分のデータを集計
  - [x] 週間変動幅・高値/安値の算出
  - [x] 来週の注目イベントの抽出
- [x] `src/generate_chart.py` を作成
  - [x] matplotlib で USD/JPY 5日間チャート画像を生成
  - [x] PNG画像として一時保存
- [x] `notify.py` を改修 — LINE Image Message 送信に対応
- [x] `templates/weekly_summary.j2` を作成
- [x] `.github/workflows/weekly_summary.yml` を作成（金曜17:00 JST）
- [x] `requirements.txt` に matplotlib を追加
- [x] `tests/test_weekly.py` を作成
- [ ] PR提出

---

## Phase 12：経済用語解説機能（ブランチ: `feature/glossary`）

- [ ] `src/generate_glossary.py` を作成
  - [ ] 6つの用語解説テンプレートを定義（CPI/短観/政策金利/為替/GDP/日銀）
  - [ ] `解説:〇〇` コマンドのパース関数
  - [ ] `解説:一覧` で選択可能な用語一覧を返す機能
- [ ] `templates/glossary.j2` を作成
- [ ] `api/webhook.py` を改修 — `解説:〇〇` コマンドに対応
- [ ] Quick Reply に「📖 用語解説」ボタンを追加
- [ ] `tests/test_glossary.py` を作成
- [ ] PR提出

---

## Phase 13：リッチメニュー（ブランチ: `feature/richmenu`）

- [ ] `src/generate_richmenu.py` を作成
  - [ ] Pillow で 2500×843px のリッチメニュー画像を生成
  - [ ] 6分割ボタン（為替/金利/CPI/短観/用語/注目）
- [ ] リッチメニュー登録スクリプトを作成（LINE Messaging API経由）
  - [ ] リッチメニューオブジェクト作成
  - [ ] 画像アップロード
  - [ ] デフォルトリッチメニューとして設定
- [ ] `requirements.txt` に Pillow を追加
- [ ] PR提出

---

## Phase 14：リアルタイム為替アラート（ブランチ: `feature/forex-alert`）

- [ ] `src/forex_alert.py` を作成
  - [ ] 現在の為替レートを取得
  - [ ] CSVの直近レートと比較
  - [ ] 閾値（デフォルト ±2円）超えの場合にアラート送信
- [ ] `templates/forex_alert.j2` を作成
- [ ] `.github/workflows/forex_alert.yml` を作成
  - [ ] 平日09:00〜18:00 JSTに15分間隔で実行
  - [ ] 閾値以下なら何もせず終了
- [ ] `FOREX_ALERT_THRESHOLD` 環境変数対応
- [ ] `tests/test_forex_alert.py` を作成
- [ ] PR提出

---

## 将来対応

- [ ] Streamlit ダッシュボードの追加（指標の時系列グラフ可視化）
- [ ] GitHub Pages でのレポートアーカイブ公開
- [ ] Claude Haiku API によるAI要約機能の追加
- [ ] 「詳細:比較」コマンドで前月比較データを表示

---

## ブランチ戦略

```
main
├── feature/fetch-indicators    # Phase 1  ✅
├── feature/template-engine     # Phase 2  ✅
├── feature/notify              # Phase 3  ✅
├── feature/github-actions      # Phase 4  ✅
├── fix/template-syntax-error   # Bug Fix  ✅
├── feature/date-format         # Phase 5  ✅
├── feature/detail-data         # Phase 6  ✅
├── feature/quick-reply         # Phase 7  ✅
├── feature/webhook             # Phase 8  ✅
├── feature/detail-templates    # Phase 9  ✅
├── feature/morning-review      # 振り返り  ✅
├── fix/import-path             # Bug Fix  ✅
├── fix/quick-reply-persist     # Bug Fix  ✅
├── feature/data-store          # Phase 10
├── feature/weekly-summary      # Phase 11
├── feature/glossary            # Phase 12
├── feature/richmenu            # Phase 13
└── feature/forex-alert         # Phase 14
```

各フェーズ完了後にPRを作成し、レビュー後に `main` へマージします。
