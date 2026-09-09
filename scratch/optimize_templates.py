import os
import re

templates_dir = r"c:\Users\racha\Desktop\codenative-main\templates"

def process_html_content(content, rel_path):
    orig = content

    # 1. Asynchronous Font Awesome
    fa_sync_pattern = r'<link\s+rel="stylesheet"\s+href="https://cdnjs\.cloudflare\.com/ajax/libs/font-awesome/6\.5\.1/css/all\.min\.css"\s*>'
    fa_async_replacement = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" media="print" onload="this.media=\'all\'">\n    <noscript><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"></noscript>'
    content = re.sub(fa_sync_pattern, fa_async_replacement, content)

    # 2. Add gstatic preconnect if fonts.googleapis.com is present without gstatic
    if 'fonts.googleapis.com' in content and 'fonts.gstatic.com' not in content:
        content = content.replace(
            '<link rel="preconnect" href="https://fonts.googleapis.com">',
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        )

    # 3. Ensure &display=swap on Google Fonts
    def font_swap(match):
        url = match.group(0)
        if 'display=swap' not in url:
            if '?' in url:
                return url + '&display=swap'
            else:
                return url + '?display=swap'
        return url
    content = re.sub(r'https://fonts\.googleapis\.com/css2\?[^\s"\'<>]+', font_swap, content)

    # 4. Replace CSS asset links with .min.css
    content = content.replace('/static/c.css', '/static/c.min.css')
    content = content.replace('/static/compiler.css', '/static/compiler.min.css')
    content = content.replace('/static/dashboard.css', '/static/dashboard.min.css')
    content = content.replace('/static/auth.css', '/static/auth.min.css')
    content = content.replace('/static/admin.css', '/static/admin.min.css')
    content = content.replace('/static/roadmap.css', '/static/roadmap.min.css')
    content = content.replace('/static/style.css', '/static/style.min.css')
    content = content.replace("filename='style.css'", "filename='style.min.css'")
    content = content.replace("filename='auth.css'", "filename='auth.min.css'")

    # 5. Replace JS asset links with .min.js
    content = content.replace('/static/c.js', '/static/c.min.js')
    content = content.replace('/static/java.js', '/static/java.min.js')
    content = content.replace('/static/python.js', '/static/python.min.js')
    content = content.replace('/static/tutorial.js', '/static/tutorial.min.js')
    content = content.replace('/static/chatbot.js', '/static/chatbot.min.js')
    content = content.replace('/static/compiler.js', '/static/compiler.min.js')
    content = content.replace("filename='theme.js'", "filename='theme.min.js'")
    content = content.replace("filename='chatbot.js'", "filename='chatbot.min.js'")
    content = content.replace("filename='whatsapp-widget.js'", "filename='whatsapp-widget.min.js'")

    # 6. Image WebP replacements
    content = content.replace('CodeNative.png', 'CodeNative.webp')
    content = content.replace('LMS image.jpg', 'LMS image.webp')
    content = content.replace('avatar1.png', 'avatar1.webp')
    content = content.replace('avatar2.png', 'avatar2.webp')
    content = content.replace('avatar3.png', 'avatar3.webp')

    return content

modified_count = 0
for root, dirs, files in os.walk(templates_dir):
    for f in files:
        if f.endswith('.html'):
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, templates_dir)
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()
            new_content = process_html_content(content, rel_path)
            if new_content != content:
                with open(full_path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                modified_count += 1
                print(f"Updated template: {rel_path}")

print(f"\nDone! Modified {modified_count} templates.")
