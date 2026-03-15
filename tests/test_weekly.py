"""
test_weekly.py
週間サマリー・チャート生成のテスト
"""

import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from generate_weekly import build_weekly_summary, generate_weekly_report, _determine_weekly_comment
from generate_chart import generate_forex_chart

DUMMY_WEEK = [
    {"date": "2026-03-09", "weekday": "月", "usdjpy": 151.20, "eurjpy": 162.0, "usdjpy_prev": 150.80, "policy_rate": 0.50, "cpi_total": 3.2, "cpi_core": 2.8, "tankan_di": 12},
    {"date": "2026-03-10", "weekday": "火", "usdjpy": 150.90, "eurjpy": 161.5, "usdjpy_prev": 151.20, "policy_rate": 0.50, "cpi_total": 3.2, "cpi_core": 2.8, "tankan_di": 12},
    {"date": "2026-03-11", "weekday": "水", "usdjpy": 153.50, "eurjpy": 164.0, "usdjpy_prev": 150.90, "policy_rate": 0.50, "cpi_total": 3.2, "cpi_core": 2.8, "tankan_di": 12},
    {"date": "2026-03-12", "weekday": "木", "usdjpy": 152.10, "eurjpy": 163.2, "usdjpy_prev": 153.50, "policy_rate": 0.50, "cpi_total": 3.2, "cpi_core": 2.8, "tankan_di": 12},
    {"date": "2026-03-13", "weekday": "金", "usdjpy": 152.80, "eurjpy": 163.8, "usdjpy_prev": 152.10, "policy_rate": 0.50, "cpi_total": 3.2, "cpi_core": 2.8, "tankan_di": 12},
]


class TestBuildWeeklySummary:
    def test_has_data_true(self):
        result = build_weekly_summary(DUMMY_WEEK)
        assert result["has_data"] is True

    def test_empty_data(self):
        result = build_weekly_summary([])
        assert result["has_data"] is False

    def test_usdjpy_values(self):
        result = build_weekly_summary(DUMMY_WEEK)
        assert result["usdjpy_open"] == 151.20
        assert result["usdjpy_close"] == 152.80

    def test_week_change(self):
        result = build_weekly_summary(DUMMY_WEEK)
        assert abs(result["week_change"] - 1.60) < 0.01

    def test_high_low(self):
        result = build_weekly_summary(DUMMY_WEEK)
        assert result["usdjpy_high"] == 153.50
        assert result["usdjpy_low"] == 150.90

    def test_policy_rate_from_latest(self):
        result = build_weekly_summary(DUMMY_WEEK)
        assert result["policy_rate"] == 0.50

    def test_week_start_end_display(self):
        result = build_weekly_summary(DUMMY_WEEK)
        assert "3月9日" in result["week_start"]
        assert "3月13日" in result["week_end"]


class TestWeeklyComment:
    def test_stable(self):
        comment = _determine_weekly_comment(0.5, 1.0)
        assert "安定" in comment

    def test_yen_weak(self):
        comment = _determine_weekly_comment(2.0, 2.0)
        assert "円安" in comment

    def test_yen_strong(self):
        comment = _determine_weekly_comment(-2.0, 2.0)
        assert "円高" in comment

    def test_volatile(self):
        comment = _determine_weekly_comment(0.5, 4.0)
        assert "変動" in comment


class TestGenerateWeeklyReport:
    def test_report_contains_key_elements(self):
        report = generate_weekly_report(DUMMY_WEEK)
        assert "週間サマリー" in report
        assert "USD/JPY" in report
        assert "151.20" in report
        assert "152.80" in report

    def test_empty_data_report(self):
        report = generate_weekly_report([])
        assert "データがまだ蓄積されていません" in report


class TestGenerateChart:
    def test_generates_png_file(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            output = f.name
        try:
            result = generate_forex_chart(DUMMY_WEEK, output)
            assert result == output
            assert os.path.exists(output)
            assert os.path.getsize(output) > 0
        finally:
            os.unlink(output)

    def test_empty_data_returns_empty(self):
        result = generate_forex_chart([])
        assert result == ""

    def test_single_day_data(self):
        single = [DUMMY_WEEK[0]]
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            output = f.name
        try:
            result = generate_forex_chart(single, output)
            assert os.path.exists(output)
        finally:
            os.unlink(output)
