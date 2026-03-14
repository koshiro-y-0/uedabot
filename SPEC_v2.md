# 🏦 植田総裁Bot — 拡張機能仕様書

**Version 2.0 | 2026年3月**
**コスト完全ゼロ構成を維持**

---

## 1. 拡張の目的

v1.0 では毎朝の一方向配信のみだったが、v2.0 ではユーザーが **LINE上で選択操作** をして、知りたい指標の詳細情報をオンデマンドで取得できるインタラクティブ機能を追加する。

---

## 2. 通知メッセージ完成イメージ（v2.0）

### 2.1 毎朝の定期配信（改善）

```
🏦 【日銀レポート】2026年3月14日（金）09:00配信
━━━━━━━━━━━━━━━━━━━━
📊 本日の主要指標サマリー
━━━━━━━━━━━━━━━━━━━━

📅 2026年3月14日（金）

🎯 政策金利：0.50%（前回比 変化なし）
   →「物価の基調は概ね見通し通り。先行きのリスクは上下双方向に存在します。」

💱 為替相場（09:00時点）
   USD/JPY：152.30円（前日比 +0.50円）
   EUR/JPY：163.45円

📈 CPI（2026年1月）：総合 3.2%  コア 2.8%

🏭 短観・大企業製造業DI：+12（2025年Q4）

📌 次回政策決定会合：2026年4月30日

━━━━━━━━━━━━━━━━━━━━
💡 詳しく知りたい項目をタップ ↓
```

※ メッセージ下部に Quick Reply ボタンが表示される

### 2.2 Quick Reply ボタン（選択肢）

毎朝のレポート送信時に、以下の選択ボタンが表示される：

| ボタンラベル | 送信されるテキスト | 表示される詳細情報 |
|---|---|---|
| 📊 為替詳細 | `詳細:為替` | USD/JPY・EUR/JPYの直近5日間推移・前日比・週間変動幅 |
| 🎯 金利詳細 | `詳細:金利` | 政策金利の推移・次回会合日程・過去の変更履歴 |
| 📈 CPI詳細 | `詳細:CPI` | CPI総合/コア/食料エネルギー除くの詳細・前月比・前年比 |
| 🏭 短観詳細 | `詳細:短観` | 製造業/非製造業DI比較・先行き見通しDI |
| 📰 今日の注目 | `詳細:注目` | 本日の経済イベントカレンダー・注目ポイント |

### 2.3 詳細レスポンス例（為替の場合）

```
💱 為替相場 — 詳細レポート
━━━━━━━━━━━━━━━━━━━━
📅 2026年3月14日（金）09:00時点

■ USD/JPY
  現在値：152.30円
  前日比：+0.50円（+0.33%）
  週間高値：153.20円（3/11）
  週間安値：150.80円（3/12）
  5日間推移：150.80 → 151.20 → 151.80 → 152.30

■ EUR/JPY
  現在値：163.45円
  前日比：-0.15円（-0.09%）

📊 トレンド判定：円安方向で推移中
「為替市場は米国金利動向を注視しつつ、
 緩やかな円安基調で推移しております。」
```

---

## 3. システムアーキテクチャ（v2.0）

### 3.1 全体構成

```
[定期配信]                          [インタラクティブ応答]
GitHub Actions (cron)               LINE Webhook → Vercel (serverless)
    ↓                                    ↓
fetch → generate → notify          ユーザーのタップを受信
    ↓                                    ↓
LINE Push Message                   fetch_detail → generate_detail
  + Quick Reply ボタン                   ↓
                                    LINE Reply Message
```

### 3.2 技術スタック（追加分）

| 役割 | 技術・ツール | コスト |
|---|---|---|
| Webhook サーバー | Vercel Serverless Functions（Python） | 無料（月100GB帯域） |
| LINE Webhook | LINE Messaging API Reply Message | 無料 |
| LINE Channel Secret | Webhook署名検証 | — |
| 為替履歴データ | yfinance（過去5日分） | 無料 |

> **注記**: Vercel の無料プランで十分対応可能（1日数十リクエスト程度）

---

## 4. 機能仕様

### 4.1 Quick Reply 付き Push Message

毎朝のレポート送信時に、テキストメッセージに加えて Quick Reply ボタンを付与する。ユーザーがボタンをタップすると、対応するテキスト（例: `詳細:為替`）がBot宛に送信される。

### 4.2 Webhook による応答

LINE の Webhook URL に Vercel の Serverless Function を設定。ユーザーから `詳細:〇〇` のメッセージを受信すると、対応する詳細情報を Reply Message で返す。

### 4.3 詳細データ取得

| カテゴリ | 取得データ | ソース |
|---|---|---|
| 為替詳細 | 直近5日間のUSD/JPY・EUR/JPY推移、前日比、週間高値/安値 | Yahoo Finance |
| 金利詳細 | 政策金利推移、次回会合日程、過去の変更履歴（直近3回分） | 日銀IMAS / 定数 |
| CPI詳細 | 総合/コア/食料エネルギー除くの3系列、前月比、前年比 | e-Stat API |
| 短観詳細 | 製造業/非製造業DI、先行き見通し、前回比 | 日銀IMAS / 定数 |
| 今日の注目 | 経済イベントカレンダー（日銀会合・統計発表日程） | 定数（手動更新） |

### 4.4 日付・曜日表示の改善

v2.0 ではすべてのメッセージに **年月日 + 曜日** を表示する。

| 箇所 | v1.0 | v2.0 |
|---|---|---|
| レポートヘッダー | `2026年3月14日` | `2026年3月14日（金）` |
| 為替時刻 | `09:00時点` | `2026年3月14日（金）09:00時点` |
| CPI日付 | `2026年1月` | `2026年1月`（月次データのためそのまま） |
| 短観日付 | `2025-Q4` | `2025年Q4（12月調査）` |

---

## 5. 環境変数（追加）

| 変数名 | 内容 | 取得方法 |
|---|---|---|
| `LINE_CHANNEL_SECRET` | Webhook署名検証用シークレット | LINE Developers コンソール |

> 既存の `LINE_CHANNEL_TOKEN`・`LINE_USER_ID`・`ESTAT_API_KEY` はそのまま使用

---

## 6. ディレクトリ構成（v2.0）

```
uedabot/
├── .github/
│   └── workflows/
│       ├── daily_report.yml          # 毎朝配信（既存）
│       └── test.yml                  # テスト自動実行（既存）
├── api/
│   └── webhook.py                    # Vercel Serverless: LINE Webhook受信
├── src/
│   ├── fetch_indicators.py           # データ取得（既存）
│   ├── fetch_detail.py               # 詳細データ取得（新規）
│   ├── generate_report.py            # レポート生成（既存・改修）
│   ├── generate_detail.py            # 詳細レポート生成（新規）
│   ├── notify.py                     # 通知送信（既存・改修：Quick Reply対応）
│   └── main.py                       # エントリーポイント（既存）
├── templates/
│   ├── report.j2                     # 毎朝レポート（既存・改修）
│   ├── detail_forex.j2               # 為替詳細テンプレート（新規）
│   ├── detail_rate.j2                # 金利詳細テンプレート（新規）
│   ├── detail_cpi.j2                 # CPI詳細テンプレート（新規）
│   ├── detail_tankan.j2              # 短観詳細テンプレート（新規）
│   └── detail_events.j2             # 注目イベントテンプレート（新規）
├── tests/
│   ├── test_fetch.py                 # 既存テスト
│   ├── test_detail.py                # 詳細取得テスト（新規）
│   └── test_webhook.py               # Webhookテスト（新規）
├── vercel.json                       # Vercel設定ファイル（新規）
├── SPEC.md                           # v1.0仕様書
├── SPEC_v2.md                        # 本仕様書
├── TODO.md
├── FIX.md
├── requirements.txt
└── README.md
```

---

## 7. 開発フェーズ（v2.0）

| フェーズ | ブランチ | 内容 | 成果物 |
|---|---|---|---|
| Phase 5 | `feature/date-format` | 日付・曜日表示の改善、レポートの情報拡充 | `report.j2` 改修 |
| Phase 6 | `feature/detail-data` | 詳細データ取得モジュール（為替5日間推移・CPI詳細等） | `fetch_detail.py`, `generate_detail.py` |
| Phase 7 | `feature/quick-reply` | Quick Reply ボタン付きPush Message対応 | `notify.py` 改修 |
| Phase 8 | `feature/webhook` | LINE Webhook + Vercel Serverless Function | `api/webhook.py`, `vercel.json` |
| Phase 9 | `feature/detail-templates` | 詳細テンプレート5種の作成・結合テスト | `templates/detail_*.j2` |

---

## 8. コスト試算（v2.0）

| 項目 | 月額コスト | 備考 |
|---|---|---|
| v1.0 全機能 | ¥0 | 既存 |
| Vercel Serverless | ¥0 | Hobby プラン（月100GB帯域・100時間実行） |
| LINE Reply Message | ¥0 | Reply Message は無料（Push Messageの200通制限とは別枠） |
| **合計** | **¥0** | **引き続き完全無料** |

---

## 9. 制約・注意事項

- LINE の Quick Reply はスマホアプリでのみ表示される（PC版LINEでは非表示）
- Webhook サーバーは常時稼働ではなく、リクエスト時にコールドスタートが発生する場合がある（Vercel の特性上、初回応答に1-2秒かかることがある）
- Reply Message はユーザーのメッセージに対する応答としてのみ送信可能（30秒以内）
- 詳細データの取得は API コール数を増やすため、連続タップ時のレート制限に注意
