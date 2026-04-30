import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines[193:200], start=194):
    print(f"Line {i}: {repr(line)}")
