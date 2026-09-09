import re
import os

static_dir = r"c:\Users\racha\Desktop\codenative-main\static"

def minify_css(css):
    css = re.sub(r'/\*[\s\S]*?\*/', '', css)
    css = re.sub(r'\s+', ' ', css)
    css = re.sub(r'\s*([\{\}\:\;\,])\s*', r'\1', css)
    css = re.sub(r';\}', '}', css)
    return css.strip()

def minify_js(js):
    # Strip block comments (careful with regexes / strings)
    js = re.sub(r'/\*[\s\S]*?\*/', '', js)
    # Strip single line comments starting at line start or whitespace
    js = re.sub(r'(?<=\s)//.*$', '', js, flags=re.MULTILINE)
    js = re.sub(r'^\s*//.*$', '', js, flags=re.MULTILINE)
    # Compact multiple empty lines / whitespace
    lines = [line.strip() for line in js.splitlines() if line.strip()]
    return '\n'.join(lines)

css_files = ['style.css', 'c.css', 'compiler.css', 'dashboard.css', 'auth.css', 'admin.css', 'roadmap.css']
js_files = ['c.js', 'java.js', 'python.js', 'tutorial.js', 'chatbot.js', 'compiler.js', 'whatsapp-widget.js', 'theme.js', 'script.js']

print("--- Minifying CSS Files ---")
for f_name in css_files:
    src_path = os.path.join(static_dir, f_name)
    min_name = f_name.replace('.css', '.min.css')
    dst_path = os.path.join(static_dir, min_name)
    if os.path.exists(src_path):
        with open(src_path, 'r', encoding='utf-8') as f:
            raw = f.read()
        minified = minify_css(raw)
        with open(dst_path, 'w', encoding='utf-8') as f:
            f.write(minified)
        print(f"CSS: {f_name} ({len(raw)} B) -> {min_name} ({len(minified)} B)")

print("\n--- Minifying JS Files ---")
for f_name in js_files:
    src_path = os.path.join(static_dir, f_name)
    min_name = f_name.replace('.js', '.min.js')
    dst_path = os.path.join(static_dir, min_name)
    if os.path.exists(src_path):
        with open(src_path, 'r', encoding='utf-8') as f:
            raw = f.read()
        minified = minify_js(raw)
        with open(dst_path, 'w', encoding='utf-8') as f:
            f.write(minified)
        print(f"JS: {f_name} ({len(raw)} B) -> {min_name} ({len(minified)} B)")
