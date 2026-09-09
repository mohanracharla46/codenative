import os
from PIL import Image

static_img_dir = r"c:\Users\racha\Desktop\codenative-main\static\images"

files = os.listdir(static_img_dir)
print("Static images:")
for f in files:
    fp = os.path.join(static_img_dir, f)
    print(f"{f}: {os.path.getsize(fp)} bytes")

# 1. Optimize hero-girl.webp
hero_png_p = os.path.join(static_img_dir, "hero-girl.png")
hero_webp_p = os.path.join(static_img_dir, "hero-girl.webp")

if os.path.exists(hero_png_p):
    with Image.open(hero_png_p) as img:
        # Resize or save as WebP with optimal quality
        # Check dimensions
        print(f"hero-girl.png size: {img.size}")
        # Let's save a highly optimized WebP
        opt_path = os.path.join(static_img_dir, "hero-girl-opt.webp")
        img.save(opt_path, "WEBP", quality=80, method=6)
        print(f"hero-girl-opt.webp size: {os.path.getsize(opt_path)} bytes")

# 2. Convert CodeNative.png to WebP and compressed PNG
logo_png_p = os.path.join(static_img_dir, "CodeNative.png")
if os.path.exists(logo_png_p):
    with Image.open(logo_png_p) as img:
        print(f"CodeNative.png size: {img.size}")
        logo_webp_p = os.path.join(static_img_dir, "CodeNative.webp")
        img.save(logo_webp_p, "WEBP", quality=85, method=6)
        print(f"CodeNative.webp size: {os.path.getsize(logo_webp_p)} bytes")

# 3. LMS image.jpg
lms_jpg_p = os.path.join(static_img_dir, "LMS image.jpg")
if os.path.exists(lms_jpg_p):
    with Image.open(lms_jpg_p) as img:
        print(f"LMS image.jpg size: {img.size}")
        lms_webp_p = os.path.join(static_img_dir, "LMS image.webp")
        img.save(lms_webp_p, "WEBP", quality=80, method=6)
        print(f"LMS image.webp size: {os.path.getsize(lms_webp_p)} bytes")
