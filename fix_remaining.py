import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('core/views.py', 'r', encoding='utf-8') as f:
    text = f.read()

changes = 0

# 1. Journal trigger
t = "seance.validee = True\n\n    seance.save()\n\n    return JsonResponse"
r = """seance.validee = True

    seance.save()

    try:
        from .services_fiabilite import attribuer_points_journal
        attribuer_points_journal(seance)
    except Exception:
        pass

    return JsonResponse"""
if 'attribuer_points_journal' not in text:
    if t in text:
        text = text.replace(t, r)
        changes += 1
        print("[OK] trigger journal")
    else:
        print("[ERREUR] journal: cible introuvable")

# 2. Engagement terminé
t = "engagement.statut_general = StatutGeneral.TERMINE\n\n        engagement.save()\n\n        return JsonResponse"
r = """engagement.statut_general = StatutGeneral.TERMINE

        engagement.save()

        try:
            from .services_fiabilite import attribuer_points_engagement_termine
            attribuer_points_engagement_termine(engagement)
        except Exception:
            pass

        return JsonResponse"""
if 'attribuer_points_engagement_termine' not in text:
    if t in text:
        text = text.replace(t, r)
        changes += 1
        print("[OK] trigger engagement terminé")
    else:
        print("[ERREUR] engagement terminé: cible introuvable")

# 3. Avis
t = "evaluation, created = Evaluation.objects.update_or_create(\n\n            parent_evaluateur=request.user,\n\n            professeur_evalue=engagement.professeur,\n\n            defaults={\n\n                'engagement_lie': engagement,\n\n                'note': note,\n\n                'commentaire': commentaire\n\n            }\n\n        )\n\n        \n\n        return JsonResponse"
r = """evaluation, created = Evaluation.objects.update_or_create(

            parent_evaluateur=request.user,

            professeur_evalue=engagement.professeur,

            defaults={

                'engagement_lie': engagement,

                'note': note,

                'commentaire': commentaire

            }

        )

        if created:
            try:
                from .services_fiabilite import attribuer_points_avis
                attribuer_points_avis(evaluation)
            except Exception:
                pass

        return JsonResponse"""
if 'attribuer_points_avis' not in text:
    if t in text:
        text = text.replace(t, r)
        changes += 1
        print("[OK] trigger avis")
    else:
        print("[ERREUR] avis: cible introuvable")

# 4. Post signup (double blank lines)
t2 = 'return redirect("prof_intro")'
r2 = 'return redirect("prof_create_profile")'
if t2 in text:
    text = text.replace(t2, r2)
    changes += 1
    print("[OK] redirect prof_create_profile")

with open('core/views.py', 'w', encoding='utf-8') as f:
    f.write(text)

print(f"\n[TOTAL] {changes} corrections supplémentaires appliquées")
