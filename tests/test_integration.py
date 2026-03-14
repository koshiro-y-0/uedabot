"""
test_integration.py
Webhook → 詳細取得 → Reply の一連フローを結合テストする
"""

import json
import hashlib
import hmac
import base64
import pytest
from unittest.mock import patch, MagicMock

from api.webhook import handle_webhook_event, verify_signature
from src.generate_detail import generate_detail_report, parse_detail_command
from src.fetch_detail import fetch_detail, DETAIL_FETCHERS


class TestEndToEndFlow:
    """Quick Reply → Webhook → 詳細レポート → Reply の結合テスト"""

    CATEGORIES = ["為替", "金利", "CPI", "短観", "注目"]

    @pytest.mark.parametrize("category", CATEGORIES)
    def test_full_flow_per_category(self, category):
        """各カテゴリで fetch → generate → reply の一連フローが通ること"""
        # 1. コマンド解析
        command = f"詳細:{category}"
        parsed = parse_detail_command(command)
        assert parsed == category

        # 2. データ取得
        data = fetch_detail(category)
        assert isinstance(data, dict)
        assert len(data) > 0

        # 3. レポート生成
        report = generate_detail_report(category)
        assert isinstance(report, str)
        assert len(report) > 50  # 意味のある長さのレポートが生成されること

    @pytest.mark.parametrize("category", CATEGORIES)
    @patch("api.webhook.reply_message", return_value=True)
    def test_webhook_event_triggers_reply_per_category(self, mock_reply, category):
        """Webhookイベントが各カテゴリの詳細レポートをReplyすること"""
        event = {
            "type": "message",
            "message": {"type": "text", "text": f"詳細:{category}"},
            "replyToken": "test_token_123",
        }
        handle_webhook_event(event)
        mock_reply.assert_called_once()
        reply_text = mock_reply.call_args[0][1]
        assert len(reply_text) > 50

    def test_report_contains_no_template_errors(self):
        """全レポートにJinja2のテンプレートエラーが含まれないこと"""
        for category in self.CATEGORIES:
            report = generate_detail_report(category)
            assert "{{" not in report, f"{category}レポートに未解決テンプレート変数あり"
            assert "}}" not in report, f"{category}レポートに未解決テンプレート変数あり"
            assert "Undefined" not in report, f"{category}レポートにUndefinedエラーあり"

    def test_all_reports_have_date(self):
        """全レポートに日付が含まれること"""
        for category in self.CATEGORIES:
            report = generate_detail_report(category)
            assert "年" in report and "月" in report, f"{category}レポートに日付がない"

    def test_fullwidth_colon_also_works(self):
        """全角コロンでもコマンド解析が動作すること"""
        for category in self.CATEGORIES:
            parsed = parse_detail_command(f"詳細：{category}")
            assert parsed == category


class TestSignatureVerification:
    """署名検証の結合テスト"""

    @patch("api.webhook.LINE_CHANNEL_SECRET", "integration_test_secret")
    def test_valid_request_flow(self):
        """正しい署名 → 検証通過"""
        body = json.dumps({"events": [{"type": "follow"}]})
        hash_value = hmac.new(
            b"integration_test_secret", body.encode("utf-8"), hashlib.sha256
        ).digest()
        signature = base64.b64encode(hash_value).decode("utf-8")
        assert verify_signature(body, signature) is True

    @patch("api.webhook.LINE_CHANNEL_SECRET", "integration_test_secret")
    def test_tampered_body_fails(self):
        """改ざんされたbody → 検証失敗"""
        body = json.dumps({"events": []})
        hash_value = hmac.new(
            b"integration_test_secret", body.encode("utf-8"), hashlib.sha256
        ).digest()
        signature = base64.b64encode(hash_value).decode("utf-8")
        # bodyを改ざん
        assert verify_signature(body + "tampered", signature) is False
