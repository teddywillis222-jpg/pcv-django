import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import TeacherProfile

tp = TeacherProfile.objects.order_by('-id').first()
if tp:
    print(f"Teacher Profile ID: {tp.id}, Name: {tp.nom} {tp.prenom}")
    
    fields_to_check = [
        'photo_de_profil', 'presentation', 'methodologie', 
        'annees_d_experience', 'classes_enseignees', 'modes_de_cours',
        'ville_quartier', 'tarifs_par_classe', 'telephone_whatsapp'
    ]
    
    filled = 0
    for field in fields_to_check:
        val = getattr(tp, field)
        is_filled = bool(val)
        if val and isinstance(val, (list, dict)) and not val:
            is_filled = False
        if is_filled:
            filled += 1
        print(f"Field: {field:<20} | Value: {str(val)[:30]:<30} | Filled: {is_filled}")
        
    has_diploma = tp.diplomes.exists()
    if has_diploma:
        filled += 1
    print(f"Field: diplomes             | Value: exists={has_diploma}                | Filled: {has_diploma}")
    
    perc = int((filled / (len(fields_to_check) + 1)) * 100)
    print(f"Total filled: {filled} / {len(fields_to_check) + 1}")
    print(f"Completion Percentage: {perc}%")
    print(f"Model Property returns: {tp.completion_percentage}%")
else:
    print("No teacher profile found.")
