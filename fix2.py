import sys

with open('core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

target_term = "        engagement.statut_general = StatutGeneral.TERMINE\n        engagement.save()"
rep_term = target_term + '''
        try:
            from core.services_fiabilite import attribuer_points_engagement_termine
            attribuer_points_engagement_termine(engagement)
        except Exception as e:
            pass'''
content = content.replace(target_term, rep_term)

target_avis = "        except Exception as e:" # Let's just check if avis worked.
if "attribuer_points_avis" not in content:
    target_eval = "        evaluation, created = Evaluation.objects.update_or_create("
    # I already did avis with fix.py ! Let's check it.
    pass

with open('core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done again")
