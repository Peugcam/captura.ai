"""
Quick icon generator for GTA Analytics
Creates a simple icon from scratch
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create icon sizes
sizes = [256, 128, 64, 48, 32, 16]

# Create 256x256 base image
img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw gradient background circle
for i in range(128, 0, -1):
    alpha = int(255 * (i / 128))
    color = (233, 69, 96, alpha)  # GTA Analytics red
    draw.ellipse([128-i, 128-i, 128+i, 128+i], fill=color)

# Draw "GTA" text
try:
    # Try to use a bold font
    font = ImageFont.truetype("arialbd.ttf", 80)
except:
    font = ImageFont.load_default()

# Draw text with shadow
draw.text((128, 100), "GTA", fill=(0, 0, 0, 200), font=font, anchor="mm")
draw.text((128, 98), "GTA", fill=(255, 255, 255, 255), font=font, anchor="mm")

# Draw "Analytics" smaller
try:
    font_small = ImageFont.truetype("arial.ttf", 24)
except:
    font_small = ImageFont.load_default()

draw.text((128, 155), "Analytics", fill=(255, 255, 255, 200), font=font_small, anchor="mm")

# Save PNG
os.makedirs("assets", exist_ok=True)
img.save("assets/icon.png", "PNG")
print("[OK] Created assets/icon.png")

# Create ICO with multiple sizes
icon_images = []
for size in sizes:
    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    icon_images.append(resized)

icon_images[0].save(
    "assets/icon.ico",
    format='ICO',
    sizes=[(s, s) for s in sizes]
)
print("[OK] Created assets/icon.ico")

# Also create tray icon (smaller, simpler)
tray = img.resize((256, 256), Image.Resampling.LANCZOS)
tray.save("assets/tray-icon.png", "PNG")
print("[OK] Created assets/tray-icon.png")

print("\nAll icons created successfully!")
