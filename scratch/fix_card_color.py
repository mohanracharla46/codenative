path = 'templates/dashboard.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old = 'class="lp-card" style="background: {{ course.header_bg }};"'
new = 'class="lp-card" style="background: linear-gradient(145deg, #1e1b4b 0%, #3730a3 55%, #4f46e5 100%);"'

count = content.count(old)
print(f"Found {count} occurrence(s)")

updated = content.replace(old, new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(updated)

print("Done.")
