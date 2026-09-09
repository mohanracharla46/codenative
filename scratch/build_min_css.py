import re
import os

css_path = r"c:\Users\racha\Desktop\codenative-main\static\style.css"
min_path = r"c:\Users\racha\Desktop\codenative-main\static\style.min.css"

with open(css_path, "r", encoding="utf-8") as f:
    content = f.read()

# Strip comments
content = re.sub(r'/\*[\s\S]*?\*/', '', content)
# Strip unnecessary whitespace
content = re.sub(r'\s+', ' ', content)
content = re.sub(r'\s*([\{\}\:\;\,])\s*', r'\1', content)
content = re.sub(r';\}', '}', content)
content = content.strip()

with open(min_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Generated style.min.css ({len(content.encode('utf-8'))} bytes)")
