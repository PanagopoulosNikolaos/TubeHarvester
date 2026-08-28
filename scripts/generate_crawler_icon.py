#!/usr/bin/env python3
"""
Generates the crawler.png icon.

Creates a black line-art YouTube logo (rounded rectangle with "YouTube" text),
tilts it slightly, and composites it directly at the spider's mouth so it
looks like the spider bit the logo and is dragging it upward. Paths are
resolved relative to the project root so the script can run from any working
directory.

Usage:
    python scripts/generate_crawler_icon.py
"""

from pathlib import Path

import math

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_IMAGE = PROJECT_ROOT / "images" / "icons" / "spiderweb1.png"
OUTPUT_IMAGE = PROJECT_ROOT / "images" / "icons" / "crawler.png"

LOGO_WIDTH = 120           # Width of the pasted logo before rotation, in pixels.
TILT_ANGLE = -55           # Clockwise rotation; negative angle tilts down-right like "\".
MOUTH_POINT = (297, 470)   # Center of the spider's mouth between the fangs.
BOX_PADDING = 20           # Padding between logo and box borders, in pixels.


def createYoutubeLogo(width: int) -> Image.Image:
    """
    Creates a black line-art YouTube logo matching the spiderweb icon style.

    Args:
        width (int): Target width of the returned logo in pixels.

    Returns:
        Image.Image: RGBA image of a rounded-rectangle outline containing
            the text "YouTube", cropped to content and resized to width.
    """
    logo = Image.new("RGBA", (200, 140), (0, 0, 0, 0))
    draw = ImageDraw.Draw(logo)


    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 31
        )
    except OSError:
        font = ImageFont.load_default()  # Fallback keeps the script portable.

    text = "YouTube"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    draw.text(
        ((200 - text_w) // 2 - text_bbox[0], (140 - text_h) // 2 - text_bbox[1]),
        text,
        fill="black",
        font=font,
    )

    logo = logo.crop(logo.getbbox())  # Trims empty margins around the artwork.
    height = round(width * logo.size[1] / logo.size[0])
    return logo.resize((width, height), Image.Resampling.LANCZOS)


def generateCrawlerIcon() -> None:
    """
    Composites the tilted YouTube logo onto the spiderweb icon.

    Loads spiderweb.png and pastes the rotated logo at the spider's mouth
    so it appears to be bitten and dragged upward.

    Returns:
        None: The result is written to OUTPUT_IMAGE.
    """
    yt_logo = createYoutubeLogo(LOGO_WIDTH)
    logo_w, logo_h = yt_logo.size

    box_w = logo_w + 2 * BOX_PADDING
    box_h = logo_h + 2 * BOX_PADDING

    box = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    box_draw = ImageDraw.Draw(box)
    box_draw.rounded_rectangle([2, 2, box_w - 3, box_h - 3], radius=30, outline="black", width=5)

    box.paste(yt_logo, (BOX_PADDING, BOX_PADDING), yt_logo)

    box_rotated = box.rotate(TILT_ANGLE, expand=True, fillcolor=(0, 0, 0, 0))

    result = Image.open(SOURCE_IMAGE).convert("RGBA")

    rot_w, rot_h = box_rotated.size
    angle_rad = math.radians(TILT_ANGLE)
    cx, cy = box_w / 2, box_h / 2
    corner_x = -cx * math.cos(angle_rad) + cy * math.sin(angle_rad) + rot_w / 2
    corner_y = -cx * math.sin(angle_rad) - cy * math.cos(angle_rad) + rot_h / 2

    paste_x = int(MOUTH_POINT[0] - corner_x)
    paste_y = int(MOUTH_POINT[1] - corner_y)

    result.paste(box_rotated, (paste_x, paste_y), box_rotated)
    result.save(OUTPUT_IMAGE, "PNG")
    print(f"Saved {OUTPUT_IMAGE} (rotated box {rot_w}x{rot_h} at {paste_x},{paste_y}, corner offset ({corner_x:.1f},{corner_y:.1f}))")


if __name__ == "__main__":
    generateCrawlerIcon()
