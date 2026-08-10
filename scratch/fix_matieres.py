import os
import sys
import django
import json

# Configuration de l'environnement Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import Enfant, Apprenant, TeacherProfile

MAPPING = {
    "maths": "Mathématiques (Soutien scolaire général)",
    "math": "Mathématiques (Soutien scolaire général)",
    "mathématiques": "Mathématiques (Soutien scolaire général)",
    "sciences de la vie et de la terre": "SVT (Soutien scolaire général)",
    "svt": "SVT (Soutien scolaire général)",
    "pct": "PCT (Soutien scolaire général)",
    "physique": "PCT (Soutien scolaire général)",
    "chimie": "PCT (Soutien scolaire général)",
    "physique-chimie": "PCT (Soutien scolaire général)",
    "tcf canada": "Français (Préparation aux examens)",
    "commentaire composé": "Français (Préparation aux examens)",
    "contraction de texte": "Français (Préparation aux examens)",
    "français": "Français (Soutien scolaire général)",
    "anglais": "Anglais (Soutien scolaire général)"
}

def clean_matiere_list(matieres_list):
    """Nettoie une liste de matières en utilisant le mapping."""
    if not isinstance(matieres_list, list):
        return matieres_list
    
    cleaned = []
    for m in matieres_list:
        m_lower = m.lower().strip()
        # On cherche si on a un mapping direct
        if m_lower in MAPPING:
            cleaned.append(MAPPING[m_lower])
        else:
            # Sinon on garde la valeur d'origine
            cleaned.append(m)
            
    # Déduplication
    return list(dict.fromkeys(cleaned))

def run():
    print("Mise à jour des profils Enfant...")
    enfants = Enfant.objects.all()
    count_enfants = 0
    for enfant in enfants:
        old_val = enfant.matieres
        new_val = clean_matiere_list(enfant.matieres)
        if old_val != new_val:
            enfant.matieres = new_val
            enfant.save(update_fields=['matieres'])
            count_enfants += 1
    print(f"{count_enfants} profils Enfant mis à jour.")

    print("\nMise à jour des profils Apprenant...")
    apprenants = Apprenant.objects.all()
    count_apprenants = 0
    for apprenant in apprenants:
        old_val = apprenant.matieres_recherchees
        new_val = clean_matiere_list(apprenant.matieres_recherchees)
        if old_val != new_val:
            apprenant.matieres_recherchees = new_val
            apprenant.save(update_fields=['matieres_recherchees'])
            count_apprenants += 1
    print(f"{count_apprenants} profils Apprenant mis à jour.")

    print("\nMise à jour des profils Professeurs...")
    profs = TeacherProfile.objects.all()
    count_profs = 0
    for prof in profs:
        old_val = prof.matiere_enseignee
        if old_val:
            # matière_enseignee est une string séparée par des virgules
            mat_list = [m.strip() for m in old_val.split(',') if m.strip()]
            new_list = clean_matiere_list(mat_list)
            new_val = ", ".join(new_list)
            if old_val != new_val:
                prof.matiere_enseignee = new_val
                prof.save(update_fields=['matiere_enseignee'])
                count_profs += 1
    print(f"{count_profs} profils Professeurs mis à jour.")

if __name__ == "__main__":
    run()
