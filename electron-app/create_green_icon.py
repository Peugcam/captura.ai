"""
Create military green icon for GTA Analytics
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create 512x512 image (high resolution)
size = 512
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Military green colors
bg_color = (74, 95, 58)  # #4a5f3a - primary green
border_color = (90, 114, 68)  # #5a7244 - lighter green
text_color = (255, 255, 255)  # white

# Draw circle with gradient effect
center = size // 2
radius = size // 2 - 10

# Draw main circle
draw.ellipse([10, 10, size-10, size-10], fill=bg_color, outline=border_color, width=6)

# Draw text "GTA"
try:
    # Try to use a nice font
    font_large = ImageFont.truetype("arial.ttf", 160)
    font_small = ImageFont.truetype("arial.ttf", 60)
except:
    # Fallback to default
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Draw "GTA" text
text1 = "GTA"
bbox1 = draw.textbbox((0, 0), text1, font=font_large)
text1_width = bbox1[2] - bbox1[0]
text1_height = bbox1[3] - bbox1[1]
text1_x = (size - text1_width) // 2
text1_y = (size - text1_height) // 2 - 50

# Draw text with shadow for depth
shadow_color = (42, 74, 38)  # darker green
draw.text((text1_x+3, text1_y+3), text1, font=font_large, fill=shadow_color)
draw.text((text1_x, text1_y), text1, font=font_large, fill=text_color)

# Draw "Analytics" text
text2 = "Analytics"
bbox2 = draw.textbbox((0, 0), text2, font=font_small)
text2_width = bbox2[2] - bbox2[0]
text2_x = (size - text2_width) // 2
text2_y = text1_y + text1_height + 20

draw.text((text2_x+2, text2_y+2), text2, font=font_small, fill=shadow_color)
draw.text((text2_x, text2_y), text2, font=font_small, fill=text_color)

# Save PNG
output_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.png')
img.save(output_path, 'PNG')
print(f"Icon saved to: {output_path}")

# Also save tray icon (smaller version)
tray_img = img.resize((64, 64), Image.Resampling.LANCZOS)
tray_path = os.path.join(os.path.dirname(__file__), 'assets', 'tray-icon.png')
tray_img.save(tray_path, 'PNG')
print(f"Tray icon saved to: {tray_path}")

print("Green military icons created successfully!")
