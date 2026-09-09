import re
import os

css_path = r"c:\Users\racha\Desktop\codenative-main\static\style.css"
with open(css_path, "r", encoding="utf-8") as f:
    content = f.read()

orig_size = len(content.encode('utf-8'))

# Strip comments
content = re.sub(r'/\*[\s\S]*?\*/', '', content)
# Strip unnecessary whitespace
content = re.sub(r'\s+', ' ', content)
content = re.sub(r'\s*([\{\}\:\;\,])\s*', r'\1', content)
content = re.sub(r';\}', '}', content)
content = content.strip()

min_size = len(content.encode('utf-8'))
print(f"Original style.css: {orig_size} bytes")
print(f"Minified style.css: {min_size} bytes (Saved {orig_size - min_size} bytes)")
