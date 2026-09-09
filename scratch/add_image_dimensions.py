import os
import re

templates_dir = r"c:\Users\racha\Desktop\codenative-main\templates"

for root, dirs, files in os.walk(templates_dir):
    for f in files:
        if f.endswith('.html'):
            full_path = os.path.join(root, f)
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            cleaned = content
            # If CodeNative.webp tag doesn't specify width/height, add width="180" height="45" decoding="async"
            def fix_cn_img(match):
                tag = match.group(0)
                if 'width=' not in tag:
                    tag = tag.replace('alt=', 'width="180" height="45" decoding="async" alt=')
                return tag
            
            cleaned = re.sub(r'<img\s+src=["\'][^"\']*CodeNative\.webp["\'][^>]*>', fix_cn_img, cleaned)

            if cleaned != content:
                with open(full_path, 'w', encoding='utf-8') as file:
                    file.write(cleaned)
                print(f"Added dimensions to logo image in: {f}")
