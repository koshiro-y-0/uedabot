"""
test_glossary.py
経済用語解説機能のテスト
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from generate_glossary import (
    GLOSSARY,
    GLOSSARY_ALIASES,
    parse_glossary_command,
    generate_glossary_list,
    generate_glossary_report,
)


class TestParseGlossaryCommand:
    def test_cpi(self):
        assert parse_glossary_command("解説:CPI") == "CPI"

    def test_cpi_fullwidth_colon(self):
        assert parse_glossary_command("解説：CPI") == "CPI"

    def test_tankan(self):
        assert parse_glossary_command("解説:短観") == "短観"

    def test_policy_rate(self):
        assert parse_glossary_command("解説:政策金利") == "政策金利"

    def test_forex(self):
        assert parse_glossary_command("解説:為替") == "為替"

    def test_gdp(self):
        assert parse_glossary_command("解説:GDP") == "GDP"

    def test_boj(self):
        assert parse_glossary_command("解説:日銀") == "日銀"

    def test_list(self):
        assert parse_glossary_command("解説:一覧") == "一覧"

    def test_alias_kinri(self):
        assert parse_glossary_command("解説:金利") == "政策金利"

    def test_alias_boj_english(self):
        assert parse_glossary_command("解説:BOJ") == "日銀"

    def test_alias_lowercase(self):
        assert parse_glossary_command("解説:cpi") == "CPI"

    def test_unknown_term(self):
        assert parse_glossary_command("解説:不明") is None

    def test_not_glossary_command(self):
        assert parse_glossary_command("詳細:為替") is None

    def test_empty_text(self):
        assert parse_glossary_command("") is None


class TestGenerateGlossaryList:
    def test_contains_all_terms(self):
        result = generate_glossary_list()
        for key in GLOSSARY:
            assert key in result

    def test_contains_header(self):
        result = generate_glossary_list()
        assert "経済用語解説" in result

    def test_contains_usage_hint(self):
        result = generate_glossary_list()
        assert "解説:CPI" in result


class TestGenerateGlossaryReport:
    def test_cpi_report(self):
        report = generate_glossary_report("CPI")
        assert "消費者物価指数" in report
        assert "コアCPI" in report
        assert "物価の安定" in report

    def test_tankan_report(self):
        report = generate_glossary_report("短観")
        assert "日銀短観" in report
        assert "DI" in report

    def test_policy_rate_report(self):
        report = generate_glossary_report("政策金利")
        assert "無担保コール翌日物" in report
        assert "金融政策決定会合" in report

    def test_forex_report(self):
        report = generate_glossary_report("為替")
        assert "円安" in report
        assert "円高" in report

    def test_gdp_report(self):
        report = generate_glossary_report("GDP")
        assert "国内総生産" in report
        assert "実質" in report

    def test_boj_report(self):
        report = generate_glossary_report("日銀")
        assert "中央銀行" in report
        assert "日本銀行券" in report

    def test_unknown_key(self):
        report = generate_glossary_report("不明")
        assert "未対応" in report
        assert "解説:一覧" in report

    def test_all_reports_have_quote(self):
        for key in GLOSSARY:
            report = generate_glossary_report(key)
            assert "━━━" in report
            assert "「" in report
