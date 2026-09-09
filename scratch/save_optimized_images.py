import os
from PIL import Image

static_img_dir = r"c:\Users\racha\Desktop\codenative-main\static\images"

# 1. Replace hero-girl.webp with optimized version
hero_png_p = os.path.join(static_img_dir, "hero-girl.png")
hero_webp_p = os.path.join(static_img_dir, "hero-girl.webp")

if os.path.exists(hero_png_p):
    with Image.open(hero_png_p) as img:
        img.save(hero_webp_p, "WEBP", quality=80, method=6)
        print(f"Updated hero-girl.webp size: {os.path.getsize(hero_webp_p)} bytes")

# 2. Create CodeNative.webp
logo_png_p = os.path.join(static_img_dir, "CodeNative.png")
logo_webp_p = os.path.join(static_img_dir, "CodeNative.webp")

if os.path.exists(logo_png_p):
    with Image.open(logo_png_p) as img:
        img.save(logo_webp_p, "WEBP", quality=85, method=6)
        print(f"Created CodeNative.webp size: {os.path.getsize(logo_webp_p)} bytes")

# Clean up temp file if exists
temp_hero = os.path.join(static_img_dir, "hero-girl-opt.webp")
if os.path.exists(temp_hero):
    os.remove(temp_hero)
