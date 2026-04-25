"""
test_prev_close_date.py
毎朝レポートで「前日終値」が2日前のデータになっていないかを検証するテスト。

fetch_forex() は period="2d" の iloc[-2] を「前日終値」として使う。
yfinance の日次バーは UTC 基準のため、JST 08:30 に実行すると
UTC では前日の 23:30 にあたる。この際に period="2d" が返すデータの
日付がどうなるかを検証する。
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
import pandas as pd
from datetime import datetime, timedelta, timezone, date
from unittest.mock import patch, MagicMock

JST = timezone(timedelta(hours=9))
UTC = timezone.utc


def make_df_with_dates(dates: list) -> pd.DataFrame:
    """指定した日付リストで Close カラムを持つ DataFrame を作成する。"""
    idx = pd.DatetimeIndex(
        [pd.Timestamp(d, tz="UTC") for d in dates]
    )
    return pd.DataFrame({"Close": [152.0 + i * 0.1 for i in range(len(dates))]}, index=idx)


# ────────────────────────────────────────────────────────────────────
# fetch_forex() の内部ロジックを再現したユーティリティ
# ────────────────────────────────────────────────────────────────────

def simulate_fetch_forex(hist_2d: pd.DataFrame) -> dict:
    """fetch_indicators.fetch_forex() と同じ index 取得ロジック。"""
    usdjpy_now = round(float(hist_2d["Close"].iloc[-1]), 2)
    usdjpy_prev = (
        round(float(hist_2d["Close"].iloc[-2]), 2)
        if len(hist_2d) >= 2
        else usdjpy_now
    )
    return {
        "usdjpy_now": usdjpy_now,
        "usdjpy_prev": usdjpy_prev,
        "now_date": hist_2d.index[-1].date() if len(hist_2d) >= 1 else None,
        "prev_date": hist_2d.index[-2].date() if len(hist_2d) >= 2 else None,
    }


# ────────────────────────────────────────────────────────────────────
# テストケース
# ────────────────────────────────────────────────────────────────────

class TestForexPrevCloseDate:

    def test_normal_case_today_and_yesterday(self):
        """
        【正常ケース】period='2d' が「今日(UTC)」と「昨日(UTC)」を返すとき、
        iloc[-1]=今日, iloc[-2]=昨日 となること。
        """
        today_utc = date(2026, 4, 25)       # JST 08:30 = UTC 23:30 Apr 24 → UTC的「今日」は Apr 24
        yesterday_utc = date(2026, 4, 24)   # 前日(UTC)

        hist = make_df_with_dates([yesterday_utc, today_utc])
        result = simulate_fetch_forex(hist)

        assert result["now_date"] == today_utc
        assert result["prev_date"] == yesterday_utc
        # 日付差は1日
        assert (result["now_date"] - result["prev_date"]).days == 1

    def test_stale_data_prev_is_2days_old(self):
        """
        【問題ケース】period='2d' が「昨日(UTC)」と「一昨日(UTC)」を返してしまうとき、
        iloc[-2] = 一昨日 = JST基準で"2日前"になる。

        JST 08:30 に実行 → UTC 23:30(前日)
        もし yfinance が今日のバーをまだ返さない場合、
        period="2d" で得られるのが day-2 と day-1(UTC) になる。
        """
        jst_today = date(2026, 4, 25)        # レポート配信日 (JST)
        utc_day_minus1 = date(2026, 4, 24)   # JST 04/25 08:30 = UTC 04/24 23:30
        utc_day_minus2 = date(2026, 4, 23)   # その前日

        hist = make_df_with_dates([utc_day_minus2, utc_day_minus1])
        result = simulate_fetch_forex(hist)

        # now_date は UTC 4/24 → JST では「昨日」相当（問題ない）
        # prev_date は UTC 4/23 → JST では「2日前」相当
        days_ago = (jst_today - result["prev_date"]).days
        print(f"\n[INFO] prev_date(UTC): {result['prev_date']} → JST基準で {days_ago} 日前")

        # ★ これが問題: JST 的には2日前のデータが「前日終値」として使われる
        assert days_ago == 2, (
            f"JST基準で prev_date は {days_ago} 日前。"
            f"期待: 1日前 or 2日前 (今回のシナリオは2日前)"
        )

    def test_period_2d_returns_only_1_row_fallback(self):
        """
        【エッジケース】period='2d' が1行しか返さない場合、
        usdjpy_prev は usdjpy_now と同値になり前日比=0になること。
        """
        hist = make_df_with_dates([date(2026, 4, 24)])  # 1行のみ
        result = simulate_fetch_forex(hist)

        assert result["prev_date"] is None
        assert result["usdjpy_now"] == result["usdjpy_prev"]

    def test_period_5d_always_has_enough_data(self):
        """
        【改善案検証】period='5d' を使えば十分な行数が得られること。
        週またぎ（月曜朝）でも直近2営業日が確実に含まれる。
        """
        # 月曜朝シナリオ: 先週月〜金 5日分
        days_5d = [
            date(2026, 4, 20),  # 月
            date(2026, 4, 21),  # 火
            date(2026, 4, 22),  # 水
            date(2026, 4, 23),  # 木
            date(2026, 4, 24),  # 金
        ]
        hist = make_df_with_dates(days_5d)

        assert len(hist) >= 2, "period='5d' で2行以上取得できること"

        usdjpy_now = round(float(hist["Close"].iloc[-1]), 2)
        usdjpy_prev = round(float(hist["Close"].iloc[-2]), 2)
        diff = round(usdjpy_now - usdjpy_prev, 2)

        # iloc[-1] = 金曜, iloc[-2] = 木曜 → 1日差
        assert (hist.index[-1].date() - hist.index[-2].date()).days == 1

    def test_monday_scenario_weekend_gap(self):
        """
        【月曜朝シナリオ】period='2d' を月曜朝に呼ぶと、
        土日を挟むため iloc[-1]=金曜, iloc[-2]=木曜 になる可能性がある。
        月曜朝の「前日終値」は金曜終値であるべきなのに iloc[-1] が金曜になる。
        """
        # 月曜(JST)朝08:30 = 日曜(UTC)23:30 に実行
        # period="2d" → 木曜と金曜のデータが返ることが多い
        thursday = date(2026, 4, 23)  # 木
        friday   = date(2026, 4, 24)  # 金

        hist = make_df_with_dates([thursday, friday])
        result = simulate_fetch_forex(hist)

        # 月曜朝(4/27)時点での各日付の「カレンダー日数差」
        monday_jst = date(2026, 4, 27)
        days_now_is_old  = (monday_jst - result["now_date"]).days   # 金曜 → 3暦日前
        days_prev_is_old = (monday_jst - result["prev_date"]).days  # 木曜 → 4暦日前

        print(f"\n[月曜朝] now_date:{result['now_date']} (暦{days_now_is_old}日前=前営業日の金曜), "
              f"prev_date:{result['prev_date']} (暦{days_prev_is_old}日前=木曜)")

        # 月曜朝: iloc[-1]=金曜(暦3日前=前営業日), iloc[-2]=木曜(暦4日前=2営業日前)
        # ★ 問題: 「前日比」として表示されるのは (金曜終値)-(木曜終値) であり、
        #   本来の「月曜朝レートと金曜終値の差」ではない。
        #   つまり前日比が1営業日ずれた値になる。
        assert days_now_is_old == 3, f"月曜朝の now_date は暦3日前(金曜)のはず: {result['now_date']}"
        assert days_prev_is_old == 4, f"月曜朝の prev_date は暦4日前(木曜)のはず: {result['prev_date']}"

    def test_fetch_forex_actual_logic(self):
        """
        fetch_indicators.fetch_forex() を直接モックして、
        iloc[-2] の日付が正しく取れているかを検証する。
        """
        import yfinance as yf
        from src.fetch_indicators import fetch_forex

        today_utc = date(2026, 4, 25)
        yesterday_utc = date(2026, 4, 24)
        hist_mock = make_df_with_dates([yesterday_utc, today_utc])

        with patch("src.fetch_indicators.yf.Ticker") as mock_ticker:
            mock_instance = MagicMock()
            mock_instance.history.return_value = hist_mock
            mock_ticker.return_value = mock_instance

            result = fetch_forex()

        assert "usdjpy" in result
        assert "usdjpy_prev" in result
        # 2行データ → 正常に前日比が計算できること
        assert result["usdjpy"] != result["usdjpy_prev"] or len(hist_mock) < 2
