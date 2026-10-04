import sys

with open('core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. api_engagement_action (reactivite)
target1 = "engagement.date_confirmation = timezone.now()"
replacement1 = target1 + """
            try:
                from core.services_fiabilite import attribuer_points_reactivite
                attribuer_points_reactivite(engagement, engagement.date_confirmation)
            except Exception as e:
                pass"""
content = content.replace(target1, replacement1)

# 2. api_ajouter_seance (journal)
target2 = "seance.save()"
replacement2 = target2 + """
        try:
            from core.services_fiabilite import attribuer_points_journal
            attribuer_points_journal(seance)
        except Exception as e:
            pass"""
content = content.replace(target2, replacement2)

# 3. api_demander_cloture (engagement achevé)
target3 = "engagement.statut_general = StatutGeneral.TERMINE\n        engagement.save()"
replacement3 = target3 + """
        try:
            from core.services_fiabilite import attribuer_points_engagement_termine
            attribuer_points_engagement_termine(engagement)
        except Exception as e:
            pass"""
content = content.replace(target3, replacement3)

# 4. api_rate_professeur (avis)
target4 = "evaluation.save()"
replacement4 = target4 + """
        try:
            if created:
                from core.services_fiabilite import attribuer_points_avis
                attribuer_points_avis(evaluation)
        except Exception as e:
            pass"""
content = content.replace(target4, replacement4)

# 5. recherche (algorithme)
target5 = """        sort_args.extend([
            '-profil_complet',
            '-est_certifie',
            '-suivi_rigoureux',
            '-moyenne_avis',
            '-id'
        ])"""
replacement5 = """        sort_args.extend([
            '-est_certifie',
            '-profil_complet',
            '-score_fiabilite',
            '-moyenne_avis',
            '-user__last_login'
        ])"""
content = content.replace(target5, replacement5)

with open('core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Views modify reussi")
