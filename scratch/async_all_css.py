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

            # Make static CSS links asynchronous if not already
            def make_css_async(match):
                tag = match.group(0)
                if 'media=' in tag or 'onload=' in tag:
                    return tag
                href_match = re.search(r'href=["\']([^"\']+)["\']', tag)
                if href_match:
                    href = href_match.group(1)
                    return f'<link rel="stylesheet" href="{href}" media="print" onload="this.media=\'all\'">\n    <noscript><link rel="stylesheet" href="{href}"></noscript>'
                return tag

            # Pattern for static CSS files (e.g. style.min.css, c.min.css, compiler.min.css, etc.)
            cleaned = re.sub(r'<link\s+rel="stylesheet"\s+href=["\'][^"\']*\.min\.css[^"\']*["\']\s*>', make_css_async, cleaned)
            cleaned = re.sub(r'<link\s+rel="stylesheet"\s+href=["\'][^"\']*\.css[^"\']*["\']\s*>', make_css_async, cleaned)

            # Pattern for Google Fonts link without media="print"
            def make_gf_async(match):
                tag = match.group(0)
                if 'media=' in tag or 'onload=' in tag:
                    return tag
                href_match = re.search(r'href=["\']([^"\']+)["\']', tag)
                if href_match:
                    href = href_match.group(1)
                    return f'<link rel="stylesheet" href="{href}" media="print" onload="this.media=\'all\'">\n    <noscript><link rel="stylesheet" href="{href}"></noscript>'
                return tag

            cleaned = re.sub(r'<link\s+rel="stylesheet"\s+href=["\']https://fonts\.googleapis\.com/css2[^"\']+["\']\s*>', make_gf_async, cleaned)

            # Remove duplicate noscript blocks if any
            cleaned = re.sub(r'(<noscript><link rel="stylesheet" href="[^"]+"></noscript>\s*)+<noscript><link rel="stylesheet" href="[^"]+"></noscript>', r'\1', cleaned)

            if cleaned != content:
                with open(full_path, 'w', encoding='utf-8') as file:
                    file.write(cleaned)
                print(f"Made CSS async in: {f}")
