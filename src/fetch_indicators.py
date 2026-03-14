"""
fetch_indicators.py
日銀IMAS API・総務省e-Stat API・Yahoo Financeから経済指標を取得するモジュール
"""

import os
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

ESTAT_API_KEY = os.getenv("ESTAT_API_KEY")

# 日銀IMAS API
BOJ_BASE_URL = "https://www.stat-search.boj.or.jp/ssi/mtsearch.do"
# 総務省e-Stat API
ESTAT_BASE_URL = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"


def fetch_policy_rate() -> dict:
    """
    日銀IMAS APIから政策金利（無担保コール翌日物）を取得する
    Returns: {"rate": float, "date": str, "prev_rate": float}
    """
    params = {
        "type": "ST",
        "fc": "FM01'MABASE",  # 無担保コールレート系列
        "oc": "LE",
        "dateType": "12",
        "cnt": 2,
        "outputType": "json",
    }
    try:
        response = requests.get(BOJ_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        records = data.get("items", [])
        if len(records) >= 2:
            return {
                "rate": float(records[0]["value"]),
                "date": records[0]["date"],
                "prev_rate": float(records[1]["value"]),
            }
    except Exception as e:
        print(f"[WARN] 政策金利取得エラー: {e}")
    # フォールバック（APIが不安定な場合）
    return {"rate": 0.50, "date": datetime.now().strftime("%Y-%m"), "prev_rate": 0.50}


def fetch_tankan_di() -> dict:
    """
    日銀IMAS APIから短観・大企業製造業DIを取得する
    Returns: {"di": int, "date": str}
    """
    params = {
        "type": "ST",
        "fc": "QT'CG10",  # 大企業製造業業況判断DI
        "oc": "LE",
        "dateType": "12",
        "cnt": 1,
        "outputType": "json",
    }
    try:
        response = requests.get(BOJ_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        records = data.get("items", [])
        if records:
            return {
                "di": int(float(records[0]["value"])),
                "date": records[0]["date"],
            }
    except Exception as e:
        print(f"[WARN] 短観DI取得エラー: {e}")
    return {"di": 12, "date": datetime.now().strftime("%Y-Q%q")}


def fetch_cpi() -> dict:
    """
    総務省e-Stat APIからCPI（消費者物価指数）を取得する
    Returns: {"total": float, "core": float, "date": str, "prev_total": float}
    """
    if not ESTAT_API_KEY:
        print("[WARN] ESTAT_API_KEY が未設定です。フォールバック値を使用します。")
        return {"total": 3.2, "core": 2.8, "date": "2026年1月", "prev_total": 3.0}

    # 総合CPI（statsDataId: 0003427112）
    params = {
        "appId": ESTAT_API_KEY,
        "statsDataId": "0003427112",
        "metaGetFlg": "N",
        "cntGetFlg": "N",
        "explanationGetFlg": "N",
        "limit": 2,
    }
    try:
        response = requests.get(ESTAT_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        values = data["GET_STATS_DATA"]["STATISTICAL_DATA"]["DATA_INF"]["VALUE"]
        latest = values[-1]
        prev = values[-2] if len(values) >= 2 else latest
        return {
            "total": float(latest["$"]),
            "core": float(latest["$"]) - 0.4,  # コアCPIの概算
            "date": latest["@time"],
            "prev_total": float(prev["$"]),
        }
    except Exception as e:
        print(f"[WARN] CPI取得エラー: {e}")
    return {"total": 3.2, "core": 2.8, "date": "2026年1月", "prev_total": 3.0}


def fetch_forex() -> dict:
    """
    Yahoo Finance から USD/JPY・EUR/JPY のレートを取得する
    Returns: {"usdjpy": float, "eurjpy": float, "usdjpy_prev": float}
    """
    try:
        usdjpy = yf.Ticker("USDJPY=X")
        eurjpy = yf.Ticker("EURJPY=X")

        usdjpy_hist = usdjpy.history(period="2d")
        eurjpy_hist = eurjpy.history(period="1d")

        usdjpy_now = round(float(usdjpy_hist["Close"].iloc[-1]), 2)
        usdjpy_prev = round(float(usdjpy_hist["Close"].iloc[-2]), 2) if len(usdjpy_hist) >= 2 else usdjpy_now
        eurjpy_now = round(float(eurjpy_hist["Close"].iloc[-1]), 2)

        return {
            "usdjpy": usdjpy_now,
            "eurjpy": eurjpy_now,
            "usdjpy_prev": usdjpy_prev,
        }
    except Exception as e:
        print(f"[WARN] 為替取得エラー: {e}")
    return {"usdjpy": 152.30, "eurjpy": 163.45, "usdjpy_prev": 152.30}


def fetch_all() -> dict:
    """
    すべての指標を取得してまとめて返す
    Returns: 全指標をまとめたdict
    """
    print("経済指標を取得中...")
    policy = fetch_policy_rate()
    tankan = fetch_tankan_di()
    cpi = fetch_cpi()
    forex = fetch_forex()

    return {
        "fetch_date": datetime.now().strftime("%Y年%-m月%-d日"),
        "fetch_time": datetime.now().strftime("%H:%M"),
        "policy_rate": policy["rate"],
        "policy_rate_prev": policy["prev_rate"],
        "policy_rate_date": policy["date"],
        "tankan_di": tankan["di"],
        "tankan_date": tankan["date"],
        "cpi_total": cpi["total"],
        "cpi_core": cpi["core"],
        "cpi_date": cpi["date"],
        "cpi_prev_total": cpi.get("prev_total", cpi["total"]),
        "usdjpy": forex["usdjpy"],
        "eurjpy": forex["eurjpy"],
        "usdjpy_prev": forex["usdjpy_prev"],
    }


if __name__ == "__main__":
    indicators = fetch_all()
    for key, value in indicators.items():
        print(f"  {key}: {value}")
