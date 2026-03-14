"""
notify.py
LINE Messaging API と Discord Webhook への通知送信モジュール
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_TOKEN = os.getenv("LINE_CHANNEL_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def send_line(message: str) -> bool:
    """
    LINE Messaging API でメッセージを送信する
    Args:
        message: 送信するテキスト
    Returns:
        送信成功ならTrue
    """
    if not LINE_CHANNEL_TOKEN or not LINE_USER_ID:
        print("[WARN] LINE環境変数が未設定のため送信をスキップします")
        return False

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": message}],
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        print("[OK] LINE送信成功")
        return True
    except requests.HTTPError as e:
        print(f"[ERROR] LINE送信失敗: {e.response.status_code} {e.response.text}")
        return False
    except Exception as e:
        print(f"[ERROR] LINE送信エラー: {e}")
        return False


def send_discord(message: str) -> bool:
    """
    Discord Webhook にメッセージを送信する
    Args:
        message: 送信するテキスト
    Returns:
        送信成功ならTrue
    """
    if not DISCORD_WEBHOOK_URL:
        print("[WARN] DISCORD_WEBHOOK_URLが未設定のため送信をスキップします")
        return False

    payload = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        print("[OK] Discord送信成功")
        return True
    except requests.HTTPError as e:
        print(f"[ERROR] Discord送信失敗: {e.response.status_code} {e.response.text}")
        return False
    except Exception as e:
        print(f"[ERROR] Discord送信エラー: {e}")
        return False


def send_all(message: str) -> None:
    """
    設定済みのすべての通知先にメッセージを送信する
    """
    line_ok = send_line(message)
    discord_ok = send_discord(message)

    if not line_ok and not discord_ok:
        print("[WARN] すべての通知チャンネルへの送信に失敗しました")


def check_alerts(data: dict) -> list[str]:
    """
    指標データからアラートの種別リストを返す
    Args:
        data: fetch_indicators.fetch_all() の返り値
    Returns:
        発生したアラート種別のリスト（例: ["forex", "cpi"]）
    """
    alerts = []

    usdjpy_diff = abs(data["usdjpy"] - data["usdjpy_prev"])
    if usdjpy_diff >= 1.5:
        alerts.append("forex")

    rate_diff = data["policy_rate"] - data["policy_rate_prev"]
    if rate_diff != 0:
        alerts.append("rate_change")

    cpi_diff = abs(data["cpi_total"] - data.get("cpi_prev_total", data["cpi_total"]))
    if cpi_diff >= 0.5:
        alerts.append("cpi")

    return alerts


if __name__ == "__main__":
    test_msg = "🏦 テスト送信：植田総裁Botの通知テストです。"
    send_all(test_msg)
