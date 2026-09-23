from PIL import Image
from pathlib import Path

image_path = Path("dd1.jpeg")
img = Image.open(image_path)

print(f"File: {image_path.resolve()}")
print(f"Format: {img.format}")
print(f"Mode: {img.mode}")
print(f"Size: {img.size}")

# Basic stats
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
print(f"Average RGB: ({r_total // count}, {g_total // count}, {b_total // count})")

# Save a small thumbnail for quick visual output
thumb = img.resize((200, 150))
thumb.save("dd1_thumb.jpg")
print("Saved thumbnail: dd1_thumb.jpg")
