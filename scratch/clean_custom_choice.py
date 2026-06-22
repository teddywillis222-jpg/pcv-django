import os
import django
import sys
import json
import unicodedata

sys.path.append(r"C:\Users\JGA'TIC BENIN\Documents\ProfChezVous")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import CustomChoice

def normalize(text):
    return unicodedata.normalize('NFKD', text.lower()).encode('ASCII', 'ignore').decode('utf-8')

file_path = r"C:\Users\JGA'TIC BENIN\Documents\ProfChezVous\core\matieres.json"
with open(file_path, "r", encoding="utf-8") as f:
    matieres = json.load(f)

json_normalized = {normalize(m): m for m in matieres}

custom_choices = CustomChoice.objects.filter(category='matiere')
deleted_count = 0

for choice in custom_choices:
    norm = normalize(choice.value)
    if norm in json_normalized:
        choice.delete()
        deleted_count += 1

print(f"Nettoyage effectué : {deleted_count} entrées redondantes supprimées de CustomChoice.")
