"""
main.py
GitHub Actions から呼び出されるエントリーポイント
fetch → generate → notify の一連の処理を実行する
"""

import sys
from pathlib import Path

# src/ ディレクトリをモジュール検索パスに追加
sys.path.insert(0, str(Path(__file__).parent))

from fetch_indicators import fetch_all, fetch_review_and_outlook
from generate_report import generate_report, generate_alert
from notify import send_all, check_alerts


def main():
    # 1. 経済指標を取得
    data = fetch_all()

    # 2. アラート確認（緊急通知が必要か）
    alerts = check_alerts(data)
    for alert_type in alerts:
        alert_msg = generate_alert(alert_type, data)
        print(f"[ALERT] {alert_type}: 送信します")
        send_all(alert_msg)

    # 3. 昨日の振り返り・今日の見通しを生成
    review_data = fetch_review_and_outlook(data)

    # 4. 通常レポートを生成して送信（振り返り・見通し付き）
    report = generate_report(data, review_data)
    print("--- 生成されたレポート ---")
    print(report)
    print("-------------------------")
    send_all(report, with_quick_reply=True)


if __name__ == "__main__":
    main()
