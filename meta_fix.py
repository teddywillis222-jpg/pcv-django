import os
files = ['templates/core/apprenant_create_profile.html', 'templates/core/parent_create_profile.html', 'templates/core/parent_dashboard.html']
meta = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">'
for path in files:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if "{% block extra_css %}" in content and meta not in content:
            content = content.replace("{% block extra_css %}", "{% block extra_css %}\n" + meta)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"FIXED {path}")
