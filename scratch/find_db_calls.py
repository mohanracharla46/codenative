
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

calls = [m.start() for m in re.finditer('get_db_connection\(', content)]
for pos in calls:
    line_no = content.count('\n', 0, pos) + 1
    context = content[pos:pos+500].split('\n')[:10]
    print(f"Line {line_no}:")
    print('\n'.join(context))
    print("-" * 40)
