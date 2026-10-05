import sys, re
sys.stdout.reconfigure(encoding='utf-8')
path = 'templates/core/admin_create_announcement.html'
text = open(path, 'r', encoding='utf-8').read()

# Pattern for the SVG container in the preview
pattern = r'<div style="color: #16a34a; margin-top: 0\.15rem; flex-shrink: 0;">\s*<svg.*?</svg>\s*</div>'

if '<circle cx="12" cy="12" r="10"></circle>' in text:
    new_text = re.sub(pattern, '', text, flags=re.DOTALL)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("SVG enlevé du preview")
else:
    print("SVG preview not found")
