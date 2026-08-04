import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Quartier
import json

for q in Quartier.objects.all():
    original = q.nom
    modified = False
    
    # Fix the mess of repeated è
    while '\xe8\xe8' in q.nom:
        q.nom = q.nom.replace('\xe8\xe8', '\xe8')
        modified = True
    while '\xe9\xe9' in q.nom:
        q.nom = q.nom.replace('\xe9\xe9', '\xe9')
        modified = True
        
    # Also fix some characters from the first corrupted import if they still exist
    if '' in q.nom or '' in q.ville:
        # We need to manually rename the bad ones
        if q.id == 13: q.nom = 'Fidjrossè'
        if q.id == 28: q.nom = 'Tankpè'
        if q.id == 33: q.nom = 'Zogbadjè'
        if q.id == 16: q.nom = 'Gbégamey'
        if q.id == 22: q.nom = 'Mérontin'
        if q.id == 32: q.nom = 'Vèdoko'
        if q.id == 27: q.nom = 'Suru Léré'
        if q.id == 19: q.nom = 'Houèdonou'
        if q.id == 11: q.nom = 'Cité Houeyiho'
        if q.id == 23: q.nom = 'Ouèdo'
        if q.id == 41: q.nom = 'Adogbèta'
        if q.id == 49: q.nom = 'Niaro/Sinendé'
        modified = True

    if modified:
        q.save()
        print(f"Fixed {original} -> {ascii(q.nom)}")

file_path = 'core/localisations.json'
with open(file_path, 'w', encoding='utf-8') as f:
    data = [[f'{q.nom} - {q.ville}', f'{q.nom} - {q.ville}'] for q in Quartier.objects.all().order_by('ville', 'nom')]
    json.dump(data, f, ensure_ascii=False, indent=2)

print("DB and JSON fixed")
