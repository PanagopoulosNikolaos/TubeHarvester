#!/usr/bin/env python3
"""
Generates the crawler.png icon.

Creates a black line-art YouTube logo (rounded rectangle with "YouTube" text),
tilts it down to the right, and composites it onto spiderweb.png so it hangs
from the spider's mouth on a short silk thread. Paths are resolved relative to
the project root so the script can run from any working directory.

Usage:
    python scripts/generate_crawler_icon.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_IMAGE = PROJECT_ROOT / "images" / "icons" / "spiderweb.png"
OUTPUT_IMAGE = PROJECT_ROOT / "images" / "icons" / "crawler.png"

LOGO_WIDTH = 85            # Width of the pasted logo before rotation, in pixels.
TILT_ANGLE = -20           # Clockwise rotation; negative angle tilts down-right like "\".
LOGO_CENTER_X = 305        # Horizontal center of the hanging logo on the canvas.
LOGO_TOP_Y = 448           # Vertical top of the pasted logo, just below the spider's legs.
MOUTH_POINT = (295, 388)   # Bottom of the spider body where the thread anchors.


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

    draw.rounded_rectangle([2, 2, 197, 137], radius=30, outline="black", width=10)

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42
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

    Loads spiderweb.png, draws a silk thread from the spider's mouth, and
    pastes the rotated logo below the legs so it appears to hang.

    Returns:
        None: The result is written to OUTPUT_IMAGE.
    """
    yt_logo = createYoutubeLogo(LOGO_WIDTH)
    yt_rotated = yt_logo.rotate(TILT_ANGLE, expand=True, fillcolor=(0, 0, 0, 0))

    result = Image.open(SOURCE_IMAGE).convert("RGBA")
    draw = ImageDraw.Draw(result)

    logo_w, logo_h = yt_rotated.size
    paste_x = LOGO_CENTER_X - logo_w // 2
    paste_y = LOGO_TOP_Y

    # Thread runs from the mouth to the top-left corner of the tilted logo.
    thread_top = MOUTH_POINT
    thread_bottom = (LOGO_CENTER_X - 12, paste_y + 14)
    draw.line([thread_top, thread_bottom], fill="black", width=3)

    result.paste(yt_rotated, (paste_x, paste_y), yt_rotated)
    result.save(OUTPUT_IMAGE, "PNG")
    print(f"Saved {OUTPUT_IMAGE} (logo {logo_w}x{logo_h} at {paste_x},{paste_y})")


if __name__ == "__main__":
    generateCrawlerIcon()
