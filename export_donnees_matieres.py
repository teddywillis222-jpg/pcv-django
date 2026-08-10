import os
import django
import sys
import csv
from collections import defaultdict

# Initialisation de Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import TeacherProfile

def run_export():
    print("Début de l'analyse des données...")
    teachers = TeacherProfile.objects.prefetch_related('quartiers_couverts').all()
    
    # Dictionnaire pour agréger par matière
    # subject -> {'teachers': set(teacher_ids), 'quartiers': set(quartier_names)}
    subjects_data = defaultdict(lambda: {'teachers': set(), 'quartiers': set()})
    
    for teacher in teachers:
        raw_subjects = teacher.matiere_enseignee
        if not raw_subjects:
            continue
            
        # On sépare par virgule et on nettoie pour avoir des matières propres
        subject_list = [s.strip().capitalize() for s in raw_subjects.split(',') if s.strip()]
        
        # Quartiers couverts par ce professeur
        quartier_names = [q.nom for q in teacher.quartiers_couverts.all()]
        
        for subject in subject_list:
            subjects_data[subject]['teachers'].add(teacher.id)
            for q_name in quartier_names:
                subjects_data[subject]['quartiers'].add(q_name)
                
    output_file = 'analyse_matieres_quartiers.csv'
    
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        # On utilise le point-virgule comme délimiteur pour une ouverture facile dans Excel (version française)
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Matière', 'Nombre de professeurs', 'Nombre de quartiers couverts', 'Liste des quartiers'])
        
        # Tri par nombre de professeurs (décroissant) puis par nom de matière (alphabétique)
        sorted_subjects = sorted(subjects_data.items(), key=lambda x: (-len(x[1]['teachers']), x[0]))
        
        for subject, data in sorted_subjects:
            num_teachers = len(data['teachers'])
            quartiers = sorted(list(data['quartiers']))
            num_quartiers = len(quartiers)
            quartiers_str = ', '.join(quartiers)
            
            writer.writerow([subject, num_teachers, num_quartiers, quartiers_str])
            
    print(f"\n✅ Analyse terminée avec succès !")
    print(f"Les résultats ont été exportés dans le fichier : {output_file}")
    print("\nCe fichier est directement exploitable avec Excel (séparateur point-virgule, encodage UTF-8).")

if __name__ == '__main__':
    run_export()
