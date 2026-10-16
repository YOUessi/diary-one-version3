"""Share still-image compose for Expo Go (Pillow) — collage + illustrated styles."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

COLLAGE_W = 1080
COLLAGE_H = 1350  # 4:5 share-friendly
GAP = 12
PAD = 24
BG = (18, 18, 18)
PAPER = (245, 241, 234)
INK = (28, 28, 28)


def _open_rgb(data: bytes) -> Image.Image:
    img = Image.open(BytesIO(data))
    return ImageOps.exif_transpose(img).convert("RGB")


def _cover(img: Image.Image, tw: int, th: int) -> Image.Image:
    return ImageOps.fit(img, (tw, th), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def compose_collage(images: list[bytes], *, max_tiles: int = 4) -> bytes:
    """Multi-tile photo collage (1–4 cells)."""
    if not images:
        raise ValueError("no_images")
    tiles = [_open_rgb(b) for b in images[:max_tiles]]
    n = len(tiles)
    canvas = Image.new("RGB", (COLLAGE_W, COLLAGE_H), BG)
    inner_w = COLLAGE_W - PAD * 2
    inner_h = COLLAGE_H - PAD * 2

    if n == 1:
        canvas.paste(_cover(tiles[0], inner_w, inner_h), (PAD, PAD))
    elif n == 2:
        cell_w = (inner_w - GAP) // 2
        for i, t in enumerate(tiles):
            x = PAD + i * (cell_w + GAP)
            canvas.paste(_cover(t, cell_w, inner_h), (x, PAD))
    elif n == 3:
        left_w = int(inner_w * 0.58)
        right_w = inner_w - left_w - GAP
        half_h = (inner_h - GAP) // 2
        canvas.paste(_cover(tiles[0], left_w, inner_h), (PAD, PAD))
        canvas.paste(_cover(tiles[1], right_w, half_h), (PAD + left_w + GAP, PAD))
        canvas.paste(
            _cover(tiles[2], right_w, half_h),
            (PAD + left_w + GAP, PAD + half_h + GAP),
        )
    else:
        cell_w = (inner_w - GAP) // 2
        cell_h = (inner_h - GAP) // 2
        positions = [
            (PAD, PAD),
            (PAD + cell_w + GAP, PAD),
            (PAD, PAD + cell_h + GAP),
            (PAD + cell_w + GAP, PAD + cell_h + GAP),
        ]
        for t, (x, y) in zip(tiles[:4], positions):
            canvas.paste(_cover(t, cell_w, cell_h), (x, y))

    out = BytesIO()
    canvas.save(out, format="JPEG", quality=90, optimize=True)
    return out.getvalue()


def compose_illustrated(image: bytes, style: str, *, title: str = "") -> bytes:
    """
    Style A — Polaroid / paper frame + caption bar
    Style B — Warm grade + soft vignette
    Style C — Cool split duotone panel
    """
    src = _open_rgb(image)
    style = (style or "A").upper()
    if style not in ("A", "B", "C"):
        style = "A"

    if style == "A":
        frame = 48
        bar_h = 120
        photo = _cover(src, COLLAGE_W - frame * 2, COLLAGE_H - frame * 2 - bar_h)
        canvas = Image.new("RGB", (COLLAGE_W, COLLAGE_H), PAPER)
        canvas.paste(photo, (frame, frame))
        draw = ImageDraw.Draw(canvas)
        caption = (title or "Diary One").strip()[:42] or "Diary One"
        draw.rectangle(
            [(0, COLLAGE_H - bar_h), (COLLAGE_W, COLLAGE_H)],
            fill=PAPER,
        )
        # Simple centered caption (default font — Expo Go still gets a distinct layout)
        tw = draw.textlength(caption) if hasattr(draw, "textlength") else len(caption) * 8
        draw.text(
            ((COLLAGE_W - tw) / 2, COLLAGE_H - bar_h + 42),
            caption,
            fill=INK,
        )
    elif style == "B":
        photo = _cover(src, COLLAGE_W, COLLAGE_H)
        photo = ImageEnhance.Color(photo).enhance(1.25)
        photo = ImageEnhance.Contrast(photo).enhance(1.08)
        photo = ImageEnhance.Brightness(photo).enhance(1.05)
        # Warm overlay
        warm = Image.new("RGB", photo.size, (255, 170, 90))
        photo = Image.blend(photo, warm, 0.18)
        # Soft edge vignette
        vignette = Image.new("L", photo.size, 0)
        vdraw = ImageDraw.Draw(vignette)
        margin = 80
        vdraw.ellipse(
            [margin, margin, photo.size[0] - margin, photo.size[1] - margin],
            fill=255,
        )
        vignette = vignette.filter(ImageFilter.GaussianBlur(60))
        darkened = ImageEnhance.Brightness(photo).enhance(0.55)
        photo = Image.composite(photo, darkened, vignette)
        canvas = photo
    else:  # C
        photo = _cover(src, COLLAGE_W, COLLAGE_H)
        left = photo.crop((0, 0, COLLAGE_W // 2, COLLAGE_H))
        right = photo.crop((COLLAGE_W // 2, 0, COLLAGE_W, COLLAGE_H))
        left = ImageEnhance.Color(left).enhance(0.35)
        left = ImageOps.colorize(ImageOps.grayscale(left), black="#0a1628", white="#c8d8f0")
        right = ImageEnhance.Color(right).enhance(1.4)
        right = ImageEnhance.Contrast(right).enhance(1.15)
        canvas = Image.new("RGB", (COLLAGE_W, COLLAGE_H))
        canvas.paste(left, (0, 0))
        canvas.paste(right, (COLLAGE_W // 2, 0))
        # Thin center rule
        draw = ImageDraw.Draw(canvas)
        draw.line([(COLLAGE_W // 2, 0), (COLLAGE_W // 2, COLLAGE_H)], fill=(255, 255, 255), width=3)

    out = BytesIO()
    canvas.save(out, format="JPEG", quality=90, optimize=True)
    return out.getvalue()


def write_jpeg(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
