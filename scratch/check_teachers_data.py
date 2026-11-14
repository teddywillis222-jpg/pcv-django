import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import TeacherProfile, Quartier
from core.choices import ValidationStatus
from django.db.models import Count

print("=== STATISTIQUES GLOBALES BASE ===")
total = TeacherProfile.objects.count()
print(f"Total professeurs inscrits: {total}")

valides = TeacherProfile.objects.filter(statut_de_validation=ValidationStatus.VALIDE)
print(f"Professeurs VALIDÉS (visibles/actifs): {valides.count()}")

en_attente = TeacherProfile.objects.filter(statut_de_validation=ValidationStatus.EN_ATTENTE)
print(f"Professeurs EN ATTENTE: {en_attente.count()}")

incomplets = TeacherProfile.objects.filter(statut_de_validation=ValidationStatus.INCOMPLET)
print(f"Professeurs INCOMPLETS: {incomplets.count()}")

suspendus = TeacherProfile.objects.filter(statut_de_validation=ValidationStatus.SUSPENDU)
print(f"Professeurs SUSPENDUS: {suspendus.count()}")

refuses = TeacherProfile.objects.filter(statut_de_validation=ValidationStatus.REFUSE)
print(f"Professeurs REFUSÉS: {refuses.count()}")

print(f"\nProfils complets à 100%: {TeacherProfile.objects.filter(profil_complet=True).count()}")
print(f"Profs avec essai gratuit actif: {TeacherProfile.objects.filter(essai_gratuit_actif=True).count()}")
print(f"Profs certifiés: {TeacherProfile.objects.filter(est_certifie=True).count()}")

# Analyse parmi les professeurs validés ou actifs
print("\n=== TOP MATIERES (SUR VALIDÉS) ===")
matieres = {}
for p in valides:
    if p.matiere_enseignee:
        for m in [x.strip().capitalize() for x in p.matiere_enseignee.split(',') if x.strip()]:
            matieres[m] = matieres.get(m, 0) + 1
for m, c in sorted(matieres.items(), key=lambda x: -x[1])[:15]:
    print(f"  {m}: {c}")

print("\n=== VILLES ET QUARTIERS (SUR VALIDÉS) ===")
from collections import Counter
villes = Counter()
quartiers = Counter()
for p in valides.prefetch_related('quartiers_couverts'):
    for q in p.quartiers_couverts.all():
        quartiers[f"{q.nom} ({q.ville})"] += 1
        villes[q.ville] += 1

print("Top 10 Villes:")
for v, c in villes.most_common(10):
    print(f"  {v}: {c} profs")

print("Top 10 Quartiers:")
for q, c in quartiers.most_common(10):
    print(f"  {q}: {c} profs")
