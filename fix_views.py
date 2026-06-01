import re

with open('core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern for apprenant dashboard block 1
pattern1 = r'# Onglet "En cours" : En attente ou ConfirmÃ©/En cours.*?# Onglet "Essais"\n    engs_essais = engagements\.filter\(type_engagement=EngagementType\.ESSAI\)'

replacement1 = """engs_essais_programmes = engagements.filter(statut_general=StatutGeneral.ESSAI_PROGRAMME)
    engs_essais_confirmes = engagements.filter(statut_general__in=[StatutGeneral.ESSAI_CONFIRME, StatutGeneral.ESSAI_REALISE])
    engs_finalises = engagements.filter(statut_general=StatutGeneral.FINALISE)
    engs_termines = engagements.filter(statut_general=StatutGeneral.TERMINE)
    engagements_tous = engagements.all()"""

# Pattern for apprenant dashboard block 2
pattern2 = r'"engagements_en_cours": engs_en_cours.*?# Annonce \(Parents/Apprenants\)'

replacement2 = """"engagements_essais_programmes": engs_essais_programmes,
        "engagements_essais_confirmes": engs_essais_confirmes,
        "engagements_finalises": engs_finalises,
        "engagements_termines": engs_termines,
        "engagements_tous": engagements_tous,
        "abonnement": abonnement,
        "favoris": favoris,
        "show_welcome_popup": not profile.a_vu_popup_bienvenue,
        "badge_essais_programmes": engs_essais_programmes.count(),
        "badge_essais_confirmes": engs_essais_confirmes.count(),
    }

    # Annonce (Parents/Apprenants)"""

# Only replace in apprenant_dashboard. Let's find def apprenant_dashboard
parts = content.split('def apprenant_dashboard(request):')
if len(parts) > 1:
    before = parts[0]
    after = parts[1]
    
    after = re.sub(pattern1, replacement1, after, flags=re.DOTALL)
    after = re.sub(pattern2, replacement2, after, flags=re.DOTALL)
    
    content = before + 'def apprenant_dashboard(request):' + after

with open('core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
