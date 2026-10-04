import sys

with open('core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = '''        evaluation, created = Evaluation.objects.update_or_create(
            parent_evaluateur=request.user,
            professeur_evalue=engagement.professeur,
            defaults={
                'engagement_lie': engagement,
                'note': note,
                'commentaire': commentaire
            }
        )'''

replacement = target + '''
        try:
            if created:
                from core.services_fiabilite import attribuer_points_avis
                attribuer_points_avis(evaluation)
        except Exception as e:
            pass
'''

content = content.replace(target, replacement)
with open('core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
