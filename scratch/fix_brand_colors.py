import sys
sys.stdout.reconfigure(encoding='utf-8')

# Fix 1: app.py — update header_bg to proper brand color gradients
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_courses = """        {'id': 'python', 'name': 'Python Core', 'icon': 'fab fa-python', 'bg': 'python-bg', 'header_bg': 'linear-gradient(135deg, #3776ab, #ffde57)', 'link': '/python.html'},
        {'id': 'c', 'name': 'C Architecture', 'icon': 'fas fa-code-branch', 'bg': 'c-bg', 'header_bg': 'linear-gradient(135deg, #00599c, #004482)', 'link': '/c.html'},
        {'id': 'java', 'name': 'Java Masterclass', 'icon': 'fab fa-java', 'bg': 'java-bg', 'header_bg': 'linear-gradient(135deg, #ed8b00, #f8981d)', 'link': '/java.html'},
        {'id': 'web', 'name': 'Web Development', 'icon': 'fab fa-html5', 'bg': 'web-bg', 'header_bg': 'linear-gradient(135deg, #e34f26, #f06529)', 'link': '/web.html'},
        {'id': 'js', 'name': 'JavaScript Expert', 'icon': 'fab fa-js', 'bg': 'js-bg', 'header_bg': 'linear-gradient(135deg, #f7df1e, #f0db4f)', 'link': '/js.html'}"""

new_courses = """        {'id': 'python', 'name': 'Python Core', 'icon': 'fab fa-python', 'bg': 'python-bg', 'header_bg': 'linear-gradient(145deg, #1e4d8c 0%, #2b6cb0 60%, #3776ab 100%)', 'link': '/python.html'},
        {'id': 'c', 'name': 'C Architecture', 'icon': 'fas fa-code-branch', 'bg': 'c-bg', 'header_bg': 'linear-gradient(145deg, #00254d 0%, #003f80 55%, #00599c 100%)', 'link': '/c.html'},
        {'id': 'java', 'name': 'Java Masterclass', 'icon': 'fab fa-java', 'bg': 'java-bg', 'header_bg': 'linear-gradient(145deg, #7a3d00 0%, #c47000 55%, #ed8b00 100%)', 'link': '/java.html'},
        {'id': 'web', 'name': 'Web Development', 'icon': 'fab fa-html5', 'bg': 'web-bg', 'header_bg': 'linear-gradient(145deg, #7a1800 0%, #b83214 55%, #e34f26 100%)', 'link': '/web.html'},
        {'id': 'js', 'name': 'JavaScript Expert', 'icon': 'fab fa-js', 'bg': 'js-bg', 'header_bg': 'linear-gradient(145deg, #4a3800 0%, #8a6c00 55%, #b8960c 100%)', 'link': '/js.html'}"""

count = content.count(old_courses)
print(f"app.py: found {count} match(es)")
content = content.replace(old_courses, new_courses)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Fix 2: dashboard.html — revert to {{ course.header_bg }}
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_fixed = 'class="lp-card" style="background: linear-gradient(145deg, #1e1b4b 0%, #3730a3 55%, #4f46e5 100%);"'
new_dynamic = 'class="lp-card" style="background: {{ course.header_bg }};"'

count2 = html.count(old_fixed)
print(f"dashboard.html: found {count2} match(es)")
html = html.replace(old_fixed, new_dynamic)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done!")
