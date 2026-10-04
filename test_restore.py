import sys

try:
    with open('templates/core/prof_dashboard.html', 'r', encoding='utf-8') as f:
        text = f.read()
    
    restored = text.encode('cp1252').decode('utf-8')
    print("Restore test OK:", restored[:100].replace('\n', ' '))
except Exception as e:
    print("Error:", e)
