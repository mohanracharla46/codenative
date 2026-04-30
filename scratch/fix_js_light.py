import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add lp-card--light class for JS yellow card
old = '<div class="lp-card" style="background: {{ course.header_bg }};">'
new = '<div class="lp-card {% if course.id == \'js\' %}lp-card--light{% endif %}" style="background: {{ course.header_bg }};">'

count = html.count(old)
print(f"Found {count} match(es)")
html = html.replace(old, new)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Done!")
