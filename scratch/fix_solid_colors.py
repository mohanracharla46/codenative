import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_courses = """        {'id': 'python', 'name': 'Python Core', 'icon': 'fab fa-python', 'bg': 'python-bg', 'header_bg': 'linear-gradient(145deg, #1e4d8c 0%, #2b6cb0 60%, #3776ab 100%)', 'link': '/python.html'},
        {'id': 'c', 'name': 'C Architecture', 'icon': 'fas fa-code-branch', 'bg': 'c-bg', 'header_bg': 'linear-gradient(145deg, #00254d 0%, #003f80 55%, #00599c 100%)', 'link': '/c.html'},
        {'id': 'java', 'name': 'Java Masterclass', 'icon': 'fab fa-java', 'bg': 'java-bg', 'header_bg': 'linear-gradient(145deg, #7a3d00 0%, #c47000 55%, #ed8b00 100%)', 'link': '/java.html'},
        {'id': 'web', 'name': 'Web Development', 'icon': 'fab fa-html5', 'bg': 'web-bg', 'header_bg': 'linear-gradient(145deg, #7a1800 0%, #b83214 55%, #e34f26 100%)', 'link': '/web.html'},
        {'id': 'js', 'name': 'JavaScript Expert', 'icon': 'fab fa-js', 'bg': 'js-bg', 'header_bg': 'linear-gradient(145deg, #4a3800 0%, #8a6c00 55%, #b8960c 100%)', 'link': '/js.html'}"""

new_courses = """        {'id': 'python', 'name': 'Python Core', 'icon': 'fab fa-python', 'bg': 'python-bg', 'header_bg': '#3776ab', 'link': '/python.html'},
        {'id': 'c', 'name': 'C Architecture', 'icon': 'fas fa-code-branch', 'bg': 'c-bg', 'header_bg': '#00599c', 'link': '/c.html'},
        {'id': 'java', 'name': 'Java Masterclass', 'icon': 'fab fa-java', 'bg': 'java-bg', 'header_bg': '#ed8b00', 'link': '/java.html'},
        {'id': 'web', 'name': 'Web Development', 'icon': 'fab fa-html5', 'bg': 'web-bg', 'header_bg': '#e34f26', 'link': '/web.html'},
        {'id': 'js', 'name': 'JavaScript Expert', 'icon': 'fab fa-js', 'bg': 'js-bg', 'header_bg': '#f7df1e', 'link': '/js.html'}"""

count = content.count(old_courses)
print(f"app.py: found {count} match(es)")
content = content.replace(old_courses, new_courses)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")
