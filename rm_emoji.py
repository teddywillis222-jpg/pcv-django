import sys, re
sys.stdout.reconfigure(encoding='utf-8')
path = 'templates/core/components/_announcement_card.html'
text = open(path, 'r', encoding='utf-8').read()

if '📢' in text:
    new_text = text.replace('<span style="margin-right: 5px;">📢</span>', '')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("📢 enlevé de la carte d'annonce")
else:
    print("📢 introuvable")
