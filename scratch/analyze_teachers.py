import os
import django
import sys
from collections import Counter

sys.path.append('c:\\Users\\JGA\'TIC BENIN\\Documents\\ProfChezVous')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import TeacherProfile, Quartier

def analyze_data():
    teachers = TeacherProfile.objects.all()
    print(f"Total teachers: {teachers.count()}")
    
    matieres = teachers.values_list('matiere_enseignee', flat=True)
    matiere_counter = Counter(matieres)
    print("\nMatieres count:")
    for matiere, count in matiere_counter.most_common():
        print(f" - {matiere}: {count}")

    print("\nSample neighborhoods for a teacher:")
    sample_teacher = teachers.first()
    if sample_teacher:
        quartiers = sample_teacher.quartiers_couverts.all()
        print(f"{sample_teacher.prenom} {sample_teacher.nom} ({sample_teacher.matiere_enseignee}) covers:")
        for q in quartiers:
            print(f" - {q.nom}")

if __name__ == '__main__':
    analyze_data()
