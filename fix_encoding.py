import os, django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Quartier

# Fix corrupted strings
for q in Quartier.objects.all():
    original_nom = q.nom
    modified = False
    
    # Check for unicode replacement characters or corrupted chars
    if "" in q.nom or "" in q.ville or "Ǹ" in q.nom or "Ǹ" in q.ville:
        print(f"Fixing: {q.nom}")
        
    replacements = {
        'Fidjross': 'Fidjrossè',
        'Gbgamey': 'Gbégamey',
        'GbǸgamey': 'Gbégamey',
        'Mrontin': 'Mérontin',
        'MǸrontin': 'Mérontin',
        'Vdoko': 'Vèdoko',
        'Suru Lr': 'Suru Léré',
        'Suru LǸrǸ': 'Suru Léré',
        'Zogbadj': 'Zogbadjè',
        'Tankp': 'Tankpè',
        'Houdonou': 'Houèdonou',
        'Cit Houeyiho': 'Cité Houeyiho',
        'CitǸ Houeyiho': 'Cité Houeyiho',
        'Oudo': 'Ouèdo',
        'Sm-Kpodji': 'Sèmè-Kpodji',
    }

    for bad, good in replacements.items():
        if bad in q.nom:
            q.nom = q.nom.replace(bad, good)
            modified = True
        if bad in q.ville:
            q.ville = q.ville.replace(bad, good)
            modified = True
            
    if modified:
        q.save()
        print(f'Updated: {original_nom} -> {q.nom}')

file_path = 'core/localisations.json'
with open(file_path, 'w', encoding='utf-8') as f:
    data = [[f'{q.nom} - {q.ville}', f'{q.nom} - {q.ville}'] for q in Quartier.objects.all().order_by('ville', 'nom')]
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Done fixing encoding!')
