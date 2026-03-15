"""
test_richmenu.py
リッチメニュー生成のテスト
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from generate_richmenu import (
    MENU_BUTTONS,
    WIDTH,
    HEIGHT,
    HALF_W,
    HALF_H,
    generate_richmenu_image,
    build_richmenu_object,
    register_richmenu,
)


class TestMenuButtons:
    def test_six_buttons(self):
        assert len(MENU_BUTTONS) == 6

    def test_all_buttons_have_required_keys(self):
        for btn in MENU_BUTTONS:
            assert "label" in btn
            assert "text" in btn
            assert "row" in btn
            assert "col" in btn

    def test_button_texts(self):
        texts = [btn["text"] for btn in MENU_BUTTONS]
        assert "詳細:為替" in texts
        assert "詳細:金利" in texts
        assert "詳細:CPI" in texts
        assert "詳細:短観" in texts
        assert "解説:一覧" in texts
        assert "詳細:注目" in texts


class TestGenerateImage:
    def test_generates_png_file(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            output = f.name
        try:
            result = generate_richmenu_image(output)
            assert result == output
            assert os.path.exists(output)
            assert os.path.getsize(output) > 0
        finally:
            os.unlink(output)

    def test_image_dimensions(self):
        from PIL import Image
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            output = f.name
        try:
            generate_richmenu_image(output)
            img = Image.open(output)
            assert img.size == (WIDTH, HEIGHT)
        finally:
            os.unlink(output)


class TestBuildRichmenuObject:
    def test_has_required_fields(self):
        obj = build_richmenu_object()
        assert "size" in obj
        assert "areas" in obj
        assert "name" in obj
        assert "chatBarText" in obj

    def test_size(self):
        obj = build_richmenu_object()
        assert obj["size"]["width"] == WIDTH
        assert obj["size"]["height"] == HEIGHT

    def test_six_areas(self):
        obj = build_richmenu_object()
        assert len(obj["areas"]) == 6

    def test_area_bounds(self):
        obj = build_richmenu_object()
        for area in obj["areas"]:
            bounds = area["bounds"]
            assert bounds["width"] == HALF_W
            assert bounds["height"] == HALF_H
            assert bounds["x"] >= 0
            assert bounds["y"] >= 0

    def test_area_actions(self):
        obj = build_richmenu_object()
        for area in obj["areas"]:
            assert area["action"]["type"] == "message"
            assert len(area["action"]["text"]) > 0

    def test_selected_true(self):
        obj = build_richmenu_object()
        assert obj["selected"] is True


class TestRegisterRichmenu:
    def test_no_token_returns_none(self):
        with patch.dict(os.environ, {}, clear=True):
            result = register_richmenu()
            assert result is None

    @patch("generate_richmenu.requests.post")
    @patch("generate_richmenu.generate_richmenu_image")
    def test_successful_registration(self, mock_image, mock_post):
        mock_image.return_value = "/tmp/test_richmenu.png"

        # モックファイルを作成
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"fake png data")
            mock_image.return_value = f.name

        # 3回のAPI呼び出しをモック
        mock_resp1 = MagicMock()
        mock_resp1.status_code = 200
        mock_resp1.json.return_value = {"richMenuId": "richmenu-test-id"}

        mock_resp2 = MagicMock()
        mock_resp2.status_code = 200

        mock_resp3 = MagicMock()
        mock_resp3.status_code = 200

        mock_post.side_effect = [mock_resp1, mock_resp2, mock_resp3]

        with patch.dict(os.environ, {"LINE_CHANNEL_TOKEN": "test-token"}):
            result = register_richmenu()

        assert result == "richmenu-test-id"
        assert mock_post.call_count == 3

        # テスト用ファイル削除
        os.unlink(f.name)

    @patch("generate_richmenu.requests.post")
    def test_create_menu_fails(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_resp.text = "Bad Request"
        mock_post.return_value = mock_resp

        with patch.dict(os.environ, {"LINE_CHANNEL_TOKEN": "test-token"}):
            result = register_richmenu()

        assert result is None
