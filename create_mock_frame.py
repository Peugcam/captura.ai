"""Create a mock frame with kill feed text to test Vision API"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create a 1920x1080 frame
img = Image.new('RGB', (1920, 1080), color=(20, 20, 30))
draw = ImageDraw.Draw(img)

# Try to use a larger font
try:
    font = ImageFont.truetype("arial.ttf", 60)
    font_small = ImageFont.truetype("arial.ttf", 40)
except:
    font = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Add GTA-style kill feed in the top right
kill_feed_text = [
    "xXSniper420Xx KILLED Noob123",
    "ProGamer WASTED NewbPlayer",
    "TeamKiller SHOT DeadMan"
]

y_position = 100
for text in kill_feed_text:
    # Add shadow
    draw.text((1920 - 650 + 2, y_position + 2), text, fill=(0, 0, 0), font=font)
    # Add main text
    draw.text((1920 - 650, y_position), text, fill=(255, 50, 50), font=font)
    y_position += 80

# Add player count
draw.text((960 - 100, 50), "Players Alive: 47", fill=(0, 255, 100), font=font_small)

# Save
output_path = "test_frames/mock_kill_feed.jpg"
img.save(output_path, quality=90)
print(f"Mock frame created: {output_path}")
print("This frame contains kill feed text that should pass OCR filter")
