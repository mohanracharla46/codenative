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
            # Clean up nested/duplicate noscript tags
            cleaned = re.sub(r'<noscript>\s*<link rel="stylesheet" href="([^"]+)" media="print" onload="this\.media=\'all\'">\s*<noscript>\s*<link rel="stylesheet" href="[^"]+">\s*</noscript>\s*</noscript>', r'<noscript><link rel="stylesheet" href="\1"></noscript>', cleaned)
            cleaned = re.sub(r'(<noscript><link rel="stylesheet" href="[^"]+"></noscript>)\s*<noscript><link rel="stylesheet" href="[^"]+"></noscript>', r'\1', cleaned)

            if cleaned != content:
                with open(full_path, 'w', encoding='utf-8') as file:
                    file.write(cleaned)
                print(f"Cleaned template: {f}")
