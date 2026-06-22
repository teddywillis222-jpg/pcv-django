import os, sys, django
sys.path.append(r"C:\Users\JGA'TIC BENIN\Documents\ProfChezVous")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import CustomChoice

total = CustomChoice.objects.filter(category='matiere').count()
print(f"Nombre total de matières dans CustomChoice : {total}")
print("--- Aperçu (20 premières) ---")
for c in CustomChoice.objects.filter(category='matiere').order_by('value')[:20]:
    print(f"  • {c.value}")
print("...")
print("--- Aperçu (20 dernières) ---")
for c in CustomChoice.objects.filter(category='matiere').order_by('-value')[:20]:
    print(f"  • {c.value}")
