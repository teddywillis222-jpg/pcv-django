import re

with open('core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''@login_required
def finalisation_engagement(request, engagement_id):
    engagement = get_object_or_404(Engagement, id=engagement_id)
    
    # Vérification des droits d'accès
    if engagement.parent_apprenant != request.user:
        return redirect('home')
        
    if engagement.statut_general in [StatutGeneral.FINALISE, StatutGeneral.ENGAGEMENT_FINALISE]:
        return redirect('parent_dashboard')
        
    if request.method == "POST":
        engagement.matiere = request.POST.get('matiere', engagement.matiere)
        engagement.classe = request.POST.get('classe', engagement.classe)
        engagement.mode_de_cours = request.POST.get('mode_de_cours', engagement.mode_de_cours)
        
        if engagement.mode_de_cours == 'en_ligne':
            engagement.plateforme_visio_preferee = request.POST.get('localisation_plateforme', engagement.plateforme_visio_preferee)
        else:
            engagement.localisation_option = request.POST.get('localisation_plateforme', engagement.localisation_option)
            
        engagement.frequence_hebdomadaire = request.POST.get('frequence_hebdomadaire', engagement.frequence_hebdomadaire)
        engagement.duree_seance = request.POST.get('duree_seance', engagement.duree_seance)
        
        duree_mois = request.POST.get('duree_mois')
        if duree_mois and duree_mois.isdigit():
            engagement.duree_mois = int(duree_mois)
            
        date_debut_str = request.POST.get('date_debut')
        if date_debut_str:
            from django.utils.dateparse import parse_date
            parsed = parse_date(date_debut_str)
            if parsed:
                engagement.date_debut = parsed
                
        enfant_id = request.POST.get('enfant_id')
        if enfant_id and str(enfant_id).isdigit():
            from .models import Enfant
            try:
                enfant = Enfant.objects.get(id=int(enfant_id))
                if hasattr(request.user, 'parent') and enfant.parent == request.user.parent:
                    engagement.enfants_concernes.clear()
                    engagement.enfants_concernes.add(enfant)
            except Enfant.DoesNotExist:
                pass
                
        engagement.statut_general = StatutGeneral.FINALISE
        engagement.type_engagement = EngagementType.NORMAL
        engagement.save()
        return redirect('parent_dashboard')

    context = {
        'engagement': engagement,
        'professeur': engagement.professeur,
        'enfants': request.user.parent.enfants.all() if hasattr(request.user, 'parent') else []
    }
    return render(request, 'core/finalisation_engagement.html', context)'''

content = re.sub(r'@login_required\ndef finalisation_engagement\(request, engagement_id\):.*?(?=def |\Z)', replacement + '\n\n', content, flags=re.DOTALL)

with open('core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
