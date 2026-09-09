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
            # Add defer to any local /static/ script tag that doesn't have async or defer
            def add_defer(match):
                tag = match.group(0)
                if 'defer' in tag or 'async' in tag or 'type="application/ld+json"' in tag:
                    return tag
                return tag.replace('<script ', '<script defer ')
            
            cleaned = re.sub(r'<script\s+src=["\']/static/[^"\']+["\'][^>]*></script>', add_defer, cleaned)

            if cleaned != content:
                with open(full_path, 'w', encoding='utf-8') as file:
                    file.write(cleaned)
                print(f"Deferred body scripts in: {f}")
