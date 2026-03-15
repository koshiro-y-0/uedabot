"""
test_forex_alert.py
為替アラート機能のテスト
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from forex_alert import (
    DEFAULT_THRESHOLD,
    check_alert,
    generate_alert_message,
    get_current_usdjpy,
    get_last_rate,
)


class TestCheckAlert:
    def test_no_alert_within_threshold(self):
        result = check_alert(152.30, 151.50)
        assert result is None

    def test_alert_yen_weak(self):
        result = check_alert(154.50, 152.00)
        assert result is not None
        assert result["direction"] == "円安"
        assert result["diff"] == pytest.approx(2.50)

    def test_alert_yen_strong(self):
        result = check_alert(149.50, 152.00)
        assert result is not None
        assert result["direction"] == "円高"
        assert result["diff"] == pytest.approx(-2.50)

    def test_exact_threshold_no_alert(self):
        # ちょうど閾値の場合はアラートなし（< threshold）
        result = check_alert(154.00, 152.00)
        assert result is None

    def test_just_over_threshold(self):
        result = check_alert(154.01, 152.00)
        assert result is not None

    def test_custom_threshold(self):
        # カスタム閾値 1.0円
        result = check_alert(153.10, 152.00, threshold=1.0)
        assert result is not None
        assert result["threshold"] == 1.0

    def test_custom_threshold_no_alert(self):
        result = check_alert(152.80, 152.00, threshold=1.0)
        assert result is None

    def test_env_threshold(self):
        with patch.dict(os.environ, {"FOREX_ALERT_THRESHOLD": "3.0"}):
            result = check_alert(154.50, 152.00)
            assert result is None  # 差2.5 < 閾値3.0

    def test_alert_contains_pct(self):
        result = check_alert(155.00, 150.00)
        assert result is not None
        assert abs(result["pct"] - 3.33) < 0.1

    def test_alert_contains_timestamp(self):
        result = check_alert(155.00, 150.00)
        assert "年" in result["timestamp"]
        assert "月" in result["timestamp"]


class TestGenerateAlertMessage:
    def test_contains_key_elements(self):
        alert = check_alert(155.00, 152.00)
        msg = generate_alert_message(alert)
        assert "為替アラート" in msg
        assert "155.00" in msg
        assert "152.00" in msg
        assert "円安" in msg

    def test_yen_strong_message(self):
        alert = check_alert(148.00, 152.00)
        msg = generate_alert_message(alert)
        assert "円高" in msg
        assert "148.00" in msg

    def test_contains_ueda_quote(self):
        alert = check_alert(155.00, 152.00)
        msg = generate_alert_message(alert)
        assert "適切に対応" in msg


class TestGetCurrentUsdjpy:
    @patch("forex_alert.yf.Ticker")
    def test_returns_float(self, mock_ticker):
        mock_hist = MagicMock()
        mock_hist.empty = False
        mock_hist.__getitem__ = lambda self, key: MagicMock(iloc=MagicMock(__getitem__=lambda s, i: 152.50))
        mock_ticker.return_value.history.return_value = mock_hist
        result = get_current_usdjpy()
        assert result == 152.50

    @patch("forex_alert.yf.Ticker")
    def test_returns_none_on_error(self, mock_ticker):
        mock_ticker.side_effect = Exception("API error")
        result = get_current_usdjpy()
        assert result is None


class TestGetLastRate:
    @patch("data_store.load_recent")
    def test_returns_rate(self, mock_load):
        mock_load.return_value = [{"usdjpy": 151.50, "date": "2026-03-14"}]
        result = get_last_rate()
        assert result == 151.50

    @patch("data_store.load_recent")
    def test_returns_none_when_empty(self, mock_load):
        mock_load.return_value = []
        result = get_last_rate()
        assert result is None


class TestDefaultThreshold:
    def test_default_value(self):
        assert DEFAULT_THRESHOLD == 2.0
