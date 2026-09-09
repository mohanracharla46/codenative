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
            
            # Revert primary CSS files (style, c, compiler, dashboard, auth, admin, roadmap) from media="print" back to standard rel="stylesheet"
            def revert_css(match):
                tag = match.group(0)
                href_match = re.search(r'href=["\']([^"\']+)["\']', tag)
                if href_match:
                    href = href_match.group(1)
                    return f'<link rel="stylesheet" href="{href}">'
                return tag

            cleaned = re.sub(
                r'<link\s+rel="stylesheet"\s+href=["\'][^"\']*\.min\.css[^"\']*["\']\s+media="print"\s+onload="this\.media=\'all\'">',
                revert_css,
                cleaned
            )
            cleaned = re.sub(
                r'<link\s+rel="stylesheet"\s+href=["\'][^"\']*\.css[^"\']*["\']\s+media="print"\s+onload="this\.media=\'all\'">',
                revert_css,
                cleaned
            )

            # Revert Google Fonts from media="print" back to standard rel="stylesheet"
            cleaned = re.sub(
                r'<link\s+rel="stylesheet"\s+href=["\']https://fonts\.googleapis\.com/css2[^"\']+["\']\s+media="print"\s+onload="this\.media=\'all\'">',
                revert_css,
                cleaned
            )

            # Clean any remaining noscript tags for CSS files
            cleaned = re.sub(r'<noscript><link rel="stylesheet" href="[^"]+style\.min\.css[^"]+"></noscript>', '', cleaned)
            cleaned = re.sub(r'<noscript><link rel="stylesheet" href="https://fonts\.googleapis\.com/[^"]+"></noscript>', '', cleaned)
            cleaned = re.sub(r'<noscript><link rel="stylesheet" href="[^"]+\.css"></noscript>', '', cleaned)

            if cleaned != content:
                with open(full_path, 'w', encoding='utf-8') as file:
                    file.write(cleaned)
                print(f"Restored standard CSS loading in: {f}")
