import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Insert the lp-lang-icon div AFTER the ghost icon div
old = '                    <!-- Ghost background icon -->\n                    <div class="lp-ghost"><i class="{{ course.icon }}"></i></div>\n\n                    <!-- Status badge -->'
new = '                    <!-- Ghost background icon -->\n                    <div class="lp-ghost"><i class="{{ course.icon }}"></i></div>\n\n                    <!-- Visible language logo -->\n                    <div class="lp-lang-icon"><i class="{{ course.icon }}"></i></div>\n\n                    <!-- Status badge -->'

count = html.count(old)
print(f"Found {count} match(es)")
html = html.replace(old, new)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Done!")
