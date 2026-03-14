"""
test_detail.py
詳細データ取得・レポート生成のテスト
"""

import pytest
from src.fetch_detail import fetch_detail, DETAIL_FETCHERS
from src.generate_detail import generate_detail_report, parse_detail_command


class TestFetchDetail:
    """fetch_detail のテスト"""

    def test_fetch_forex_detail_returns_expected_keys(self):
        data = fetch_detail("為替")
        expected_keys = [
            "usdjpy", "usdjpy_diff", "usdjpy_diff_pct",
            "usdjpy_week_high", "usdjpy_week_low", "usdjpy_5d",
            "eurjpy", "eurjpy_diff", "trend",
            "fetch_date", "fetch_weekday", "fetch_time",
        ]
        for key in expected_keys:
            assert key in data, f"キー '{key}' が為替詳細データに含まれていません"

    def test_fetch_rate_detail_returns_expected_keys(self):
        data = fetch_detail("金利")
        assert "current_rate" in data
        assert "rate_history" in data
        assert "next_meetings" in data
        assert len(data["rate_history"]) > 0

    def test_fetch_cpi_detail_returns_expected_keys(self):
        data = fetch_detail("CPI")
        assert "cpi_total" in data
        assert "cpi_core" in data
        assert "cpi_core_core" in data
        assert "cpi_mom_change" in data

    def test_fetch_tankan_detail_returns_expected_keys(self):
        data = fetch_detail("短観")
        assert "mfg_di" in data
        assert "non_mfg_di" in data
        assert "mfg_outlook_di" in data
        assert "tankan_date" in data

    def test_fetch_events_detail_returns_events(self):
        data = fetch_detail("注目")
        assert "events" in data
        assert len(data["events"]) > 0
        assert "date" in data["events"][0]
        assert "event" in data["events"][0]

    def test_fetch_detail_invalid_category_raises(self):
        with pytest.raises(ValueError, match="不明なカテゴリ"):
            fetch_detail("存在しない")

    def test_all_categories_covered(self):
        """全カテゴリが DETAIL_FETCHERS に登録されていることを確認"""
        expected = {"為替", "金利", "CPI", "短観", "注目"}
        assert set(DETAIL_FETCHERS.keys()) == expected


class TestGenerateDetailReport:
    """generate_detail_report のテスト"""

    def test_forex_report_contains_usdjpy(self):
        report = generate_detail_report("為替")
        assert "USD/JPY" in report
        assert "EUR/JPY" in report
        assert "トレンド判定" in report

    def test_rate_report_contains_policy_rate(self):
        report = generate_detail_report("金利")
        assert "政策金利" in report
        assert "会合" in report

    def test_cpi_report_contains_cpi(self):
        report = generate_detail_report("CPI")
        assert "CPI" in report
        assert "コア" in report

    def test_tankan_report_contains_di(self):
        report = generate_detail_report("短観")
        assert "製造業" in report
        assert "非製造業" in report

    def test_events_report_contains_events(self):
        report = generate_detail_report("注目")
        assert "イベント" in report

    def test_invalid_category_returns_error_message(self):
        report = generate_detail_report("存在しない")
        assert "不明なカテゴリ" in report


class TestParseDetailCommand:
    """parse_detail_command のテスト"""

    def test_parse_valid_commands(self):
        assert parse_detail_command("詳細:為替") == "為替"
        assert parse_detail_command("詳細:金利") == "金利"
        assert parse_detail_command("詳細:CPI") == "CPI"
        assert parse_detail_command("詳細:短観") == "短観"
        assert parse_detail_command("詳細:注目") == "注目"

    def test_parse_fullwidth_colon(self):
        assert parse_detail_command("詳細：為替") == "為替"

    def test_parse_invalid_returns_none(self):
        assert parse_detail_command("こんにちは") is None
        assert parse_detail_command("詳細:不明") is None
        assert parse_detail_command("") is None
