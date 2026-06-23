import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import TeacherProfile

fixed_count = 0
for tp in TeacherProfile.objects.all():
    if tp.classes_enseignees and not tp.tarifs_par_classe:
        new_tarifs = {}
        for c in tp.classes_enseignees:
            new_tarifs[str(c).upper()] = 3000 # default fallback
        
        tp.tarifs_par_classe = new_tarifs
        tp.save(update_fields=['tarifs_par_classe'])
        fixed_count += 1
        print(f"Fixed profile ID {tp.id} - Set tarifs to {new_tarifs}")

print(f"Fixed {fixed_count} profiles.")
