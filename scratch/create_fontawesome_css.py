import urllib.request
import re

fa_cdn_url = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"
output_path = r"c:\Users\racha\Desktop\codenative-main\static\font-awesome.min.css"

try:
    req = urllib.request.Request(fa_cdn_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        css_content = response.read().decode('utf-8')
    
    # Replace relative webfonts URLs with absolute cdnjs URLs
    css_content = css_content.replace('url(../webfonts/', 'url(https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/webfonts/')
    
    # Replace any font-display:block or font-display:auto with font-display:swap
    css_content = re.sub(r'font-display\s*:\s*(block|auto|fallback)', 'font-display:swap', css_content)
    
    # If font-display is not in @font-face, insert font-display:swap
    def add_fd_swap(match):
        block = match.group(0)
        if 'font-display' not in block:
            return block.replace('{', '{font-display:swap;')
        return block

    css_content = re.sub(r'@font-face\s*\{[^}]*\}', add_fd_swap, css_content)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    print(f"Created font-awesome.min.css with strict font-display:swap ({len(css_content)} bytes)")

except Exception as e:
    print(f"Error fetching Font Awesome CSS: {e}")
