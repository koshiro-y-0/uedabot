"""
main.py
GitHub Actions から呼び出されるエントリーポイント
fetch → generate → notify の一連の処理を実行する
"""

from fetch_indicators import fetch_all
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

    # 3. 通常レポートを生成して送信
    report = generate_report(data)
    print("--- 生成されたレポート ---")
    print(report)
    print("-------------------------")
    send_all(report)


if __name__ == "__main__":
    main()
