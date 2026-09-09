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
            # Theme.js -> theme.min.js with defer
            cleaned = re.sub(
                r'<script\s+src=["\']/static/theme\.js["\']\s*></script>',
                r'<script src="/static/theme.min.js" defer></script>',
                cleaned
            )
            cleaned = re.sub(
                r'<script\s+src=["\']/static/theme\.js["\']\s+defer\s*></script>',
                r'<script src="/static/theme.min.js" defer></script>',
                cleaned
            )
            cleaned = re.sub(
                r'filename=\'theme\.js\'',
                r"filename='theme.min.js'",
                cleaned
            )

            # Ensure defer on theme.min.js if missing defer
            cleaned = re.sub(
                r'<script\s+src=["\']/static/theme\.min\.js["\']\s*></script>',
                r'<script src="/static/theme.min.js" defer></script>',
                cleaned
            )

            if cleaned != content:
                with open(full_path, 'w', encoding='utf-8') as file:
                    file.write(cleaned)
                print(f"Updated scripts in template: {f}")
