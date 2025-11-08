"""CSS validation checker."""

with open('static/CSS/style.css', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

issues = []

# Check for trailing whitespace
for i, line in enumerate(lines, 1):
    if line != line.rstrip():
        issues.append(f'Line {i}: Trailing whitespace')

# Check for common CSS validation issues
for i, line in enumerate(lines, 1):
    # Check for missing semicolons (property: value without ;)
    if ':' in line and '{' not in line and '}' not in line:
        stripped = line.strip()
        if stripped and not stripped.endswith((';', '{')):
            if not stripped.startswith(('/*', '*', '//')):
                issues.append(
                    f'Line {i}: Possible missing semicolon - {stripped[:50]}'
                )

if issues:
    print('\n'.join(issues))
else:
    print('✅ No validation issues found in CSS')
