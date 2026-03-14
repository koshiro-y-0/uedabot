"""
test_webhook.py
Webhook の署名検証・イベント処理のテスト
"""

import hashlib
import hmac
import base64
import pytest
from unittest.mock import patch, MagicMock

from api.webhook import verify_signature, handle_webhook_event


class TestVerifySignature:
    """署名検証のテスト"""

    @patch("api.webhook.LINE_CHANNEL_SECRET", "test_secret")
    def test_valid_signature(self):
        body = '{"events":[]}'
        # 正しい署名を生成
        hash_value = hmac.new(
            b"test_secret", body.encode("utf-8"), hashlib.sha256
        ).digest()
        signature = base64.b64encode(hash_value).decode("utf-8")
        assert verify_signature(body, signature) is True

    @patch("api.webhook.LINE_CHANNEL_SECRET", "test_secret")
    def test_invalid_signature(self):
        body = '{"events":[]}'
        assert verify_signature(body, "invalid_signature") is False

    @patch("api.webhook.LINE_CHANNEL_SECRET", "")
    def test_empty_secret_returns_false(self):
        assert verify_signature("body", "sig") is False


class TestHandleWebhookEvent:
    """イベント処理のテスト"""

    @patch("api.webhook.reply_message")
    @patch("api.webhook.generate_detail_report")
    @patch("api.webhook.parse_detail_command", return_value="為替")
    def test_detail_command_triggers_reply(self, mock_parse, mock_gen, mock_reply):
        mock_gen.return_value = "為替詳細レポート"
        event = {
            "type": "message",
            "message": {"type": "text", "text": "詳細:為替"},
            "replyToken": "test_token",
        }
        handle_webhook_event(event)
        mock_gen.assert_called_once_with("為替")
        mock_reply.assert_called_once_with("test_token", "為替詳細レポート")

    @patch("api.webhook.reply_message")
    @patch("api.webhook.parse_detail_command", return_value=None)
    def test_non_detail_message_ignored(self, mock_parse, mock_reply):
        event = {
            "type": "message",
            "message": {"type": "text", "text": "こんにちは"},
            "replyToken": "test_token",
        }
        handle_webhook_event(event)
        mock_reply.assert_not_called()

    @patch("api.webhook.reply_message")
    def test_non_message_event_ignored(self, mock_reply):
        event = {"type": "follow", "replyToken": "test_token"}
        handle_webhook_event(event)
        mock_reply.assert_not_called()

    @patch("api.webhook.reply_message")
    def test_non_text_message_ignored(self, mock_reply):
        event = {
            "type": "message",
            "message": {"type": "image"},
            "replyToken": "test_token",
        }
        handle_webhook_event(event)
        mock_reply.assert_not_called()

    @patch("api.webhook.reply_message")
    @patch("api.webhook.generate_detail_report", side_effect=Exception("API error"))
    @patch("api.webhook.parse_detail_command", return_value="為替")
    def test_error_sends_error_message(self, mock_parse, mock_gen, mock_reply):
        event = {
            "type": "message",
            "message": {"type": "text", "text": "詳細:為替"},
            "replyToken": "test_token",
        }
        handle_webhook_event(event)
        mock_reply.assert_called_once()
        call_args = mock_reply.call_args[0]
        assert "エラー" in call_args[1]
