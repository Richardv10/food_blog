"""Remove trailing whitespace from CSS file."""

with open('static/CSS/style.css', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
cleaned_lines = [line.rstrip() for line in lines]

with open('static/CSS/style.css', 'w', encoding='utf-8') as f:
    f.write('\n'.join(cleaned_lines))

print('✅ Removed trailing whitespace from CSS file')
