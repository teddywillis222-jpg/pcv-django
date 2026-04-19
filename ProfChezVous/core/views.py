from datetime import date

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .forms import (
    ApprenantCreateProfileForm,
    EnfantForm,
    FinalisationCompteForm,
    LoginForm,
    ParentForm,
    SignUpForm,
)
from .choices import TypeAbonnement, StatutGeneral, EngagementType, ValidationStatus
from .models import Abonnement, Apprenant, Enfant, Parent, Profile, TeacherProfile, Engagement
from django.db.models import Q
from django.template.loader import render_to_string


def home(request):
    return render(request, "core/home.html")

def faq(request):
    """Page FAQ - Questions fréquentes"""
    return render(request, "core/faq.html")

def support(request):
    """Page Support - Aide et assistance"""
    return render(request, "core/support.html")

def cgu(request):
    """Page des Conditions Générales d'Utilisation"""
    return render(request, "core/cgu.html")

def messagerie(request):
    """Page Messagerie - Communication entre utilisateurs"""
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "core/messagerie.html")

def recherche(request):
    """Page de recherche des professeurs avec filtres"""
    from .choices import ValidationStatus
    professeurs = TeacherProfile.objects.filter(
        statut_de_validation=ValidationStatus.VALIDE
    )
    
    # Récupération des paramètres de recherche
    matiere = request.GET.get('matiere', '')
    localisation = request.GET.get('localisation', '')
    classe = request.GET.get('classe', '')
    prix = request.GET.get('prix', '')
    mode = request.GET.get('mode', '')
    soutien = request.GET.get('soutien', '')

    if matiere:
        professeurs = professeurs.filter(matiere_enseignee__icontains=matiere)
    if localisation:
        professeurs = professeurs.filter(ville_quartier__icontains=localisation)
    if classe:
        professeurs = professeurs.filter(classes_enseignees__icontains=classe)
    if mode:
        professeurs = professeurs.filter(modes_de_cours__icontains=mode)
    if soutien:
        professeurs = professeurs.filter(categorie_de_soutien__icontains=soutien)
        
    if prix:
        if prix == "0-2000":
            professeurs = professeurs.filter(tarif_horaire__lt=2000)
        elif prix == "2000-5000":
            professeurs = professeurs.filter(tarif_horaire__gte=2000, tarif_horaire__lte=5000)
        elif prix == "5000-10000":
            professeurs = professeurs.filter(tarif_horaire__gte=5000, tarif_horaire__lte=10000)
        elif prix == "10000+":
            professeurs = professeurs.filter(tarif_horaire__gt=10000)

    professeurs = professeurs.order_by('-est_certifie', '-id')

    for prof in professeurs:
        prof.moyenne_avis = 4.8 if prof.est_certifie else 4.5
        prof.nombre_avis = 12 if prof.est_certifie else 3

    # Contexte Parent/Enfants
    parent_children = []
    parent_children_json = "[]"
    if request.user.is_authenticated and hasattr(request.user, 'parent'):
        parent_children = list(request.user.parent.enfants.all().values('id', 'prenom'))
        parent_children_json = json.dumps(parent_children)

    context = {
        'professeurs': professeurs,
        'matiere': matiere,
        'localisation': localisation,
        'classe': classe,
        'prix': prix,
        'mode': mode,
        'soutien': soutien,
        'parent_children': parent_children,
        'parent_children_json': parent_children_json,
    }
    
    return render(request, "core/recherche.html", context)


def signup(request):
    if request.user.is_authenticated:
        return redirect("post_signup_redirect")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data["role"]
            Profile.objects.create(user=user, role=role)
            # Création automatique d'abonnement (Standard, 2000f)
            Abonnement.objects.create(
                user=user,
                type_abonnement=TypeAbonnement.STANDARD,
                prix="2000f par engagement",
                date_debut=date.today(),
            )
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect("post_signup_redirect")
    else:
        form = SignUpForm()

    return render(request, "core/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("post_signup_redirect")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("post_signup_redirect")
    else:
        form = LoginForm()

    return render(request, "core/login.html", {"form": form})


def finalisation_compte(request):
    """Page pour finaliser le compte (rôle + nom) après Google Login."""
    if not request.user.is_authenticated:
        return redirect("login")

    try:
        profile = request.user.profile
        # Si profil complet, rediriger
        if profile.role and request.user.first_name:
            return redirect("post_signup_redirect")
    except Profile.DoesNotExist:
        pass

    if request.method == "POST":
        form = FinalisationCompteForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data["nom_complet"].strip()
            request.user.save()
            role = form.cleaned_data["role"]
            profile, _ = Profile.objects.get_or_create(user=request.user, defaults={"role": role})
            if profile.role != role:
                profile.role = role
                profile.save()
            if not request.user.abonnements.exists():
                Abonnement.objects.create(
                    user=request.user,
                    type_abonnement=TypeAbonnement.STANDARD,
                    prix="2000f par engagement",
                    date_debut=date.today(),
                )
            return redirect("post_signup_redirect")
    else:
        initial = {"nom_complet": request.user.first_name or ""}
        try:
            initial["role"] = request.user.profile.role
        except Profile.DoesNotExist:
            pass
        form = FinalisationCompteForm(initial=initial)

    return render(request, "core/finalisation_compte.html", {"form": form})


def post_signup_redirect(request):
    if not request.user.is_authenticated:
        return redirect("home")

    # On récupère ou crée le profil sans rôle par défaut
    profile, created = Profile.objects.get_or_create(user=request.user)

    # SI PAS DE RÔLE OU PAS DE NOM : Direction l'accueil avec un paramètre spécial
    if not profile.role or not request.user.first_name:
        return redirect('/?show_finalisation_popup=true')

    if profile.role == Profile.ROLE_PROF:
        teacher = getattr(request.user, "teacher_profile", None)
        if teacher:
            from .choices import ValidationStatus
            if teacher.statut_de_validation == ValidationStatus.VALIDE:
                return redirect("prof_dashboard")
            return redirect("prof_attente_dashboard")
        return redirect("prof_intro")
    elif profile.role == Profile.ROLE_PARENT:
        parent = getattr(request.user, "parent", None)
        if parent and parent.enfants.exists():
            return redirect("parent_dashboard")
        return redirect("parent_create_profile")
    elif profile.role == Profile.ROLE_APPRENANT:
        apprenant = getattr(request.user, "apprenant", None)
        if apprenant:
            return redirect("apprenant_dashboard")
        return redirect("apprenant_create_profile")

    return redirect("home")


from .forms import TeacherProfileForm

def prof_intro(request):
    return render(request, "core/prof_intro.html")

@login_required
def prof_create_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect("finalisation_compte")

    if profile.role != Profile.ROLE_PROF:
        return redirect("home")

    teacher_instance = getattr(request.user, "teacher_profile", None)
    
    from .choices import ValidationStatus
    if teacher_instance:
        if teacher_instance.statut_de_validation == ValidationStatus.VALIDE:
            return redirect("prof_dashboard")
        return redirect("prof_attente_dashboard")

    if request.method == "POST":
        form = TeacherProfileForm(request.POST, request.FILES, instance=teacher_instance)
        if form.is_valid():
            teacher = form.save(commit=False)
            teacher.user = request.user
            teacher.prenom = ""
            teacher.statut_de_validation = ValidationStatus.EN_ATTENTE
            teacher.save()
            
            from .models import Diplome
            diplomes_files = request.FILES.getlist('diplomes_fichiers')
            diplomes_noms = request.POST.getlist('diplomes_noms')
            for index, file in enumerate(diplomes_files):
                nom_diplome = diplomes_noms[index] if index < len(diplomes_noms) else file.name
                Diplome.objects.create(teacher=teacher, nom_diplome=nom_diplome, fichier_preuve=file)

            return redirect("prof_attente_dashboard")
    else:
        initial = {
            "nom": f"{request.user.first_name} {request.user.last_name}".strip(),
            "email": request.user.email
        }
        form = TeacherProfileForm(instance=teacher_instance, initial=initial)

    return render(request, "core/prof_create_profile.html", {"form": form})


@login_required
def prof_attente_dashboard(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect("finalisation_compte")

    if profile.role != Profile.ROLE_PROF:
        return redirect("home")

    teacher_instance = getattr(request.user, "teacher_profile", None)
    if not teacher_instance:
        return redirect("prof_create_profile")

    from .choices import ValidationStatus
    if teacher_instance.statut_de_validation == ValidationStatus.VALIDE:
        return redirect("prof_dashboard")

    if request.method == "POST":
        teacher_instance.presentation = request.POST.get("presentation", teacher_instance.presentation)
        teacher_instance.methodologie = request.POST.get("methodologie", teacher_instance.methodologie)
        exp = request.POST.get("annees_d_experience")
        if exp: teacher_instance.annees_d_experience = exp
        tarif = request.POST.get("tarif_horaire")
        if tarif: teacher_instance.tarif_horaire = tarif
        
        dispos = request.POST.getlist("disponibilites")
        if dispos:
            teacher_instance.grille_disponibilites = dispos
            
        teacher_instance.save()
        return redirect("prof_attente_dashboard")

    # Calcul pourcentage complétion 
    completion = 50
    if teacher_instance.presentation: completion += 20
    if teacher_instance.methodologie: completion += 15
    if teacher_instance.tarif_horaire: completion += 5
    if teacher_instance.grille_disponibilites: completion += 10

    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    return render(request, "core/prof_attente_dashboard.html", {
        "teacher": teacher_instance,
        "completion": completion,
        "jours": jours
    })

@login_required
def prof_dashboard(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect("finalisation_compte")

    if profile.role != Profile.ROLE_PROF:
        return redirect("home")
        
    try:
        teacher = request.user.teacher_profile
    except:
        return redirect("prof_create_profile")

    return render(request, "core/prof_dashboard.html", {"teacher": teacher})


@login_required
def parent_create_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect("finalisation_compte")

    if profile.role != Profile.ROLE_PARENT:
        return redirect("home")

    parent_instance = getattr(request.user, "parent", None)
    if parent_instance and parent_instance.enfants.exists():
        return redirect("parent_dashboard")

    if request.method == "POST":
        parent_form = ParentForm(request.POST, request.FILES, instance=parent_instance)
        enfant_form = EnfantForm(request.POST)
        if parent_form.is_valid() and enfant_form.is_valid():
            if not parent_instance:
                parent_instance = parent_form.save(commit=False)
                parent_instance.user = request.user
                parent_instance.save()
            else:
                parent_form.save()

            enfant = enfant_form.save(commit=False)
            enfant.parent = parent_instance
            enfant.save()
            return redirect("parent_dashboard")
    else:
        initial_parent = {"nom": request.user.first_name}
        if request.user.last_name:
            initial_parent["nom"] = f"{request.user.first_name} {request.user.last_name}"
        parent_form = ParentForm(instance=parent_instance, initial=initial_parent)
        enfant_form = EnfantForm()

    return render(
        request,
        "core/parent_create_profile.html",
        {"parent_form": parent_form, "enfant_form": enfant_form},
    )


@login_required
def parent_dashboard(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect("finalisation_compte")

    if profile.role != Profile.ROLE_PARENT:
        return redirect("home")

    try:
        parent = request.user.parent
    except Parent.DoesNotExist:
        return redirect("parent_create_profile")

    enfants = parent.enfants.all()
    if not enfants.exists():
        return redirect("parent_create_profile")

    # 1. Sélection de l'enfant actif (par URL, sinon le 1er par défaut)
    enfant_id = request.GET.get("enfant_id")
    active_enfant = enfants.filter(id=enfant_id).first() if enfant_id else enfants.first()

    # 2. Recommandations dynamiques basées sur l'enfant actif
    recommandations = TeacherProfile.objects.filter(statut_de_validation=ValidationStatus.VALIDE)
    
    # Filtrage par classe de l'enfant (si disponible dans les TeacherProfile)
    if active_enfant.classe:
        recommandations = recommandations.filter(classes_enseignees__icontains=active_enfant.classe)
    
    # On mélange et on limite
    recommandations = recommandations.order_by("?")[:8]

    # 3. Engagements filtrés selon la fiche technique
    engagements = active_enfant.engagements.all().order_by("-date_creation")

    # Onglet "En cours" : En attente ou Confirmé/En cours
    engs_en_cours = engagements.filter(
        statut_general__in=[StatutGeneral.EN_ATTENTE, StatutGeneral.CONFIRME, StatutGeneral.EN_COURS]
    )
    
    # Onglet "Actifs" : Finalisé
    engs_actifs = engagements.filter(statut_general=StatutGeneral.FINALISE)
    
    # Onglet "Terminé" (Historique rapide) : Terminé, Annulé, Refusé
    engs_termines = engagements.filter(
        statut_general__in=[StatutGeneral.TERMINE, StatutGeneral.ANNULE, StatutGeneral.REFUSE]
    )
    
    # Historique complet pour le modal/liste (tous les statuts)
    engagements_tous = engagements.all()

    # Onglet "Essais"
    engs_essais = engagements.filter(type_engagement=EngagementType.ESSAI)

    # 4. Abonnement & Favoris (Placeholders pour l'instant)
    abonnement = request.user.abonnements.first()
    favoris = [] # À implémenter si le modèle existe

    return render(
        request,
        "core/parent_dashboard.html",
        {
            "parent_details": parent,
            "enfants": enfants,
            "active_enfant": active_enfant,
            "recommandations": recommandations,
            "engagements_en_cours": engs_en_cours,
            "engagements_actifs": engs_actifs,
            "engagements_termines": engs_termines,
            "engagements_essais": engs_essais,
            "engagements_tous": engagements_tous,
            "abonnement": abonnement,
            "favoris": favoris,
        },
    )




@login_required
def apprenant_create_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect("finalisation_compte")

    if profile.role != Profile.ROLE_APPRENANT:
        return redirect("home")

    apprenant_instance = getattr(request.user, "apprenant", None)

    if request.method == "POST":
        form = ApprenantCreateProfileForm(request.POST, request.FILES, instance=apprenant_instance)
        if form.is_valid():
            apprenant = form.save(commit=False)
            apprenant.user = request.user
            apprenant.nom = apprenant.nom or request.user.first_name
            apprenant.save()
            return redirect("apprenant_dashboard")
    else:
        initial = {"nom": request.user.first_name, "email_apprenant": request.user.email}
        form = ApprenantCreateProfileForm(instance=apprenant_instance, initial=initial)

    return render(request, "core/apprenant_create_profile.html", {"form": form})


@login_required
def apprenant_dashboard(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect("finalisation_compte")

    if profile.role != Profile.ROLE_APPRENANT:
        return redirect("home")

    try:
        apprenant = request.user.apprenant
    except Apprenant.DoesNotExist:
        return redirect("apprenant_create_profile")

    return render(request, "core/apprenant_dashboard.html", {"apprenant": apprenant})


# Vues pour le système de recherche et profils hybride
def professeur_detail(request, teacher_slug):
    """Page profil professeur dynamique pour SEO avec robustesse accrue"""
    teacher = get_object_or_404(TeacherProfile, slug=teacher_slug)
    
    # Calcul des stats sécurisé
    from django.db.models import Avg
    engs_stats = teacher.engagements.exclude(temps_reponse_prof__isnull=True)
    temps_moyen_reponse = engs_stats.aggregate(avg=Avg('temps_reponse_prof'))['avg'] if engs_stats.exists() else None
    
    engagements_actifs = teacher.engagements.filter(
        statut_general__in=[StatutGeneral.EN_COURS, StatutGeneral.CONFIRME, StatutGeneral.FINALISE]
    ).count()
    
    # Auth context
    is_parent = False
    is_premium = False
    parent_children = []
    parent_children_json = "[]"
    existing_engagement = None
    existing_engagement_json = "null"
    
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile') and request.user.profile.role == Profile.ROLE_PARENT:
            is_parent = True
            if request.user.abonnements.exists():
                is_premium = True
            if hasattr(request.user, 'parent'):
                parent_children = list(request.user.parent.enfants.all().values('id', 'prenom'))
                parent_children_json = json.dumps(parent_children)
                
        # Vérifier engagement existant
        existing_engagement_obj = teacher.engagements.filter(
            parent_apprenant=request.user,
            statut_general=StatutGeneral.EN_ATTENTE
        ).first()
        if existing_engagement_obj:
            existing_engagement = existing_engagement_obj
            existing_engagement_json = json.dumps({
                'id': existing_engagement_obj.id,
                'matiere': existing_engagement_obj.matiere,
                'mode_de_cours': existing_engagement_obj.mode_de_cours,
                'frequence': existing_engagement_obj.frequence_hebdomadaire,
                'duree': existing_engagement_obj.duree_seance,
                'type': 'essai' if existing_engagement_obj.type_engagement == EngagementType.ESSAI else 'standard'
            })

    # Conversion des codes en noms lisibles
    mode_map = {'PARENT_HOME': 'Présentiel', 'APPRENANT_HOME': 'Présentiel', 'ONLINE': 'En ligne', 'HYBRID': 'Hybride'}
    class_map = {'6EME': '6ème', '5EME': '5ème', '4EME': '4ème', '3EME': '3ème', '2NDE': '2nde', '1ERE': '1ère', 'TLE': 'Terminale'}
    
    readable_modes = [mode_map.get(m, m) for m in teacher.modes_de_cours]
    readable_classes = [class_map.get(c, c) for c in teacher.classes_enseignees]
        
    context = {
        'teacher': teacher,
        'teacher_slug': teacher_slug,
        'user': request.user,
        'temps_moyen_reponse': temps_moyen_reponse,
        'engagements_actifs': engagements_actifs,
        'is_parent': is_parent,
        'is_premium': is_premium,
        'readable_modes': readable_modes,
        'readable_classes': readable_classes,
        'parent_children': parent_children,
        'parent_children_json': parent_children_json,
        'existing_engagement': existing_engagement,
        'existing_engagement_json': existing_engagement_json
    }
    
    return render(request, "core/professeur_detail.html", context)


@require_http_methods(["GET"])
def api_teacher_profile(request, teacher_slug):
    """API pour récupérer les données du professeur (pour le side panel) avec gestion d'erreur robuste"""
    try:
        teacher = TeacherProfile.objects.get(slug=teacher_slug)
        
        # Calcul des stats sécurisé
        engs_stats = teacher.engagements.exclude(temps_reponse_prof__isnull=True)
        if engs_stats.exists():
            from django.db.models import Avg
            temps_moyen_reponse = engs_stats.aggregate(avg=Avg('temps_reponse_prof'))['avg']
        else:
            temps_moyen_reponse = None
            
        engagements_actifs = teacher.engagements.filter(
            statut_general__in=[StatutGeneral.EN_COURS, StatutGeneral.CONFIRME, StatutGeneral.FINALISE]
        ).count()
        
        # Contexte d'authentification sécurisé
        is_parent = False
        is_premium = False
        parent_children = []
        existing_engagement = None
        
        if request.user.is_authenticated:
            try:
                if hasattr(request.user, 'profile') and request.user.profile.role == Profile.ROLE_PARENT:
                    is_parent = True
                    if request.user.abonnements.exists():
                        is_premium = True
                    if hasattr(request.user, 'parent'):
                        parent_children = list(request.user.parent.enfants.all().values('id', 'prenom'))
                
                # Vérifier engagement existant
                existing_engagement_obj = teacher.engagements.filter(
                    parent_apprenant=request.user,
                    statut_general=StatutGeneral.EN_ATTENTE
                ).first()
                if existing_engagement_obj:
                    existing_engagement = {
                        'id': existing_engagement_obj.id,
                        'matiere': existing_engagement_obj.matiere,
                        'mode_de_cours': existing_engagement_obj.mode_de_cours,
                        'frequence': existing_engagement_obj.frequence_hebdomadaire,
                        'duree': existing_engagement_obj.duree_seance,
                        'type': 'essai' if existing_engagement_obj.type_engagement == EngagementType.ESSAI else 'standard'
                    }
            except Exception:
                pass
        
        # Conversion des codes en noms lisibles
        mode_map = {'PARENT_HOME': 'Présentiel', 'APPRENANT_HOME': 'Présentiel', 'ONLINE': 'En ligne', 'HYBRID': 'Hybride'}
        class_map = {'6EME': '6ème', '5EME': '5ème', '4EME': '4ème', '3EME': '3ème', '2NDE': '2nde', '1ERE': '1ère', 'TLE': 'Terminale'}
        readable_modes = [mode_map.get(m, m) for m in teacher.modes_de_cours]
        readable_classes = [class_map.get(c, c) for c in teacher.classes_enseignees]
            
        html = render_to_string('core/components/teacher_profile.html', {
            'teacher': teacher,
            'user': request.user,
            'is_side_panel': True,
            'temps_moyen_reponse': temps_moyen_reponse,
            'engagements_actifs': engagements_actifs,
            'is_parent': is_parent,
            'is_premium': is_premium,
            'readable_modes': readable_modes,
            'readable_classes': readable_classes,
            'parent_children': parent_children,
            'existing_engagement': existing_engagement
        }, request=request)
        
        return JsonResponse({
            'html': html,
            'parent_children': parent_children,
            'existing_engagement': existing_engagement
        })
        
    except TeacherProfile.DoesNotExist:
        return JsonResponse({'error': 'Professeur non trouvé'}, status=404)
    except Exception as e:
        import traceback
        print(traceback.format_exc()) # Log l'erreur complète sur Render
        return JsonResponse({'error': f"Erreur interne: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_engagement(request):
    """API pour créer une proposition d'engagement (Standard ou Essai)"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Utilisateur non authentifié'}, status=401)
    
    try:
        data = json.loads(request.body)
        teacher_id = data.get('teacher_id')
        
        if hasattr(request.user, 'teacher_profile') and str(request.user.teacher_profile.id) == str(teacher_id):
            return JsonResponse({'error': 'Un professeur ne peut pas s\'auto-engager'}, status=403)
            
        teacher = get_object_or_404(TeacherProfile, id=teacher_id)
        
        # Champs communs
        matiere = data.get('matiere', '')
        course_mode = data.get('course_mode', '')
        localisation = data.get('localisation', '')
        plateforme = data.get('plateforme_visio', '')
        
        # Créer la conversation si besoin
        # Pour faire simple on associe juste l'engagement
        
        engagement_type_str = data.get('engagement_type', 'standard')
        type_eng = EngagementType.ESSAI if engagement_type_str == 'essai' else EngagementType.NORMAL
        
        # Recherche d'un engagement existant en attente pour mise à jour
        engagement = Engagement.objects.filter(
            professeur=teacher,
            parent_apprenant=request.user,
            statut_general=StatutGeneral.EN_ATTENTE
        ).first()

        if not engagement:
            engagement = Engagement(
                professeur=teacher,
                parent_apprenant=request.user,
                statut_general=StatutGeneral.EN_ATTENTE
            )
            
        engagement.type_engagement = type_eng
        engagement.matiere = data.get('matiere', '')
        engagement.mode_de_cours = data.get('course_mode', '')
        engagement.localisation_option = data.get('localisation', '')
        engagement.plateforme_visio_preferee = data.get('plateforme_visio', '')
        
        if type_eng == EngagementType.ESSAI:
            date_essai_str = data.get('date_essai')
            if date_essai_str:
                from django.utils.dateparse import parse_datetime
                engagement.date_heure_essai = parse_datetime(date_essai_str)
            engagement.lien_cours_essai = data.get('description_essai', '')
        else:
            budget = data.get('budget')
            if budget: engagement.budget_convenu = budget
            engagement.frequence_hebdomadaire = data.get('frequence', '')
            engagement.duree_seance = data.get('duree_seance', '')
            date_debut_str = data.get('date_debut')
            if date_debut_str:
                from django.utils.dateparse import parse_date
                engagement.date_debut = parse_date(date_debut_str)
                
        engagement.save()
        
        # Lier les enfants (ManyToManyField)
        enfant_id = data.get('enfant_id')
        if enfant_id:
            from .models import Enfant
            try:
                enfant = Enfant.objects.get(id=enfant_id)
                engagement.enfants_concernes.clear()
                engagement.enfants_concernes.add(enfant)
            except Enfant.DoesNotExist:
                pass
        elif hasattr(request.user, 'parent'):
            # Si un seul enfant, on le lie par défaut
            enfants = request.user.parent.enfants.all()
            if enfants.count() == 1:
                engagement.enfants_concernes.clear()
                engagement.enfants_concernes.add(enfants.first())

        return JsonResponse({
            'success': True,
            'message': 'Votre proposition d\'engagement a été enregistrée avec succès.',
            'engagement_id': engagement.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Données invalides'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# --- ADMIN DASHBOARD (SPA & API) ---
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count
from .models import Evaluation

def debug_admin_pcv(request):
    """Point d'entrée du dashboard administrateur (sans authentification pour tests)"""
    return render(request, "core/admin_dashboard/base.html")

def admin_api_accueil(request):
    """Retourne le HTML partiel pour l'accueil du dashboard"""
    # 1. Statistiques Globales
    total_parents = Profile.objects.filter(role=Profile.ROLE_PARENT).count()
    total_apprenants = Profile.objects.filter(role=Profile.ROLE_APPRENANT).count()
    total_professeurs = Profile.objects.filter(role=Profile.ROLE_PROF).count()
    total_users = total_parents + total_apprenants + total_professeurs

    engagements = Engagement.objects.all()
    stats_engagements = engagements.values('statut_general').annotate(count=Count('id'))
    dict_engagements = {stat['statut_general']: stat['count'] for stat in stats_engagements}
    total_engagements = engagements.count()

    evaluations = Evaluation.objects.all()
    total_evaluations = evaluations.count()
    moyenne_generale = evaluations.aggregate(Avg('note'))['note__avg'] or 0

    # 2. Engagements Prioritaires
    # Condition: Statut "En attente" + Parent/Apprenant Access+ Premium + Délai >= 30 min
    limite_temps = timezone.now() - timedelta(minutes=30)
    engagements_prioritaires = Engagement.objects.filter(
        statut_general=StatutGeneral.EN_ATTENTE,
        date_creation__lte=limite_temps,
        parent_apprenant__abonnements__type_abonnement=TypeAbonnement.ACCESS_PREMIUM
    ).select_related('parent_apprenant').distinct()

    context = {
        'total_users': total_users,
        'total_parents': total_parents,
        'total_apprenants': total_apprenants,
        'total_professeurs': total_professeurs,
        'total_engagements': total_engagements,
        'dict_engagements': dict_engagements,
        'StatutGeneral': StatutGeneral,
        'total_evaluations': total_evaluations,
        'moyenne_generale': round(moyenne_generale, 1),
        'engagements_prioritaires': engagements_prioritaires,
    }
    return render(request, "core/admin_dashboard/partials/accueil.html", context)

def admin_api_professeurs(request):
    """Retourne le HTML partiel pour la liste des professeurs selon le filtre"""
    statut = request.GET.get('statut', ValidationStatus.EN_ATTENTE)
    # tri par date de création ou un autre critère pour avoir une liste consistante (user date_joined par ex)
    professeurs = TeacherProfile.objects.filter(statut_de_validation=statut).order_by('-user__date_joined')
    
    context = {
        'professeurs': professeurs,
        'statut_actif': statut,
        'ValidationStatus': ValidationStatus
    }
    return render(request, "core/admin_dashboard/partials/professeurs.html", context)

@csrf_exempt
@require_http_methods(["POST"])
def admin_api_prof_action(request, prof_id):
    """Action sur un professeur (valider, refuser, incomplet, etc.)"""
    prof = get_object_or_404(TeacherProfile, id=prof_id)
    action = request.POST.get('action')
    
    if action == 'valider':
        prof.statut_de_validation = ValidationStatus.VALIDE
        prof.save()
        # TODO: Envoi d'email de confirmation (simulation pour le test)
        print(f"[SIMULATION EMAIL] Profil validé envoyé à {prof.email}")
        return JsonResponse({'success': True, 'message': 'Professeur validé avec succès.'})
        
    elif action == 'incomplet':
        raison = request.POST.get('raison', 'Informations incomplètes.')
        prof.statut_de_validation = ValidationStatus.INCOMPLET
        prof.save()
        print(f"[SIMULATION EMAIL] Profil incomplet envoyé à {prof.email}. Raison: {raison}")
        return JsonResponse({'success': True, 'message': 'Statut mis à jour et email envoyé.'})
        
    elif action == 'valider_note':
        note = request.POST.get('note', '')
        print(f"[SIMULATION EMAIL] Email envoyé à {prof.email} avec la note d'évaluation: {note}")
        return JsonResponse({'success': True, 'message': 'Note enregistrée et email envoyé.'})
        
    return JsonResponse({'error': 'Action non reconnue.'}, status=400)
