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
- [ ] LINE Messaging API の Push Message 実装
- [ ] 環境変数（`LINE_CHANNEL_TOKEN`・`LINE_USER_ID`）から認証情報を読み込む処理を実装
- [ ] 送信成功・失敗のログ出力を実装

### Discord Webhook
- [ ] Discord Webhook への POST リクエスト実装
- [ ] 環境変数（`DISCORD_WEBHOOK_URL`）から読み込む処理を実装

### アラートロジック
- [ ] 為替アラート：USD/JPY が前日比 ±1.5円以上で緊急通知
- [ ] 政策変更アラート：金利変動時に即時通知
- [ ] 物価動向アラート：CPI が前月比 ±0.5%以上で通知
- [ ] アラートと通常レポートを一元管理する `notify.py` を実装

### 成果物
- [ ] `src/notify.py` を作成・PR提出
- [ ] 通知テスト（ローカルで手動実行して動作確認）

---

## Phase 4：GitHub Actions / CI/CD（ブランチ: `feature/github-actions`）

### ワークフロー設定
- [ ] `.github/workflows/daily_report.yml` を作成
  - [ ] cron スケジュール設定（平日 09:00 JST = UTC 00:00）
  - [ ] Python 環境セットアップ（`actions/setup-python`）
  - [ ] 依存ライブラリインストール（`pip install -r requirements.txt`）
  - [ ] `fetch_indicators.py` → `generate_report.py` → `notify.py` の順で実行

### テスト・品質管理
- [ ] GitHub Actions でのテスト自動実行を設定（PR時にテストが走るようにする）
- [ ] `pytest` で全テストが通ることを確認
- [ ] ワークフローの手動実行（`workflow_dispatch`）を追加してデバッグできるようにする

### 最終確認
- [ ] 本番環境（GitHub Actions）での動作確認（手動トリガーで1回実行）
- [ ] LINE または Discord に正しくメッセージが届くことを確認
- [ ] エラー時のログ確認方法をREADMEに追記

### 成果物
- [ ] `.github/workflows/daily_report.yml` を作成・PR提出
- [ ] 全体の動作確認完了

---

## 拡張機能（将来対応）

- [ ] Streamlit ダッシュボードの追加（指標の時系列グラフ可視化）
- [ ] GitHub Pages でのレポートアーカイブ公開
- [ ] 短観詳細分析（製造業・非製造業の比較レポート）
- [ ] Claude Haiku API によるAI要約機能の追加

---

## ブランチ戦略

```
main
├── feature/fetch-indicators    # Phase 1
├── feature/template-engine     # Phase 2
├── feature/notify              # Phase 3
└── feature/github-actions      # Phase 4
```

各フェーズ完了後にPRを作成し、レビュー後に `main` へマージします。
