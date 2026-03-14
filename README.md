# 🏦 植田総裁Bot

日本銀行の公開APIを活用し、金利・為替・CPI・短観などの主要経済指標を毎朝自動配信するBotです。植田総裁の口調を模したテンプレート文で整形し、LINEまたはDiscordに通知します。**完全無料で運用できます。**

## 特徴

- 完全無料（LLM・有料API一切不使用）
- GitHub Actions によるサーバーレス自動運用
- 植田総裁口調テンプレートによる読みやすいサマリー配信
- 為替・金利・CPIのアラート通知機能

## セットアップ

詳細は [SPEC.md](./SPEC.md) を参照してください。

### 必要な環境変数（GitHub Secrets）

| 変数名 | 説明 |
|---|---|
| `ESTAT_API_KEY` | 総務省 e-Stat API キー |
| `LINE_CHANNEL_TOKEN` | LINE Messaging API トークン |
| `LINE_USER_ID` | LINE 送信先ユーザーID |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL |

## 開発状況

開発の進捗は [TODO.md](./TODO.md) を参照してください。
