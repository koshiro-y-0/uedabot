# 🏦 植田総裁Bot

日本銀行の公開APIを活用し、金利・為替・CPI・短観などの主要経済指標を毎朝自動配信するBotです。植田総裁の口調を模したテンプレート文で整形し、LINEに通知します。**完全無料で運用できます。**

## 特徴

- 完全無料（LLM・有料API一切不使用）
- GitHub Actions によるサーバーレス自動運用（毎朝9:00 JST配信）
- 植田総裁口調テンプレートによる読みやすいサマリー配信
- 為替・金利・CPIのアラート通知機能
- **Quick Reply ボタンで詳細情報をオンデマンド取得**（v2.0）

## v2.0 インタラクティブ機能

毎朝のレポート下部に表示される Quick Reply ボタンをタップすると、詳細情報が返ってきます。

| ボタン | 内容 |
|---|---|
| 📊 為替詳細 | USD/JPY・EUR/JPYの5日間推移・週間高値安値・トレンド判定 |
| 🎯 金利詳細 | 政策金利推移・変更履歴（直近3回）・次回会合日程 |
| 📈 CPI詳細 | 総合/コア/コアコアCPIの3系列比較・前月比 |
| 🏭 短観詳細 | 製造業/非製造業DI比較・先行き見通しDI |
| 📰 今日の注目 | 今後の経済イベントカレンダー |

> Quick Reply はスマホの LINE アプリでのみ表示されます（PC版では非表示）

## セットアップ

### 1. GitHub Secrets の設定

| 変数名 | 説明 |
|---|---|
| `ESTAT_API_KEY` | 総務省 e-Stat API キー |
| `LINE_CHANNEL_TOKEN` | LINE Messaging API チャネルアクセストークン |
| `LINE_USER_ID` | LINE 送信先ユーザーID |

### 2. Vercel デプロイ（v2.0 Quick Reply 応答用）

1. [Vercel](https://vercel.com) で GitHub リポジトリをインポート
2. 環境変数を設定:
   - `LINE_CHANNEL_SECRET` — LINE Developers「チャネル基本設定」のチャネルシークレット
   - `LINE_CHANNEL_TOKEN` — チャネルアクセストークン（GitHub Secrets と同じ値）
   - `ESTAT_API_KEY` — e-Stat API キー（GitHub Secrets と同じ値）
3. LINE Developers コンソールで Webhook URL を設定:
   - URL: `https://<your-project>.vercel.app/api/webhook`
   - 「Webhook の利用」をオンにする

## ディレクトリ構成

```
uedabot/
├── .github/workflows/
│   ├── daily_report.yml      # 毎朝配信ワークフロー
│   └── test.yml              # PR時テスト自動実行
├── api/
│   └── webhook.py            # Vercel Serverless: LINE Webhook受信
├── src/
│   ├── fetch_indicators.py   # 経済指標取得（日銀/e-Stat/Yahoo Finance）
│   ├── fetch_detail.py       # 詳細データ取得（5カテゴリ）
│   ├── generate_report.py    # 毎朝レポート生成
│   ├── generate_detail.py    # 詳細レポート生成
│   ├── notify.py             # LINE/Discord通知（Quick Reply対応）
│   └── main.py               # エントリーポイント
├── templates/
│   ├── report.j2             # 毎朝レポートテンプレート
│   ├── detail_forex.j2       # 為替詳細
│   ├── detail_rate.j2        # 金利詳細
│   ├── detail_cpi.j2         # CPI詳細
│   ├── detail_tankan.j2      # 短観詳細
│   └── detail_events.j2      # 注目イベント
├── tests/                    # テスト（43件）
├── vercel.json               # Vercel設定
├── SPEC.md                   # v1.0仕様書
├── SPEC_v2.md                # v2.0仕様書
├── TODO.md                   # 開発タスク
└── FIX.md                    # 修正履歴
```

## 開発状況

詳細は [TODO.md](./TODO.md)、仕様は [SPEC_v2.md](./SPEC_v2.md) を参照してください。
