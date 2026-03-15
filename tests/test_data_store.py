"""
test_data_store.py
日次データ蓄積モジュールのテスト
"""

import csv
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

# src/ をモジュール検索パスに追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import data_store


@pytest.fixture
def tmp_csv(tmp_path):
    """テスト用の一時CSVパスを設定する"""
    csv_path = tmp_path / "test_indicators.csv"
    original_path = data_store.CSV_PATH
    data_store.CSV_PATH = csv_path
    yield csv_path
    data_store.CSV_PATH = original_path


DUMMY_DATA = {
    "fetch_weekday": "月",
    "usdjpy": 152.30,
    "eurjpy": 163.45,
    "usdjpy_prev": 151.80,
    "policy_rate": 0.50,
    "cpi_total": 3.2,
    "cpi_core": 2.8,
    "tankan_di": 12,
}


class TestSaveDaily:
    def test_creates_csv_with_header(self, tmp_csv):
        data_store.save_daily(DUMMY_DATA)
        assert tmp_csv.exists()
        with open(tmp_csv, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            assert header == data_store.CSV_COLUMNS

    def test_saves_one_row(self, tmp_csv):
        data_store.save_daily(DUMMY_DATA)
        with open(tmp_csv, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 1
        assert float(rows[0]["usdjpy"]) == 152.30
        assert rows[0]["weekday"] == "月"

    def test_no_duplicate_on_same_day(self, tmp_csv):
        data_store.save_daily(DUMMY_DATA)
        data_store.save_daily(DUMMY_DATA)
        with open(tmp_csv, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 1

    def test_appends_different_days(self, tmp_csv):
        data_store.save_daily(DUMMY_DATA)
        # 翌日を模擬（CSVに直接書き込み）
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        with open(tmp_csv, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data_store.CSV_COLUMNS)
            writer.writerow({
                "date": tomorrow, "weekday": "火",
                "usdjpy": 153.0, "eurjpy": 164.0, "usdjpy_prev": 152.30,
                "policy_rate": 0.50, "cpi_total": 3.2, "cpi_core": 2.8, "tankan_di": 12,
            })
        with open(tmp_csv, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 2


class TestLoadRecent:
    def test_returns_empty_if_no_file(self, tmp_csv):
        result = data_store.load_recent(5)
        assert result == []

    def test_returns_data_descending(self, tmp_csv):
        # 3日分のデータを作成
        with open(tmp_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data_store.CSV_COLUMNS)
            writer.writeheader()
            for i in range(3):
                d = (datetime.now() - timedelta(days=2 - i)).strftime("%Y-%m-%d")
                writer.writerow({
                    "date": d, "weekday": "月",
                    "usdjpy": 150 + i, "eurjpy": 160, "usdjpy_prev": 149 + i,
                    "policy_rate": 0.50, "cpi_total": 3.0, "cpi_core": 2.6, "tankan_di": 10,
                })
        result = data_store.load_recent(5)
        assert len(result) == 3
        # 降順で返る
        assert result[0]["date"] > result[1]["date"]

    def test_limits_to_n_days(self, tmp_csv):
        with open(tmp_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data_store.CSV_COLUMNS)
            writer.writeheader()
            for i in range(10):
                d = (datetime.now() - timedelta(days=9 - i)).strftime("%Y-%m-%d")
                writer.writerow({
                    "date": d, "weekday": "月",
                    "usdjpy": 150, "eurjpy": 160, "usdjpy_prev": 149,
                    "policy_rate": 0.50, "cpi_total": 3.0, "cpi_core": 2.6, "tankan_di": 10,
                })
        result = data_store.load_recent(3)
        assert len(result) == 3


class TestLoadWeekData:
    def test_returns_only_current_week(self, tmp_csv):
        # 月曜〜金曜のデータを作成（今週）
        now = datetime.now()
        monday = now - timedelta(days=now.weekday())

        with open(tmp_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data_store.CSV_COLUMNS)
            writer.writeheader()
            for i in range(5):
                d = (monday + timedelta(days=i)).strftime("%Y-%m-%d")
                writer.writerow({
                    "date": d, "weekday": ["月", "火", "水", "木", "金"][i],
                    "usdjpy": 150 + i, "eurjpy": 160, "usdjpy_prev": 149 + i,
                    "policy_rate": 0.50, "cpi_total": 3.0, "cpi_core": 2.6, "tankan_di": 10,
                })
            # 先週のデータも追加
            last_week = (monday - timedelta(days=3)).strftime("%Y-%m-%d")
            writer.writerow({
                "date": last_week, "weekday": "金",
                "usdjpy": 148, "eurjpy": 158, "usdjpy_prev": 147,
                "policy_rate": 0.50, "cpi_total": 3.0, "cpi_core": 2.6, "tankan_di": 10,
            })

        result = data_store.load_week_data(now)
        # 今週のデータだけが返る
        assert all(monday.strftime("%Y-%m-%d") <= r["date"] <= (monday + timedelta(days=4)).strftime("%Y-%m-%d") for r in result)

    def test_ascending_order(self, tmp_csv):
        now = datetime.now()
        monday = now - timedelta(days=now.weekday())
        with open(tmp_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data_store.CSV_COLUMNS)
            writer.writeheader()
            for i in range(3):
                d = (monday + timedelta(days=i)).strftime("%Y-%m-%d")
                writer.writerow({
                    "date": d, "weekday": ["月", "火", "水"][i],
                    "usdjpy": 150 + i, "eurjpy": 160, "usdjpy_prev": 149,
                    "policy_rate": 0.50, "cpi_total": 3.0, "cpi_core": 2.6, "tankan_di": 10,
                })
        result = data_store.load_week_data(now)
        assert len(result) >= 1
        if len(result) > 1:
            assert result[0]["date"] < result[-1]["date"]

    def test_empty_if_no_file(self, tmp_csv):
        result = data_store.load_week_data()
        assert result == []


class TestNumericConversion:
    def test_load_recent_converts_types(self, tmp_csv):
        with open(tmp_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data_store.CSV_COLUMNS)
            writer.writeheader()
            writer.writerow({
                "date": datetime.now().strftime("%Y-%m-%d"), "weekday": "月",
                "usdjpy": "152.30", "eurjpy": "163.45", "usdjpy_prev": "151.80",
                "policy_rate": "0.50", "cpi_total": "3.2", "cpi_core": "2.8", "tankan_di": "12",
            })
        result = data_store.load_recent(1)
        assert isinstance(result[0]["usdjpy"], float)
        assert isinstance(result[0]["tankan_di"], int)
