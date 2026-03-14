"""
test_fetch.py
fetch_indicators.py のユニットテスト
"""

import pytest
from unittest.mock import patch, MagicMock
from src.fetch_indicators import fetch_forex, fetch_cpi, fetch_policy_rate, fetch_all


def test_fetch_policy_rate_returns_expected_keys():
    """政策金利取得がrate, date, prev_rateキーを返すこと"""
    with patch("src.fetch_indicators.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {
            "items": [
                {"value": "0.50", "date": "2026-01"},
                {"value": "0.25", "date": "2025-12"},
            ]
        }
        mock_get.return_value.raise_for_status = MagicMock()
        result = fetch_policy_rate()
    assert "rate" in result
    assert "prev_rate" in result
    assert result["rate"] == 0.50
    assert result["prev_rate"] == 0.25


def test_fetch_forex_returns_expected_keys():
    """為替取得がusdjpy, eurjpy, usdjpy_prevキーを返すこと"""
    with patch("src.fetch_indicators.yf.Ticker") as mock_ticker:
        import pandas as pd
        mock_hist = pd.DataFrame({"Close": [152.00, 152.30]})
        mock_ticker.return_value.history.return_value = mock_hist
        result = fetch_forex()
    assert "usdjpy" in result
    assert "eurjpy" in result
    assert "usdjpy_prev" in result


def test_fetch_all_returns_all_keys():
    """fetch_all がすべての必須キーを含むdictを返すこと"""
    with patch("src.fetch_indicators.fetch_policy_rate") as mock_policy, \
         patch("src.fetch_indicators.fetch_tankan_di") as mock_tankan, \
         patch("src.fetch_indicators.fetch_cpi") as mock_cpi, \
         patch("src.fetch_indicators.fetch_forex") as mock_forex:

        mock_policy.return_value = {"rate": 0.50, "date": "2026-01", "prev_rate": 0.50}
        mock_tankan.return_value = {"di": 12, "date": "2025-Q4"}
        mock_cpi.return_value = {"total": 3.2, "core": 2.8, "date": "2026年1月", "prev_total": 3.0}
        mock_forex.return_value = {"usdjpy": 152.30, "eurjpy": 163.45, "usdjpy_prev": 151.80}

        result = fetch_all()

    required_keys = [
        "fetch_date", "fetch_time",
        "policy_rate", "policy_rate_prev",
        "cpi_total", "cpi_core",
        "tankan_di",
        "usdjpy", "eurjpy", "usdjpy_prev",
    ]
    for key in required_keys:
        assert key in result, f"Missing key: {key}"


def test_fetch_cpi_without_api_key_returns_fallback(monkeypatch):
    """ESTAT_API_KEYが未設定でもフォールバック値を返すこと"""
    monkeypatch.setattr("src.fetch_indicators.ESTAT_API_KEY", None)
    result = fetch_cpi()
    assert result["total"] > 0
    assert result["core"] > 0
