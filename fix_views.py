import sys

with open('core/views.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
    
new_lines = []
for line in lines:
    if '@staff_member_required' in line:
        break
    new_lines.append(line)

with open('core/views.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
    f.write('''
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

@staff_member_required
def reset_stats_mensuelles(request):
    """
    Reinitialise les statistiques mensuelles des professeurs.
    A executer (en visitant l'URL) le 1er de chaque mois.
    """
    from .models import TeacherProfile
    
    # 1. On compte les profs avant
    count = TeacherProfile.objects.count()
    
    # 2. On met tout a zero en une seule requete optimisee
    TeacherProfile.objects.all().update(
        nb_vues_mois=0,
        nombre_apparitions_mois=0
    )
    
    # 3. Message de confirmation
    html = f"""
    <html>
        <body style="font-family: sans-serif; text-align: center; margin-top: 100px;">
            <h1 style="color: #2e7d32;">&#9989; Statistiques reinitialisees avec succes</h1>
            <p>Les compteurs mensuels (Vues et Apparitions) de <strong>{count} professeurs</strong> ont ete remis a 0.</p>
            <a href="/admin/" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">Retour a l'administration</a>
        </body>
    </html>
    """
    return HttpResponse(html)
''')
