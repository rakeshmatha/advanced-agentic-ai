from __future__ import annotations

from pathlib import Path

from PIL import Image


def analyze_image(image_path: str | Path) -> dict:
    path = Path(image_path)
    img = Image.open(path)
    pixels = img.convert("RGB")
    width, height = pixels.size

    r_total = 0
    g_total = 0
    b_total = 0

    for y in range(height):
        for x in range(width):
            r, g, b = pixels.getpixel((x, y))
            r_total += r
            g_total += g
            b_total += b

    count = width * height
    avg_rgb = (r_total // count, g_total // count, b_total // count)

    thumb = img.resize((200, 150))
    thumb_path = path.with_name(f"{path.stem}_thumb.jpg")
    thumb.save(thumb_path)

    return {
        "file": str(path.resolve()),
        "format": img.format,
        "mode": img.mode,
        "size": (width, height),
        "average_rgb": avg_rgb,
        "thumbnail": str(thumb_path.resolve()),
    }


def main() -> None:
    result = analyze_image("dd1.jpeg")
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
