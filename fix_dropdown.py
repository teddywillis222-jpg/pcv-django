import os

with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("dropdownParent: 'body',", "dropdownParent: select.closest('.modal-content') || select.closest('.side-panel') || 'body',")

with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed dropdownParent in base.html')
