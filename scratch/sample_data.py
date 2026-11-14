import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import TeacherProfile
from core.choices import ValidationStatus

valides = TeacherProfile.objects.filter(statut_de_validation=ValidationStatus.VALIDE)

print("Exemple de profs validés:")
for p in valides[:3]:
    print("---")
    print("Nom:", p.prenom, p.nom)
    print("Matiere:", p.matiere_enseignee)
    print("Classes enseignées:", p.classes_enseignees)
    print("Classes expertise:", p.classes_expertise)
    print("Modes de cours:", p.modes_de_cours)
    print("Tarif horaire:", p.tarif_horaire)
    print("Tarifs par classe:", p.tarifs_par_classe)
    print("Essai gratuit:", p.essai_gratuit_actif)
    print("Quartiers count:", p.quartiers_couverts.count())
    print("Dispos count:", p.disponibilites.count())
