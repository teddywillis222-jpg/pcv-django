import os
import django
import sys
import json
import unicodedata

# Set up Django environment
sys.path.append(r"C:\Users\JGA'TIC BENIN\Documents\ProfChezVous")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import CustomChoice
from django.conf import settings

def normalize(text):
    return unicodedata.normalize('NFKD', text.lower()).encode('ASCII', 'ignore').decode('utf-8')

# Load the JSON file
file_path = r"C:\Users\JGA'TIC BENIN\Documents\ProfChezVous\core\matieres.json"
with open(file_path, "r", encoding="utf-8") as f:
    matieres = json.load(f)

json_normalized = {normalize(m): m for m in matieres}

custom_choices = CustomChoice.objects.filter(category='matiere')
print(f"Found {custom_choices.count()} custom choices for matiere in DB.")

for choice in custom_choices:
    norm = normalize(choice.value)
    print(f" - {choice.value} (normalized: {norm})")
    if norm in json_normalized:
        print(f"   => Already in JSON. Should probably delete.")
