"""Unit tests for share still compose (Pillow)."""
from __future__ import annotations

from io import BytesIO

from PIL import Image

from shared.share_compose import compose_collage, compose_illustrated


def _solid_jpeg(color: tuple[int, int, int], size: tuple[int, int] = (400, 500)) -> bytes:
    img = Image.new("RGB", size, color)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def test_compose_collage_one_to_four():
    red = _solid_jpeg((200, 40, 40))
    for n in (1, 2, 3, 4):
        out = compose_collage([red] * n)
        assert out[:2] == b"\xff\xd8"
        img = Image.open(BytesIO(out))
        assert img.size == (1080, 1350)


def test_compose_illustrated_styles():
    src = _solid_jpeg((40, 120, 200))
    for style in ("A", "B", "C"):
        out = compose_illustrated(src, style, title="Morning Fishing")
        assert out[:2] == b"\xff\xd8"
        img = Image.open(BytesIO(out))
        assert img.size[0] == 1080
