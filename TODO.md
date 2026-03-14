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

- [ ] `notify.py` を改修 — Quick Reply ボタン付き Push Message に対応
- [ ] 5つの選択ボタン（為替詳細/金利詳細/CPI詳細/短観詳細/今日の注目）を実装
- [ ] GitHub Actions からの毎朝配信で Quick Reply が表示されることを確認
- [ ] PR提出

---

## Phase 8：LINE Webhook + Vercel（ブランチ: `feature/webhook`）

- [ ] `api/webhook.py` を作成（Vercel Serverless Function）
- [ ] LINE Webhook の署名検証（`LINE_CHANNEL_SECRET`）を実装
- [ ] ユーザーメッセージ `詳細:〇〇` の解析 → Reply Message で詳細情報を返す処理を実装
- [ ] `vercel.json` 設定ファイルを作成
- [ ] Vercel にデプロイ・LINE Developers で Webhook URL を設定
- [ ] `LINE_CHANNEL_SECRET` を GitHub Secrets に追加
- [ ] PR提出

---

## Phase 9：詳細テンプレート・結合テスト（ブランチ: `feature/detail-templates`）

- [ ] 全5種の詳細テンプレートの仕上げ・動作確認
- [ ] Webhook → 詳細取得 → Reply の一連フローをテスト
- [ ] README.md にv2.0の使い方を追記
- [ ] 全体の動作確認完了
- [ ] PR提出

---

## 将来対応

- [ ] Streamlit ダッシュボードの追加（指標の時系列グラフ可視化）
- [ ] GitHub Pages でのレポートアーカイブ公開
- [ ] Claude Haiku API によるAI要約機能の追加

---

## ブランチ戦略

```
main
├── feature/fetch-indicators    # Phase 1 ✅
├── feature/template-engine     # Phase 2 ✅
├── feature/notify              # Phase 3 ✅
├── feature/github-actions      # Phase 4 ✅
├── fix/template-syntax-error   # Bug Fix  ✅
├── feature/date-format         # Phase 5
├── feature/detail-data         # Phase 6
├── feature/quick-reply         # Phase 7
├── feature/webhook             # Phase 8
└── feature/detail-templates    # Phase 9
```

各フェーズ完了後にPRを作成し、レビュー後に `main` へマージします。
