import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('templates/core/prof_attente_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

banner_pattern = r'<!-- Bannière Communauté WhatsApp -->\s*<a href="https://whatsapp\.com/channel/.*?</a>'

if "Bannière Communauté WhatsApp" in text:
    text = re.sub(banner_pattern, '', text, flags=re.DOTALL)
    with open('templates/core/prof_attente_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Bannière supprimée avec succès")
else:
    print("Bannière introuvable ou déjà supprimée")
