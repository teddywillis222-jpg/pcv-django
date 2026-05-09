from datetime import date

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.conf import settings
from django.db.models import Avg, Count

from django.utils import timezone
from .forms import (
    ApprenantCreateProfileForm,
    EnfantForm,
    FinalisationCompteForm,
    LoginForm,
    ParentForm,
    SignUpForm,
)
from .choices import TypeAbonnement, StatutGeneral, EngagementType, ValidationStatus, Localisation
from .models import Abonnement, Apprenant, Enfant, Parent, Profile, TeacherProfile, Engagement, Message
from django.db.models import Q
from django.template.loader import render_to_string


def annotate_teachers_with_ratings(queryset):
    """
    Annote un queryset de TeacherProfile avec :
    - Les moyennes d'avis réels ou d'équipe (moyenne_avis, nombre_avis, has_real_reviews)
    - Le badge "Suivi Rigoureux" (suivi_rigoureux) selon la règle d'assiduité par récence :
        * Condition 1 (Seuil) : >= 3 bilans de séances enregistrés au total
        * Condition 2 (Récence) : SI engagement actif (FINALISE), le dernier bilan < 14 jours
                                   SI aucun engagement actif, la règle de récence est ignorée
    """
    from django.db.models.functions import Coalesce, Cast, Now
    from django.db.models import (
        F, Case, When, Value, BooleanField, IntegerField,
        Avg, Count, DecimalField, FloatField, Max, Q, ExpressionWrapper, DurationField
    )
    from django.utils import timezone

    # Seuil : nombre total de bilans de séances (Seance) enregistrés par ce prof
    # Un "bilan" = une Seance dont le champ objectifs est non vide
    nb_bilans_total = Count(
        'engagements__seances',
        filter=Q(engagements__seances__objectifs__gt=''),
        distinct=True
    )

    # Date du dernier bilan rempli (tout engagement confondu)
    date_dernier_bilan = Max(
        'engagements__seances__creee_le',
        filter=Q(engagements__seances__objectifs__gt='')
    )

    # Nombre d'engagements actifs (FINALISE)
    nb_engagements_actifs = Count(
        'engagements',
        filter=Q(engagements__statut_general='FINALISE'),
        distinct=True
    )

    # Date limite : il y a N jours (configurable via settings)
    date_limite_rigueur = timezone.now() - timezone.timedelta(days=settings.SUIVI_RIGOUREUX_JOURS_RECENCE)

    return queryset.annotate(
        real_moyenne=Avg('evaluations_recues__note'),
        real_nombre=Count('evaluations_recues', distinct=True),
        _nb_bilans_total=nb_bilans_total,
        _date_dernier_bilan=date_dernier_bilan,
        _nb_engagements_actifs=nb_engagements_actifs,
    ).annotate(
        moyenne_avis=Coalesce(
            Cast(F('real_moyenne'), DecimalField(max_digits=3, decimal_places=1)),
            F('note_initiale_equipe')
        ),
        nombre_avis=Case(
            When(real_nombre=0, then=Value(1)),
            default=F('real_nombre'),
            output_field=IntegerField()
        ),
        has_real_reviews=Case(
            When(real_nombre=0, then=Value(False)),
            default=Value(True),
            output_field=BooleanField()
        ),
        # Badge "Suivi Rigoureux" :
        # True si :
        #   - Seuil atteint : >= SUIVI_RIGOUREUX_SEUIL_BILANS bilans au total
        #   ET
        #   - Soit aucun engagement actif (on ignore la récence)
        #   - Soit le dernier bilan date de moins de SUIVI_RIGOUREUX_JOURS_RECENCE jours
        suivi_rigoureux=Case(
            # Seuil non atteint → False (nouveaux profs ou profs qui n'ont jamais rempli)
            When(_nb_bilans_total__lt=settings.SUIVI_RIGOUREUX_SEUIL_BILANS, then=Value(False)),
            # Seuil atteint + aucun engagement actif → True (bon passif, pas pénalisé)
            When(_nb_engagements_actifs=0, then=Value(True)),
            # Seuil atteint + engagement actif + dernier bilan récent → True
            When(
                _nb_engagements_actifs__gt=0,
                _date_dernier_bilan__gte=date_limite_rigueur,
                then=Value(True)
            ),
            # Seuil atteint + engagement actif + dernier bilan trop ancien → False
            default=Value(False),
            output_field=BooleanField()
        )
    )


def home(request):
    from .choices import ValidationStatus
    
    # On récupère 24 professeurs validés aléatoirement (ou les plus récents)
    top_professeurs = TeacherProfile.objects.filter(
        statut_de_validation=ValidationStatus.VALIDE
    ).order_by('?')[:24]

    top_professeurs = annotate_teachers_with_ratings(top_professeurs)

    return render(request, "core/home.html", {"top_professeurs": top_professeurs})

def faq(request):
    """Page FAQ - Questions fréquentes"""
    return render(request, "core/faq.html")

def support(request):
    """Page Support - Aide et assistance"""
    return render(request, "core/support.html")

def cgu(request):
    """Page des Conditions Générales d'Utilisation"""
    return render(request, "core/cgu.html")

def politique_confidentialite(request):
    """Page de la Politique de Confidentialité"""
    return render(request, "core/politique_confidentialite.html")

@login_required
def messagerie(request):
    """Page Messagerie - Liste des discussions avec filtres et recherche intelligente."""
    from .choices import StatutGeneral
    from .models import Conversation, Profile as Role, Profile
    
    # Sécurité Rôle
    try:
        user_profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect("finalisation_compte")

    # Base Queryset optimisé
    from django.db.models import Q, Count, Max
    
    conversations = Conversation.objects.filter(
        participants=request.user
    ).select_related(
        'professeur__user',
        'parent', 
        'engagement_actif',
        'engagement_actif__professeur',
        'engagement_actif__parent_apprenant',
        'dernier_message_auteur'
    ).prefetch_related(
        'engagement_actif__enfants_concernes',
        'participants'
    ).annotate(
        unread_count=Count(
            'messages', 
            filter=Q(messages__lu=False) & Q(messages__destinataire=request.user)
        )
    ).exclude(masquee_par=request.user)

    # 1. Filtre par onglet (Status)
    tab = request.GET.get('tab', 'toutes')
    
    if tab == 'actives':
        conversations = conversations.filter(engagement_actif__statut_general=StatutGeneral.FINALISE)
    elif tab == 'en_cours':
        conversations = conversations.filter(
            engagement_actif__statut_general__in=[StatutGeneral.EN_ATTENTE, StatutGeneral.CONFIRME, StatutGeneral.EN_COURS]
        )
    elif tab == 'bloquees':
        conversations = conversations.filter(
            engagement_actif__statut_general__in=[StatutGeneral.CONFIRME, StatutGeneral.EN_COURS],
            engagement_actif__paiement_effectue=False
        )
    elif tab == 'terminees':
        conversations = conversations.filter(engagement_actif__statut_general=StatutGeneral.TERMINE)
        
    # Appliquer le filtre d'archivage sur TOUS les onglets sauf "archivees"
    if tab == 'archivees':
        conversations = conversations.filter(archivee_par=request.user)
    else:
        conversations = conversations.exclude(archivee_par=request.user)

    # 2. Recherche intelligente
    search_query = request.GET.get('q', '').strip()
    if search_query:
        conversations = conversations.filter(
            Q(professeur__nom__icontains=search_query) |
            Q(professeur__prenom__icontains=search_query) |
            Q(parent__first_name__icontains=search_query) |
            Q(parent__last_name__icontains=search_query) |
            Q(parent__parent__nom__icontains=search_query) |
            Q(parent__apprenant__nom__icontains=search_query) |
            Q(engagement_actif__enfants_concernes__prenom__icontains=search_query) |
            Q(engagement_actif__matiere__icontains=search_query) |
            Q(engagement_actif__localisation_option__icontains=search_query)
        ).distinct()

    conversations = conversations.order_by('-dernier_message_date', '-date_creation')

    # 3. Traitement des données pour le template (Contextualisation)
    formatted_conversations = []
    for conv in conversations:
        eng = conv.engagement_actif
        # Déterminer le nom, la photo et l'initiale à afficher
        display_initial = "?"
        display_photo = None
        if user_profile.role == Role.ROLE_PARENT or user_profile.role == Role.ROLE_APPRENANT:
            if conv.professeur:
                display_name = f"Prof. {conv.professeur.prenom} {conv.professeur.nom}"
                display_initial = conv.professeur.prenom[0] if conv.professeur.prenom else conv.professeur.nom[0]
            else:
                display_name = "Professeur PCV"
                display_initial = "P"
            if conv.professeur and conv.professeur.photo_de_profil:
                display_photo = conv.professeur.photo_de_profil.url
        else:
            # Pour le prof : Parent de [Enfants] ou Nom Apprenant
            if eng and eng.enfants_concernes.exists():
                enfants_names = ", ".join([e.prenom for e in eng.enfants_concernes.all()])
                display_name = f"Parent de {enfants_names}"
            else:
                if conv.parent and hasattr(conv.parent, 'profile'):
                    if conv.parent.profile.role == Role.ROLE_APPRENANT and hasattr(conv.parent, 'apprenant'):
                        # Le modèle Apprenant n'a pas de prenom, on utilise nom + first_name du User
                        apprenant_nom = conv.parent.apprenant.nom or conv.parent.first_name or conv.parent.username
                        display_name = f"{apprenant_nom}"
                    elif hasattr(conv.parent, 'parent'):
                        display_name = f"Parent {conv.parent.parent.nom}"
                    else:
                        display_name = conv.parent.first_name or "Parent PCV"
                else:
                    display_name = "Utilisateur PCV"
            
            # Initiale basée sur le prénom de l'utilisateur parent
            if conv.parent:
                display_initial = conv.parent.first_name[0] if conv.parent.first_name else conv.parent.username[0]
            
            # Photo du parent ou de l'apprenant
            if conv.parent:
                try:
                    if conv.parent.profile.role == Role.ROLE_PARENT:
                        if hasattr(conv.parent, 'parent') and conv.parent.parent.photo_profil:
                            display_photo = conv.parent.parent.photo_profil.url
                    elif conv.parent.profile.role == Role.ROLE_APPRENANT:
                        if hasattr(conv.parent, 'apprenant') and conv.parent.apprenant.photo_de_profil:
                            display_photo = conv.parent.apprenant.photo_de_profil.url
                except Exception:
                    pass

        # Badge Statut & Couleur
        statut_label = "Discussion"
        statut_class = "statut-default"
        
        if eng:
            if eng.statut_general == StatutGeneral.FINALISE:
                statut_label = "Actif"
                statut_class = "statut-active"
            elif eng.statut_general == StatutGeneral.TERMINE:
                statut_label = "Terminé"
                statut_class = "statut-finished"
            elif eng.statut_general in [StatutGeneral.CONFIRME, StatutGeneral.EN_COURS] and not eng.paiement_effectue:
                statut_label = "Paiement requis"
                statut_class = "statut-blocked"
            elif eng.statut_general in [StatutGeneral.EN_ATTENTE, StatutGeneral.CONFIRME, StatutGeneral.EN_COURS]:
                statut_label = "En cours"
                statut_class = "statut-pending"

        # Blocage Messagerie
        is_blocked = False
        if eng and eng.statut_general in [StatutGeneral.CONFIRME, StatutGeneral.EN_COURS] and not eng.paiement_effectue:
            if user_profile.role in [Role.ROLE_PARENT, Role.ROLE_APPRENANT]:
                from .choices import TypeAbonnement
                is_premium = request.user.abonnements.filter(type_abonnement=TypeAbonnement.ACCESS_PREMIUM).exists()
                if not is_premium:
                    is_blocked = True
            else:
                # Le professeur n'est jamais bloqué
                is_blocked = False

        # Non-lus (utilise le compteur annoté pour performance)
        has_unread = conv.unread_count > 0

        formatted_conversations.append({
            'obj': conv,
            'display_name': display_name,
            'statut_label': statut_label,
            'statut_class': statut_class,
            'is_blocked': is_blocked,
            'has_unread': has_unread,
            'engagement': eng,
            'display_photo': display_photo,
            'display_initial': display_initial,
        })

    context = {
        'conversations': formatted_conversations,
        'current_tab': tab,
        'search_query': search_query,
        'role': user_profile.role,
        'ROLE_PROF': Role.ROLE_PROF,
        'ROLE_PARENT': Role.ROLE_PARENT,
        'ROLE_APPRENANT': Role.ROLE_APPRENANT,
        'today': timezone.now().date(),
        'unread_total': sum(1 for c in formatted_conversations if c['has_unread']),
    }

    return render(request, "core/messagerie.html", context)

def recherche(request):
    """Page de recherche des professeurs avec filtres"""
    from .choices import ValidationStatus, CourseMode, Localisation, ClassLevel, SupportCategory, Matiere
    professeurs = TeacherProfile.objects.filter(
        statut_de_validation=ValidationStatus.VALIDE
    )
    
    # Récupération des paramètres de recherche
    matiere = request.GET.get('matiere', '').strip()
    localisation = request.GET.get('localisation', '').strip()
    classe = request.GET.get('classe', '').strip()
    prix = request.GET.get('prix', '').strip()
    mode = request.GET.get('mode', '').strip()
    soutien = request.GET.get('soutien', '').strip()

    if matiere:
        professeurs = professeurs.filter(matiere_enseignee__icontains=matiere)
    if localisation:
        professeurs = professeurs.filter(ville_quartier=localisation)
    if classe:
        professeurs = professeurs.filter(classes_enseignees__icontains=classe)
    if mode:
        professeurs = professeurs.filter(modes_de_cours__icontains=mode)
    if soutien:
        professeurs = professeurs.filter(categorie_de_soutien=soutien)
        
    if prix:
        thresholds = [int(t) for t in settings.PRICE_THRESHOLDS]
        if prix == f"0-{thresholds[0]}":
            professeurs = professeurs.filter(tarif_horaire__lt=thresholds[0])
        elif prix == f"{thresholds[0]}-{thresholds[1]}":
            professeurs = professeurs.filter(tarif_horaire__gte=thresholds[0], tarif_horaire__lte=thresholds[1])
        elif prix == f"{thresholds[1]}-{thresholds[2]}":
            professeurs = professeurs.filter(tarif_horaire__gte=thresholds[1], tarif_horaire__lte=thresholds[2])
        elif prix == f"{thresholds[2]}+":
            professeurs = professeurs.filter(tarif_horaire__gt=thresholds[2])

    # 3. Annotation des ratings + badge Suivi Rigoureux via le helper centralisé
    # Ordre : 1) Certifiés en premier, 2) Badge suivi rigoureux, 3) Meilleure note, 4) Plus récent
    professeurs = annotate_teachers_with_ratings(professeurs).order_by(
        '-est_certifie',
        '-suivi_rigoureux',
        '-moyenne_avis',
        '-id'
    )

    # Contexte Parent/Enfants
    parent_children = []
    parent_children_json = "[]"
    if request.user.is_authenticated and hasattr(request.user, 'parent'):
        parent_children = list(request.user.parent.enfants.all().values('id', 'prenom'))
        parent_children_json = json.dumps(parent_children)

    # --- SEO Dynamique ---
    seo_title = "Rechercher un professeur particulier au Bénin | ProfChezVous"
    seo_description = "Trouvez le professeur idéal pour vos cours à domicile au Bénin. Sélectionnez votre matière, votre quartier et votre niveau."

    if matiere and localisation:
        seo_title = f"Meilleurs Professeurs de {matiere} à {localisation} | ProfChezVous"
        seo_description = f"Découvrez nos professeurs de {matiere} certifiés disponibles à {localisation}. Soutien scolaire de qualité à domicile."
    elif matiere:
        seo_title = f"Cours particuliers de {matiere} au Bénin | ProfChezVous"
        seo_description = f"Trouvez un professeur de {matiere} compétent pour des cours à domicile partout au Bénin. Tous niveaux."
    elif localisation:
        seo_title = f"Professeurs particuliers à {localisation} | ProfChezVous"
        seo_description = f"Besoin d'un prof à {localisation} ? Découvrez notre sélection d'enseignants vérifiés pour vos enfants."

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
        'seo_title': seo_title,
        'seo_description': seo_description,
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
                prix=f"{settings.DEFAULT_ENGAGEMENT_PRICE}{settings.DEFAULT_CURRENCY} par engagement",
                date_debut=date.today(),
            )
            from django.contrib import messages
            messages.success(request, f"Bienvenue {user.first_name} ! Votre compte a été créé avec succès.")
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
            from django.contrib import messages
            messages.success(request, f"Heureux de vous revoir, {user.first_name} !")
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
                    prix=f"{settings.DEFAULT_ENGAGEMENT_PRICE}{settings.DEFAULT_CURRENCY} par engagement",
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
    """
    Redirection intelligente après connexion ou inscription.
    Vérifie l'existence du profil métier (Prof, Parent, Apprenant) pour orienter l'utilisateur.
    """
    if not request.user.is_authenticated:
        return redirect("home")

    # 1. Staff / Admin
    if request.user.is_staff or request.user.is_superuser:
        return redirect("/admin/")

    # 2. Récupération du profil de base
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # Cas rare si le signal n'a pas fonctionné
        return redirect("home")

    # 3. Logique de redirection directe par rôle
    
    # --- RÔLE : PROFESSEUR ---
    if profile.role == Profile.ROLE_PROF:
        teacher = getattr(request.user, "teacher_profile", None)
        if teacher:
            from .choices import ValidationStatus
            if teacher.statut_de_validation == ValidationStatus.VALIDE:
                return redirect("prof_dashboard")
            return redirect("prof_attente_dashboard")
        return redirect("prof_intro")

    # --- RÔLE : PARENT ---
    elif profile.role == Profile.ROLE_PARENT:
        parent = getattr(request.user, "parent", None)
        # Si le parent existe et a au moins un enfant, dashboard direct
        if parent and parent.enfants.exists():
            return redirect("parent_dashboard")
        # Sinon, création de profil (Parent + Premier enfant)
        return redirect("parent_create_profile")

    # --- RÔLE : APPRENANT (Élève autonome) ---
    elif profile.role == Profile.ROLE_APPRENANT:
        apprenant = getattr(request.user, "apprenant", None)
        # Si le profil métier existe, dashboard direct
        if apprenant:
            return redirect("apprenant_dashboard")
        return redirect("apprenant_create_profile")

    # Par défaut
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
            
            # Gestion intelligente du nom (Allauth split ou Nom complet)
            full_name = request.user.get_full_name() or request.user.first_name or request.user.username
            if " " in full_name and not request.user.last_name:
                teacher.prenom, teacher.nom = full_name.split(" ", 1)
            else:
                teacher.prenom = request.user.first_name
                teacher.nom = request.user.last_name or " "

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

    return render(request, "core/prof_create_profile.html", {
        "form": form,
        "teacher_instance": teacher_instance
    })


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
    
    # On ne redirige plus automatiquement pour permettre d'afficher le message de succès sur cette page
    # if teacher_instance.statut_de_validation == ValidationStatus.VALIDE:
    #     return redirect("prof_dashboard")

    if request.method == "POST":
        teacher_instance.presentation = request.POST.get("presentation", teacher_instance.presentation)
        teacher_instance.methodologie = request.POST.get("methodologie", teacher_instance.methodologie)
        exp = request.POST.get("annees_d_experience")
        if exp: teacher_instance.annees_d_experience = exp
        tarif = request.POST.get("tarif_horaire")
        if tarif: teacher_instance.tarif_horaire = tarif
        
        # Sauvegarde des disponibilités (Grille)
        teacher_instance.grille_disponibilites = request.POST.getlist("disponibilites")
        
        teacher_instance.save()
        return redirect("prof_attente_dashboard")

    # Calcul pourcentage complétion
    completion = teacher_instance.completion_percentage
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    
    return render(request, "core/prof_attente_dashboard.html", {
        "teacher": teacher_instance,
        "completion": completion,
        "jours": jours
    })


@login_required
def prof_edit_profile(request):
    """Page d'édition du profil pour le professeur (Workflow complet)"""
    try:
        profile = request.user.profile
        teacher = request.user.teacher_profile
    except (Profile.DoesNotExist, TeacherProfile.DoesNotExist):
        return redirect("home")

    if profile.role != Profile.ROLE_PROF:
        return redirect("home")

    if request.method == "POST":
        form = TeacherProfileForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            teacher = form.save()
            return redirect("prof_dashboard")
    else:
        form = TeacherProfileForm(instance=teacher)

    return render(request, "core/prof_edit_profile.html", {
        "form": form,
        "teacher": teacher,
        "localisation_choices": Localisation.CHOICES
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
    except TeacherProfile.DoesNotExist:
        return redirect("prof_create_profile")

    # 1. Gestion des Engagements par onglets
    engagements = teacher.engagements.all().order_by("-date_creation")
    
    # "En cours" (Demandes en attente ou confirmées mais pas encore finalisées)
    # On regroupe EN_ATTENTE, CONFIRME (qui est "En cours") et EN_COURS
    engs_en_cours = engagements.filter(
        statut_general__in=[StatutGeneral.EN_ATTENTE, StatutGeneral.CONFIRME, StatutGeneral.EN_COURS]
    )
    
    # "Finalisés/actifs" (Uniquement les engagements ayant le statut FINALISE)
    engs_actifs = engagements.filter(statut_general=StatutGeneral.FINALISE)
    
    # "Essai"
    engs_essais = engagements.filter(type_engagement=EngagementType.ESSAI).exclude(statut_general=StatutGeneral.TERMINE)
    
    # "Terminé"
    engs_termines = engagements.filter(statut_general__in=[StatutGeneral.TERMINE, StatutGeneral.ANNULE, StatutGeneral.REFUSE])

    # 2. Statistiques dynamiques (Plus fiables que les compteurs stockés)
    # Contrats actifs = Uniquement FINALISE
    nb_actifs = engagements.filter(statut_general=StatutGeneral.FINALISE).count()
    # Cours terminés = TERMINE
    nb_termines = engagements.filter(statut_general=StatutGeneral.TERMINE).count()
    
    # 3. Centre de Notifications (Messages non lus)
    unread_messages_count = Message.objects.filter(
        destinataire=request.user,
        lu=False
    ).count()

    # 4. Parents Favoris
    parents_favoris = teacher.parents_favoris.all()

    context = {
        "teacher": teacher,
        "engs_en_cours": engs_en_cours,
        "engs_actifs": engs_actifs,
        "engs_termines": engs_termines,
        "engs_essais": engs_essais,
        "unread_count": unread_messages_count,
        "parents_favoris": parents_favoris,
        "completion": teacher.completion_percentage,
        "nb_actifs": nb_actifs,
        "nb_termines": nb_termines,
    }

    return render(request, "core/prof_dashboard.html", context)


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

    if request.method == "POST":
        enfant_form = EnfantForm(request.POST)
        if enfant_form.is_valid():
            enfant = enfant_form.save(commit=False)
            enfant.parent = parent
            enfant.save()
            # redirection vers le dashboard avec le nouvel enfant sélectionné
            from django.urls import reverse
            return redirect(f"{reverse('parent_dashboard')}?enfant_id={enfant.id}")

    enfants = parent.enfants.all()
    if not enfants.exists():
        return redirect("parent_create_profile")

    # 1. Sélection de l'enfant actif (par URL, sinon le 1er par défaut)
    enfant_id = request.GET.get("enfant_id")
    active_enfant = enfants.filter(id=enfant_id).first() if enfant_id else enfants.first()

    # 2. Recommandations dynamiques basées sur l'enfant actif et le parent
    from django.db.models import Q, Case, When, Value, IntegerField
    recommandations = TeacherProfile.objects.filter(statut_de_validation=ValidationStatus.VALIDE)
    
    score_annotation = Value(0, output_field=IntegerField())
    
    # Critère 1: Matières faibles (3 points)
    if active_enfant and active_enfant.matieres:
        q_matieres = Q()
        for mat in active_enfant.matieres:
            q_matieres |= Q(matiere_enseignee__icontains=mat)
        score_annotation = score_annotation + Case(
            When(q_matieres, then=Value(3)),
            default=Value(0),
            output_field=IntegerField()
        )
        
    # Critère 2: Classe en commun (2 points)
    if active_enfant and active_enfant.classe:
        score_annotation = score_annotation + Case(
            When(classes_enseignees__icontains=active_enfant.classe, then=Value(2)),
            default=Value(0),
            output_field=IntegerField()
        )
        
    # Critère 3: Ville / Quartier du parent (1 point)
    if parent.quartier_ville:
        score_annotation = score_annotation + Case(
            When(ville_quartier=parent.quartier_ville, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )

    # Appliquer l'annotation et trier par score décroissant
    # puis badge suivi rigoureux comme critère secondaire
    recommandations_annotees = recommandations.annotate(
        match_score=score_annotation
    ).filter(match_score__gt=0).order_by("-match_score", "-est_certifie", "?")[:8]
    
    # Appliquer les ratings avant la conversion en liste (car .annotate n'existe que sur QuerySet)
    recommandations_annotees = annotate_teachers_with_ratings(recommandations_annotees)
    recommandations_list = list(recommandations_annotees)
    
    # Compléter avec d'autres profs si insuffisant
    if len(recommandations_list) < 8:
        fallback = recommandations.exclude(id__in=[r.id for r in recommandations_list]).order_by("?")[:8 - len(recommandations_list)]
        # Appliquer les ratings aussi sur le fallback
        fallback = annotate_teachers_with_ratings(fallback)
        recommandations_list.extend(list(fallback))
        
    recommandations = recommandations_list

    # 3. Engagements : On prend TOUS les engagements du parent pour être sûr de ne rien rater
    # (Même si certains n'ont pas été correctement liés à un enfant lors de la création)
    engagements_base = request.user.engagements_client.filter(masque_par_parent=False)
    
    # On filtre ceux de l'enfant actif OU ceux qui n'ont AUCUN enfant lié (orphelins)
    from django.db.models import Q
    engagements = engagements_base.filter(
        Q(enfants_concernes=active_enfant) | Q(enfants_concernes__isnull=True)
    ).distinct().order_by("-date_creation")

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
    
    # Historique complet pour le modal/liste (tous les statuts, mais non masqués)
    engagements_tous = engagements.all()

    # Onglet "Essais"
    engs_essais = engagements.filter(type_engagement=EngagementType.ESSAI)

    # 4. Données additionnelles
    favoris = request.user.professeurs_favoris.all()
    abonnement = getattr(parent, "abonnement", None)
    enfant_form = EnfantForm()

    # Annotation des ratings + badge Suivi Rigoureux, puis tri : certifiés, badge, note
    favoris = annotate_teachers_with_ratings(favoris).order_by(
        '-est_certifie', '-suivi_rigoureux', '-moyenne_avis'
    )

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
            "enfant_form": enfant_form,
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
            form.save_m2m()
            
            from django.urls import reverse
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
                return JsonResponse({"success": True, "redirect_url": reverse("apprenant_dashboard")})
            
            return redirect("apprenant_dashboard")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
                return JsonResponse({"success": False, "errors": form.errors}, status=400)
    else:
        initial = {"nom": request.user.first_name}
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

    from .choices import ValidationStatus, StatutGeneral, EngagementType, ObjectifMotivation, CreneauDisponibilite

    # 1. Recommandations dynamiques basées sur la classe, matières et localisation de l'apprenant
    from django.db.models import Q, Case, When, Value, IntegerField
    recommandations = TeacherProfile.objects.filter(statut_de_validation=ValidationStatus.VALIDE)
    
    score_annotation = Value(0, output_field=IntegerField())
    
    # Critère 1: Matières recherchées (3 points)
    if apprenant.matieres_recherchees:
        q_matieres = Q()
        for mat in apprenant.matieres_recherchees:
            q_matieres |= Q(matiere_enseignee__icontains=mat)
        score_annotation = score_annotation + Case(
            When(q_matieres, then=Value(3)),
            default=Value(0),
            output_field=IntegerField()
        )
        
    # Critère 2: Classe en commun (2 points)
    if apprenant.classe:
        score_annotation = score_annotation + Case(
            When(classes_enseignees__icontains=apprenant.classe, then=Value(2)),
            default=Value(0),
            output_field=IntegerField()
        )
        
    # Critère 3: Ville / Quartier (1 point)
    if apprenant.quartier_ville:
        score_annotation = score_annotation + Case(
            When(ville_quartier=apprenant.quartier_ville, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    
    # Appliquer les ratings avant la conversion en liste (car .annotate n'existe que sur QuerySet)
    recommandations_annotees = annotate_teachers_with_ratings(recommandations_annotees)
    recommandations_list = list(recommandations_annotees)
    
    # Compléter avec d'autres profs si insuffisant
    if len(recommandations_list) < 8:
        fallback = recommandations.exclude(id__in=[r.id for r in recommandations_list]).order_by("?")[:8 - len(recommandations_list)]
        # Appliquer les ratings aussi sur le fallback
        fallback = annotate_teachers_with_ratings(fallback)
        recommandations_list.extend(list(fallback))
        
    recommandations = recommandations_list

    # 2. Engagements filtrés pour l'apprenant (parent_apprenant=request.user)
    engagements = request.user.engagements_client.all().order_by("-date_creation")

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

    # 3. Abonnement & Favoris
    abonnement = request.user.abonnements.first()
    favoris = TeacherProfile.objects.filter(parents_favoris=request.user)

    # Annotation des ratings + badge Suivi Rigoureux, puis tri : certifiés, badge, note
    favoris = annotate_teachers_with_ratings(favoris).order_by(
        '-est_certifie', '-suivi_rigoureux', '-moyenne_avis'
    )

    context = {
        "apprenant": apprenant,
        "recommandations": recommandations,
        "engagements_en_cours": engs_en_cours,
        "engagements_actifs": engs_actifs,
        "engagements_termines": engs_termines,
        "engagements_essais": engs_essais,
        "engagements_tous": engagements_tous,
        "abonnement": abonnement,
        "favoris": favoris,
    }

    return render(request, "core/apprenant_dashboard.html", context)


@login_required
def gestion_plan(request):
    from django.utils import timezone
    from datetime import datetime
    from .models import Profile
    
    # Sécurité Rôle
    try:
        user_profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect("finalisation_compte")
    
    # Plan actuel
    abonnement = request.user.abonnements.order_by('-date_debut').first()
    if not abonnement:
        # Créer un abonnement standard par défaut
        abonnement = Abonnement.objects.create(
            user=request.user,
            type_abonnement=TypeAbonnement.STANDARD,
            prix=f"{settings.DEFAULT_ENGAGEMENT_PRICE}{settings.DEFAULT_CURRENCY} par engagement"
        )

    # Consommation mensuelle (confirmations ce mois-ci)
    now = timezone.now()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    confirmations_ce_mois = Engagement.objects.filter(
        parent_apprenant=request.user,
        date_confirmation__gte=first_day_of_month
    ).count()
    
    # Historique de paiements (synthétique)
    history = []
    
    # 1. Engagements payés
    engagements_payes = Engagement.objects.filter(
        parent_apprenant=request.user,
        paiement_effectue=True
    ).order_by('-date_confirmation')[:10]
    
    for eng in engagements_payes:
        history.append({
            'type': 'Déblocage conversation',
            'libelle': f"Prof. {eng.professeur.nom}" if eng.professeur else "Professeur PCV",
            'montant': f"{settings.DEFAULT_ENGAGEMENT_PRICE} {settings.DEFAULT_CURRENCY}",
            'date': eng.date_confirmation
        })
    
    # 2. Abonnements Premium (si existants)
    abonnements_premium = request.user.abonnements.filter(
        type_abonnement=TypeAbonnement.ACCESS_PREMIUM
    ).order_by('-date_debut')[:5]
    
    for ab in abonnements_premium:
        history.append({
            'type': 'Abonnement Premium',
            'libelle': 'Plan Access+ Premium',
            'montant': f"{settings.PREMIUM_MONTHLY_PRICE} {settings.DEFAULT_CURRENCY}",
            'date': ab.date_debut
        })
    
    # Trier l'historique par date
    history.sort(key=lambda x: x['date'] if x['date'] else datetime.min.replace(tzinfo=timezone.utc), reverse=True)

    context = {
        'abonnement': abonnement,
        'confirmations_ce_mois': confirmations_ce_mois,
        'history': history,
        'TypeAbonnement': TypeAbonnement,
        'DEFAULT_ENGAGEMENT_PRICE': settings.DEFAULT_ENGAGEMENT_PRICE,
        'PREMIUM_MONTHLY_PRICE': settings.PREMIUM_MONTHLY_PRICE,
        'PREMIUM_ENGAGEMENT_QUOTA': settings.PREMIUM_ENGAGEMENT_QUOTA,
        'DEFAULT_CURRENCY': settings.DEFAULT_CURRENCY,
    }
    return render(request, "core/gestion_plan.html", context)



# Vues pour le système de recherche et profils hybride
def track_teacher_view(request, teacher_profile):
    from django.utils import timezone
    from datetime import timedelta
    from .models import VueProfil, Profile
    
    # Nettoyage paresseux des anciennes vues (vieux de plus de 60 jours)
    limit_date = timezone.now() - timedelta(days=60)
    VueProfil.objects.filter(professeur_vise=teacher_profile, date_consultation__lt=limit_date).delete()

    if not request.user.is_authenticated:
        return
        
    try:
        # Ne pas compter si le visiteur est un prof
        if request.user.profile.role == Profile.ROLE_PROF:
            return
    except Profile.DoesNotExist:
        pass
        
    # Ne pas compter si c'est le professeur lui-même
    if request.user.id == teacher_profile.user.id:
        return
        
    start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    vue_exists = VueProfil.objects.filter(
        professeur_vise=teacher_profile,
        visiteur_utilisateur=request.user,
        date_consultation__gte=start_of_day
    ).exists()
    
    if not vue_exists:
        VueProfil.objects.create(
            professeur_vise=teacher_profile,
            visiteur_utilisateur=request.user
        )
        # Recalcul de nb_vues_total basé sur les vues conservées (max 60 jours)
        teacher_profile.nb_vues_total = VueProfil.objects.filter(professeur_vise=teacher_profile).count()
        
        # Calcul des vues du mois (pour info, depuis le début du mois)
        first_day_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        teacher_profile.nb_vues_mois = VueProfil.objects.filter(
            professeur_vise=teacher_profile, 
            date_consultation__gte=first_day_of_month
        ).count()
        
        teacher_profile.save(update_fields=['nb_vues_total', 'nb_vues_mois'])

def professeur_detail(request, teacher_slug):
    """Page profil professeur dynamique pour SEO avec robustesse accrue"""
    teacher = get_object_or_404(TeacherProfile, slug=teacher_slug)
    
    track_teacher_view(request, teacher)
    
    # Calcul des stats sécurisé
    from django.db.models import Avg, Count
    engs_stats = teacher.engagements.exclude(temps_reponse_prof__isnull=True)
    temps_moyen_reponse = engs_stats.aggregate(avg=Avg('temps_reponse_prof'))['avg'] if engs_stats.exists() else None
    
    engagements_actifs = teacher.engagements.filter(
        statut_general__in=[StatutGeneral.EN_COURS, StatutGeneral.CONFIRME, StatutGeneral.FINALISE]
    ).count()

    # Moyenne avis dynamique
    evals_stats = teacher.evaluations_recues.aggregate(
        real_note=Avg('note'),
        real_count=Count('id')
    )
    if evals_stats['real_count'] > 0:
        teacher.moyenne_avis = round(evals_stats['real_note'], 1)
        teacher.nombre_avis = evals_stats['real_count']
    else:
        teacher.moyenne_avis = teacher.note_initiale_equipe
        teacher.nombre_avis = 1

    # Badge "Suivi Rigoureux" — calculé sur l'instance unique (même règle que l'annotation SQL)
    from django.utils import timezone as tz
    _date_limite = tz.now() - tz.timedelta(days=settings.SUIVI_RIGOUREUX_JOURS_RECENCE)
    _nb_bilans = teacher.engagements.filter(
        seances__objectifs__gt=''
    ).aggregate(total=Count('seances', distinct=True))['total'] or 0
    _nb_actifs = teacher.engagements.filter(statut_general=StatutGeneral.FINALISE).count()

    if _nb_bilans < settings.SUIVI_RIGOUREUX_SEUIL_BILANS:
        # Seuil non atteint → pas de badge
        teacher.suivi_rigoureux = False
    elif _nb_actifs == 0:
        # Bon passif, pas d'engagement actif → badge conservé
        teacher.suivi_rigoureux = True
    else:
        # Engagement actif : vérifier la récence du dernier bilan
        from django.db.models import Max as _Max
        _last_bilan = teacher.engagements.filter(
            seances__objectifs__gt=''
        ).aggregate(last=_Max('seances__creee_le'))['last']
        teacher.suivi_rigoureux = (_last_bilan is not None and _last_bilan >= _date_limite)
    
    # Auth context
    is_parent = False
    is_premium = False
    parent_children = []
    parent_children_json = "[]"
    existing_engagement = None
    existing_engagement_json = "null"
    existing_conversation_id = None
    
    if request.user.is_authenticated:
        # is_premium est vrai si l'utilisateur a un abonnement actif ACCESS_PREMIUM
        if request.user.abonnements.filter(type_abonnement=TypeAbonnement.ACCESS_PREMIUM).exists():
            is_premium = True

        # Vérifier conversation existante
        from .models import Conversation
        conv = Conversation.objects.filter(participants=request.user).filter(participants=teacher.user).first()
        if conv:
            existing_conversation_id = conv.id

        if hasattr(request.user, 'profile') and request.user.profile.role == Profile.ROLE_PARENT:
            is_parent = True
            if hasattr(request.user, 'parent'):
                parent_children = list(request.user.parent.enfants.all().values('id', 'prenom'))
                parent_children_json = json.dumps(parent_children)
                
        # Vérifier engagement existant (priorité à l'attente pour modification)
        existing_engagement_obj = teacher.engagements.filter(
            parent_apprenant=request.user,
            statut_general=StatutGeneral.EN_ATTENTE
        ).first()
        
        if not existing_engagement_obj:
            # Sinon vérifier s'il y a un engagement actif
            existing_engagement_obj = teacher.engagements.filter(
                parent_apprenant=request.user,
                statut_general__in=[StatutGeneral.CONFIRME, StatutGeneral.EN_COURS]
            ).first()

        if existing_engagement_obj:
            existing_engagement = existing_engagement_obj
            existing_engagement_json = json.dumps({
                'id': existing_engagement_obj.id,
                'matiere': existing_engagement_obj.matiere,
                'mode_de_cours': existing_engagement_obj.mode_de_cours,
                'frequence': existing_engagement_obj.frequence_hebdomadaire,
                'duree': existing_engagement_obj.duree_seance,
                'status': existing_engagement_obj.statut_general,
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
        'existing_engagement_json': existing_engagement_json,
        'existing_conversation_id': existing_conversation_id,
        'days_list': ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    }

    # --- SEO: Professeurs Similaires ---
    related_teachers = TeacherProfile.objects.filter(
        statut_de_validation=ValidationStatus.VALIDE
    ).exclude(id=teacher.id)

    # Priorité 1: Même matière (plus flexible avec icontains)
    same_matiere = related_teachers.filter(matiere_enseignee__icontains=teacher.matiere_enseignee)
    if same_matiere.count() >= 4:
        related_teachers = same_matiere.order_by('?')[:4]
    else:
        # Priorité 2: Même ville/quartier
        same_loc = related_teachers.filter(ville_quartier=teacher.ville_quartier)
        related_teachers = (same_matiere | same_loc).distinct().order_by('?')[:4]

    context['related_teachers'] = annotate_teachers_with_ratings(related_teachers)
    
    return render(request, "core/professeur_detail.html", context)


@require_http_methods(["GET"])
def api_teacher_profile(request, teacher_slug):
    """API pour récupérer les données du professeur (pour le side panel) avec gestion d'erreur robuste"""
    try:
        teacher = TeacherProfile.objects.get(slug=teacher_slug)
        
        track_teacher_view(request, teacher)
        
        # Calcul des stats sécurisé
        from django.db.models import Avg, Count
        
        engs_stats = teacher.engagements.exclude(temps_reponse_prof__isnull=True)
        temps_moyen_reponse = engs_stats.aggregate(avg=Avg('temps_reponse_prof'))['avg'] if engs_stats.exists() else None
            
        engagements_actifs = teacher.engagements.filter(
            statut_general__in=[StatutGeneral.EN_COURS, StatutGeneral.CONFIRME, StatutGeneral.FINALISE]
        ).count()

        # Professeurs similaires pour le Side Panel
        related_teachers = TeacherProfile.objects.filter(
            statut_de_validation=ValidationStatus.VALIDE
        ).exclude(id=teacher.id)
        
        same_matiere = related_teachers.filter(matiere_enseignee__icontains=teacher.matiere_enseignee)
        if same_matiere.count() >= 4:
            related_teachers = same_matiere.order_by('?')[:4]
        else:
            same_loc = related_teachers.filter(ville_quartier=teacher.ville_quartier)
            related_teachers = (same_matiere | same_loc).distinct().order_by('?')[:4]
        
        related_teachers = annotate_teachers_with_ratings(related_teachers)
        
        # Moyenne avis dynamique
        evals_stats = teacher.evaluations_recues.aggregate(
            real_note=Avg('note'),
            real_count=Count('id')
        )
        if evals_stats['real_count'] > 0:
            teacher.moyenne_avis = round(evals_stats['real_note'], 1)
            teacher.nombre_avis = evals_stats['real_count']
        else:
            teacher.moyenne_avis = teacher.note_initiale_equipe
            teacher.nombre_avis = 1
        
        # Contexte d'authentification sécurisé
        is_parent = False
        is_premium = False
        parent_children = []
        existing_engagement = None
        existing_conversation_id = None
        
        if request.user.is_authenticated:
            # Vérifier conversation existante
            from .models import Conversation
            conv = Conversation.objects.filter(participants=request.user).filter(participants=teacher.user).first()
            if conv:
                existing_conversation_id = conv.id
                
            try:
                # is_premium est vrai si l'utilisateur a un abonnement actif ACCESS_PREMIUM
                if request.user.abonnements.filter(type_abonnement=TypeAbonnement.ACCESS_PREMIUM).exists():
                    is_premium = True

                if hasattr(request.user, 'profile') and request.user.profile.role == Profile.ROLE_PARENT:
                    is_parent = True
                    if hasattr(request.user, 'parent'):
                        parent_children = list(request.user.parent.enfants.all().values('id', 'prenom'))
                
                # Vérifier engagement existant (priorité à l'attente pour modification)
                existing_engagement_obj = teacher.engagements.filter(
                    parent_apprenant=request.user,
                    statut_general=StatutGeneral.EN_ATTENTE
                ).first()
                
                if not existing_engagement_obj:
                    # Sinon vérifier s'il y a un engagement actif
                    existing_engagement_obj = teacher.engagements.filter(
                        parent_apprenant=request.user,
                        statut_general__in=[StatutGeneral.CONFIRME, StatutGeneral.EN_COURS]
                    ).first()

                if existing_engagement_obj:
                    existing_engagement = {
                        'id': existing_engagement_obj.id,
                        'matiere': existing_engagement_obj.matiere,
                        'mode_de_cours': existing_engagement_obj.mode_de_cours,
                        'frequence': existing_engagement_obj.frequence_hebdomadaire,
                        'duree': existing_engagement_obj.duree_seance,
                        'status': existing_engagement_obj.statut_general,
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
            'existing_conversation_id': existing_conversation_id,
            'readable_modes': readable_modes,
            'readable_classes': readable_classes,
            'related_teachers': related_teachers,
            'days_list': ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],
            'parent_children': parent_children,
            'existing_engagement': existing_engagement
        }, request=request)
        
        return JsonResponse({
            'html': html,
            'parent_children': parent_children,
            'existing_engagement': existing_engagement,
            'existing_conversation_id': existing_conversation_id,
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
        
        # Recherche d'un engagement existant non terminé
        existing = Engagement.objects.filter(
            professeur=teacher,
            parent_apprenant=request.user
        ).exclude(statut_general__in=[StatutGeneral.TERMINE, StatutGeneral.ANNULE, StatutGeneral.REFUSE, StatutGeneral.FINALISE]).first()

        engagement = None
        if existing:
            if existing.statut_general == StatutGeneral.EN_ATTENTE:
                engagement = existing
            else:
                return JsonResponse({'error': 'Vous avez déjà un engagement actif ou confirmé avec ce professeur.'}, status=400)

        if not engagement:
            engagement = Engagement(
                professeur=teacher,
                parent_apprenant=request.user,
                statut_general=StatutGeneral.EN_ATTENTE
            )
            
        engagement.type_engagement = type_eng
        engagement.matiere = data.get('matiere', '')
        engagement.classe = data.get('classe', '')
        engagement.mode_de_cours = data.get('course_mode', '')
        engagement.localisation_option = data.get('localisation', '')
        engagement.plateforme_visio_preferee = data.get('plateforme_visio', '')
        
        if type_eng == EngagementType.ESSAI:
            date_essai_str = data.get('date_essai')
            if date_essai_str:
                from django.utils.dateparse import parse_datetime
                engagement.date_heure_essai = parse_datetime(date_essai_str)
            
            date_fin_essai_str = data.get('date_fin_essai')
            if date_fin_essai_str:
                engagement.date_heure_fin_essai = parse_datetime(date_fin_essai_str)
            engagement.description_essai = data.get('description_essai', '')
        else:
            budget = data.get('budget')
            if budget: engagement.budget_convenu = budget
            engagement.frequence_hebdomadaire = data.get('frequence', '')
            engagement.duree_seance = data.get('duree_seance', '')
            engagement.duree_mois = data.get('duree_mois')
            date_debut_str = data.get('date_debut')
            if date_debut_str:
                from django.utils.dateparse import parse_date
                engagement.date_debut = parse_date(date_debut_str)
                
        engagement.save()
        
        # Lier les enfants (ManyToManyField)
        enfant_id = data.get('enfant_id')
        if enfant_id and str(enfant_id).isdigit():
            from .models import Enfant
            try:
                enfant = Enfant.objects.get(id=int(enfant_id))
                # Vérifier que l'enfant appartient bien au parent (sécurité)
                if hasattr(request.user, 'parent') and enfant.parent == request.user.parent:
                    engagement.enfants_concernes.clear()
                    engagement.enfants_concernes.add(enfant)
            except (Enfant.DoesNotExist, ValueError):
                pass
        
        # Fallback : si aucun enfant n'est lié et que le parent n'en a qu'un seul
        if not engagement.enfants_concernes.exists() and hasattr(request.user, 'parent'):
            enfants = request.user.parent.enfants.all()
            if enfants.count() == 1:
                engagement.enfants_concernes.add(enfants.first())

        engagement.save()
        return JsonResponse({
            'success': True,
            'message': 'Votre proposition d\'engagement a été enregistrée avec succès.',
            'engagement_id': engagement.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_engagement_action(request, engagement_id):
    """API pour qu'un professeur accepte ou refuse un engagement."""
    from .choices import StatutGeneral, ConversationStatus
    from .models import Engagement, Conversation
    
    engagement = get_object_or_404(Engagement, id=engagement_id)
    
    # Sécurité: Seul le professeur concerné peut agir
    if not hasattr(request.user, 'teacher_profile') or engagement.professeur != request.user.teacher_profile:
        return JsonResponse({'error': 'Action non autorisée'}, status=403)
        
    try:
        data = json.loads(request.body)
        action = data.get('action') # 'accepter' ou 'refuser'
        
        # Sécurité: Ne pas agir sur un engagement déjà traité
        if engagement.statut_general != StatutGeneral.EN_ATTENTE:
            return JsonResponse({'error': 'Cet engagement a déjà été traité.'}, status=400)

        if action == 'accepter':
            engagement.statut_general = StatutGeneral.CONFIRME # Sera "En cours" via les labels
            engagement.date_confirmation = timezone.now()
            
            # Calcul du temps de réponse (en minutes)
            diff = engagement.date_confirmation - engagement.date_creation
            engagement.temps_reponse_prof = diff.total_seconds() / 60
            
            # 1. Trouver ou Créer la conversation (plus robuste que get_or_create)
            conversation = Conversation.objects.filter(
                professeur=engagement.professeur,
                parent=engagement.parent_apprenant
            ).first()
            
            if not conversation:
                conversation = Conversation.objects.create(
                    professeur=engagement.professeur,
                    parent=engagement.parent_apprenant,
                    statut_conversation=ConversationStatus.ENGAGEMENT_EN_COURS
                )
                # Ajouter les participants au ManyToMany
                conversation.participants.add(engagement.professeur.user, engagement.parent_apprenant)
            
            # 2. Lier l'engagement à la conversation
            engagement.conversation = conversation
            
            # 3. Mettre à jour l'engagement actif de la conversation
            conversation.engagement_actif = engagement
            conversation.save()
            
            # 4. Mettre à jour les stats du professeur
            teacher = engagement.professeur
            teacher.nb_engagements_confirmes = Engagement.objects.filter(professeur=teacher, statut_general=StatutGeneral.CONFIRME).count()
            
            # Mise à jour du temps de réponse moyen
            responses = Engagement.objects.filter(professeur=teacher, temps_reponse_prof__isnull=False).values_list('temps_reponse_prof', flat=True)
            total_time = sum(responses) + engagement.temps_reponse_prof
            teacher.temps_moyen_reponse = total_time / (len(responses) + 1)
            
            teacher.save()
            engagement.save()
            return JsonResponse({'success': True, 'message': 'Engagement accepté', 'conversation_id': conversation.id})
            
        elif action == 'refuser':
            engagement.statut_general = StatutGeneral.REFUSE
            engagement.save()
            return JsonResponse({'success': True, 'message': 'Engagement refusé'})
            
        else:
            return JsonResponse({'error': 'Action inconnue'}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def conversation_detail(request, conversation_id):
    """Page de discussion privée entre deux participants."""
    from .choices import StatutGeneral, TypeAbonnement
    from .models import Conversation, Message, Profile as Role
    from django.contrib import messages as django_messages
    
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Sécurité stricte: Vérification que l'utilisateur est bien participant
    if request.user not in conversation.participants.all():
        django_messages.error(request, "Accès non autorisé à cette conversation.")
        return redirect("messagerie")
    
    # Vérification que l'utilisateur a un profil valide
    try:
        user_profile = request.user.profile
    except Role.DoesNotExist:
        django_messages.error(request, "Profil utilisateur incomplet. Veuillez finaliser votre compte.")
        return redirect("finalisation_compte")
        
    # Charger les messages avec marquage de changement de date
    raw_messages = conversation.messages.all().order_by("date_envoi")
    chat_messages = []
    last_date = None
    for msg in raw_messages:
        msg_date = msg.date_envoi.date()
        msg.changed_date = (msg_date != last_date)
        chat_messages.append(msg)
        last_date = msg_date
    
    # Marquer la conversation comme lue selon le rôle
    if user_profile.role in [Role.ROLE_PARENT, Role.ROLE_APPRENANT]:
        conversation.conversation_lue_par_parent = True
    elif user_profile.role == Role.ROLE_PROF:
        conversation.conversation_lue_par_prof = True
    conversation.save()
    
    # Marquer les messages reçus comme lus (messages où l'utilisateur est destinataire)
    conversation.messages.filter(destinataire=request.user, lu=False).update(
        lu=True, date_lecture=timezone.now()
    )
    
    # Engagements liés
    linked_engagements = conversation.engagements.all().order_by("-date_creation")
    
    # Déterminer le rôle
    user_role = request.user.profile.role if hasattr(request.user, 'profile') else None
    is_user_prof = (user_role == Role.ROLE_PROF) or (conversation.professeur and request.user == conversation.professeur.user)
    
    # Logique de blocage (cohérente avec api_send_message)
    is_blocked = False
    hide_input = False
    blocking_message = ""
    eng = conversation.engagement_actif
    
    # Vérifier l'abonnement
    from .choices import TypeAbonnement, Localisation
    is_premium = request.user.abonnements.filter(type_abonnement=TypeAbonnement.ACCESS_PREMIUM).exists()

    if eng and user_role in ['PARENT', 'APPRENANT']:
        # 1. Bloqué si en attente ou refusé
        if eng.statut_general in ['EN_ATTENTE', 'REFUSE']:
            is_blocked = True
            hide_input = True
            blocking_message = "En attente de la confirmation du professeur." if eng.statut_general == 'EN_ATTENTE' else "Cet engagement a été refusé."
        # 2. Bloqué si confirmé/en cours mais non payé (sauf Access+ Premium)
        elif eng.statut_general in ['CONFIRME', 'EN_COURS'] and not eng.paiement_effectue:
            if not is_premium:
                is_blocked = True
                hide_input = True
                blocking_message = "Paiement requis pour continuer les échanges."
                
    is_eligible_to_finalize = True  # On autorise par défaut

    # Autres infos pour le header
    if request.user == conversation.parent:
        other_user = conversation.professeur.user if conversation.professeur else None
    else:
        other_user = conversation.parent
    
    other_profile_obj = None
    if other_user:
        if hasattr(other_user, 'teacher_profile'):
            other_profile_obj = other_user.teacher_profile
        elif hasattr(other_user, 'parent'):
            other_profile_obj = other_user.parent
        elif hasattr(other_user, 'apprenant'):
            other_profile_obj = other_user.apprenant
    
    # Enfants du parent pour le filtre (si parent)
    parent_children = []
    if user_role == Role.ROLE_PARENT and hasattr(request.user, 'parent'):
        parent_children = request.user.parent.enfants.all()
        
    # Nom à afficher (comme dans la messagerie)
    eng = conversation.engagement_actif
    if user_role in [Role.ROLE_PARENT, Role.ROLE_APPRENANT]:
        display_name = f"Prof. {conversation.professeur.prenom} {conversation.professeur.nom}" if conversation.professeur else "Professeur PCV"
    else:
        if eng and eng.enfants_concernes.exists():
            enfants_names = ", ".join([e.prenom for e in eng.enfants_concernes.all()])
            display_name = f"Parent de {enfants_names}"
        else:
            display_name = conversation.parent.first_name if conversation.parent else "Parent/Apprenant PCV"

    from .choices import ClassLevel, CourseMode, DureeSeance, FrequenceHebdomadaire, PeriodeEngagement

    return render(request, "core/conversation_detail.html", {
        "conversation": conversation,
        "messages": chat_messages,
        "engagements": linked_engagements,
        "is_blocked": is_blocked,
        "hide_input": hide_input,
        "is_eligible_to_finalize": is_eligible_to_finalize,
        "blocking_message": blocking_message,
        "other_participant": other_user,
        "other_profile": other_profile_obj,
        "display_name": display_name,
        "parent_children": parent_children,
        "role": user_role,
        "is_user_prof": is_user_prof,
        "is_premium": is_premium,
        "ROLE_PROF": Role.ROLE_PROF,
        "ROLE_PARENT": Role.ROLE_PARENT,
        "ROLE_APPRENANT": Role.ROLE_APPRENANT,
        "CHOICES_CLASSE": ClassLevel.CHOICES,
        "CHOICES_MODE": CourseMode.CHOICES,
        "CHOICES_DUREE": DureeSeance.CHOICES,
        "CHOICES_FREQ": FrequenceHebdomadaire.CHOICES,
        "CHOICES_PERIODE": PeriodeEngagement.CHOICES,
        "CHOICES_LOCALISATION": Localisation.CHOICES,
    })


@login_required
@require_http_methods(["POST"])
def api_send_message(request, conversation_id):
    """API pour envoyer un message dans une conversation."""
    from .models import Conversation, Message
    from django.utils import timezone
    from datetime import timedelta
    
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Sécurité stricte
    if request.user not in conversation.participants.all():
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    # Validation anti-spam (max 5 messages par minute)
    recent_messages = Message.objects.filter(
        auteur=request.user,
        date_envoi__gte=timezone.now() - timedelta(minutes=1)
    ).count()
    
    if recent_messages >= 5:
        return JsonResponse({'error': 'Trop de messages envoyés. Veuillez patienter.'}, status=429)
        
    # Vérifier le blocage (même logique que conversation_detail)
    from .choices import TypeAbonnement
    user_role = None
    try:
        user_role = request.user.profile.role
    except Exception:
        pass

    if user_role in ['PARENT', 'APPRENANT']:
        active_eng = conversation.engagement_actif
        if active_eng:
            if active_eng.statut_general in ['EN_ATTENTE', 'REFUSE']:
                return JsonResponse({'error': 'En attente de la confirmation du professeur.' if active_eng.statut_general == 'EN_ATTENTE' else 'Cet engagement a été refusé.'}, status=403)
                
            is_premium = request.user.abonnements.filter(type_abonnement=TypeAbonnement.ACCESS_PREMIUM).exists()
            if active_eng.statut_general in ['CONFIRME', 'EN_COURS'] and not active_eng.paiement_effectue and not is_premium:
                return JsonResponse({'error': 'Paiement requis pour continuer les échanges'}, status=402)

    try:
        texte = request.POST.get('texte', '').strip()
        fichier = request.FILES.get('fichier')
        
        # Validation renforcée du contenu
        if not texte and not fichier:
            return JsonResponse({'error': 'Un message ou un fichier est requis'}, status=400)
        
        if texte and len(texte) > 2000:
            return JsonResponse({'error': 'Le message ne peut pas dépasser 2000 caractères'}, status=400)
            
        if request.user == conversation.parent:
            destinataire = conversation.professeur.user if conversation.professeur else None
        else:
            destinataire = conversation.parent
            
        if not destinataire:
            return JsonResponse({'error': 'Destinataire introuvable (profil incomplet ou supprimé).'}, status=400)
        
        message = Message.objects.create(
            conversation=conversation,
            auteur=request.user,
            destinataire=destinataire,
            contenu_texte=texte,
            contenu_media=fichier
        )
        
        # Mettre à jour la conversation
        if fichier:
            is_image = fichier.content_type.startswith('image/')
            prefix = "📷 Photo" if is_image else "📄 Fichier"
            conversation.dernier_message_texte = f"{prefix} {texte}" if texte else prefix
        else:
            conversation.dernier_message_texte = texte
        conversation.dernier_message_date = message.date_envoi
        conversation.dernier_message_auteur = request.user
        
        if request.user == conversation.parent:
            conversation.conversation_lue_par_prof = False
        else:
            conversation.conversation_lue_par_parent = False
            
        conversation.save()
        
        return JsonResponse({
            'success': True,
            'message_id': message.id,
            'date': message.date_envoi.strftime("%H:%M")
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def api_fetch_new_messages(request, conversation_id):
    """API pour récupérer les nouveaux messages (Polling AJAX)."""
    from .models import Conversation
    from django.utils import timezone
    
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.user not in conversation.participants.all():
        return JsonResponse({'error': 'Non autorisé'}, status=403)
        
    last_msg_id = request.GET.get('last_msg_id', 0)
    try:
        last_msg_id = int(last_msg_id)
    except ValueError:
        last_msg_id = 0
        
    new_messages = conversation.messages.filter(id__gt=last_msg_id).order_by('date_envoi')
    
    # Marquer les messages reçus comme lus
    if new_messages.exists():
        unread_received = new_messages.filter(destinataire=request.user, lu=False)
        if unread_received.exists():
            unread_received.update(lu=True, date_lecture=timezone.now())
            
        try:
            user_profile = request.user.profile
            if user_profile.role in ['PARENT', 'APPRENANT']:
                conversation.conversation_lue_par_parent = True
            elif user_profile.role == 'PROF':
                conversation.conversation_lue_par_prof = True
            conversation.save(update_fields=['conversation_lue_par_parent', 'conversation_lue_par_prof'])
        except Exception:
            pass

    # Gérer newly_read: les messages de l'utilisateur qui étaient non lus et qui sont passés à lu
    unread_ids_str = request.GET.get('unread_ids', '')
    newly_read = []
    if unread_ids_str:
        unread_ids = [int(x) for x in unread_ids_str.split(',') if x.strip().isdigit()]
        if unread_ids:
            newly_read = list(conversation.messages.filter(id__in=unread_ids, lu=True).values_list('id', flat=True))

    messages_data = []
    for msg in new_messages:
        file_url = msg.contenu_media.url if msg.contenu_media else None
        file_name = msg.contenu_media.name.split('/')[-1] if msg.contenu_media else None
        
        messages_data.append({
            'id': msg.id,
            'texte': msg.contenu_texte,
            'fichier_url': file_url,
            'fichier_nom': file_name,
            'date': msg.date_envoi.strftime("%H:%M"),
            'is_mine': msg.auteur == request.user,
            'lu': msg.lu
        })
        
    return JsonResponse({
        'messages': messages_data, 
        'newly_read': newly_read,
        'is_blocked': False,
        'blocking_message': ""
    })


@login_required
@require_http_methods(["POST"])
def api_update_engagement(request, engagement_id):
    """API pour modifier les termes d'un engagement (Parent)"""
    from .models import Engagement, Enfant
    engagement = get_object_or_404(Engagement, id=engagement_id)
    
    if engagement.parent_apprenant != request.user:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
        
    try:
        data = json.loads(request.body)
        engagement.matiere = data.get('matiere', engagement.matiere)
        engagement.budget_convenu = data.get('budget', engagement.budget_convenu)
        engagement.frequence_hebdomadaire = data.get('frequence', engagement.frequence_hebdomadaire)
        engagement.duree_seance = data.get('duree_seance', engagement.duree_seance)
        engagement.classe = data.get('classe', engagement.classe)
        engagement.mode_de_cours = data.get('mode', engagement.mode_de_cours)
        engagement.periode_engagement = data.get('periode', engagement.periode_engagement)
        engagement.duree_mois = data.get('duree_mois', engagement.duree_mois)
        engagement.localisation_option = data.get('localisation', engagement.localisation_option)
        engagement.plateforme_visio_preferee = data.get('visio', engagement.plateforme_visio_preferee)
        
        enfant_id = data.get('enfant_id')
        if enfant_id:
            enfant = Enfant.objects.filter(id=enfant_id).first()
            if enfant:
                engagement.enfants_concernes.set([enfant])
        else:
            engagement.enfants_concernes.clear()

        engagement.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_finalize_engagement(request, engagement_id):
    """API pour qu'un parent finalise un engagement après accord."""
    from .choices import StatutGeneral
    from .models import Engagement
    
    engagement = get_object_or_404(Engagement, id=engagement_id)
    
    if engagement.parent_apprenant != request.user:
        return JsonResponse({'error': 'Action non autorisée'}, status=403)
        
    try:
        engagement.statut_general = StatutGeneral.FINALISE
        engagement.save()
        
        # Mettre à jour stats prof
        teacher = engagement.professeur
        teacher.nb_engagements_finalises = Engagement.objects.filter(professeur=teacher, statut_general=StatutGeneral.FINALISE).count()
        teacher.save()
        
        return JsonResponse({'success': True, 'message': 'Engagement finalisé avec succès'})
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


@login_required
def profil_eleve(request, type_eleve, id_eleve):
    from django.http import Http404
    from .choices import ObjectifMotivation, ObjectifApprenant
    
    obj_dict = dict(ObjectifMotivation.CHOICES)
    obj_dict.update(dict(ObjectifApprenant.CHOICES))
    is_owner = False
    is_teacher = getattr(request.user.profile, 'role', '') == Profile.ROLE_PROF
    eleve_data = {}

    if type_eleve == 'enfant':
        enfant = get_object_or_404(Enfant, id=id_eleve)
        
        if hasattr(request.user, 'parent') and enfant.parent == request.user.parent:
            is_owner = True
        elif not is_teacher:
            raise Http404("Profil introuvable ou accès refusé.")
            
        obj_text = enfant.objectif_principal
        objectifs = []
        difficultes = []
        if obj_text and "DIFFICULTÉS:" in obj_text:
            parts = obj_text.split("DIFFICULTÉS:")
            obj_str = parts[0].replace("OBJECTIFS:", "").strip()
            diff_str = parts[1].strip()
            objectifs = [o.strip() for o in obj_str.split(',') if o.strip()]
            difficultes = [d.strip() for d in diff_str.split(',') if d.strip()]
        elif obj_text:
            objectifs = [obj_text]

        if not difficultes and enfant.besoin_prioritaire:
            difficultes = [enfant.besoin_prioritaire]

        # Map objectives to display names
        objectifs = [obj_dict.get(o, o) for o in objectifs]

        eleve_data = {
            'type': 'enfant',
            'id': enfant.id,
            'nom': enfant.prenom,
            'photo_url': None,
            'quartier_ville': enfant.quartier_ville,
            'classe': enfant.get_classe_display() if hasattr(enfant, 'get_classe_display') else enfant.classe,
            'matieres': enfant.matieres,
            'difficultes': difficultes,
            'objectifs': objectifs
        }
    elif type_eleve == 'apprenant':
        apprenant = get_object_or_404(Apprenant, id=id_eleve)
        
        if apprenant.user == request.user:
            is_owner = True
        elif not is_teacher:
            raise Http404("Profil introuvable ou accès refusé.")
            
        eleve_data = {
            'type': 'apprenant',
            'id': apprenant.id,
            'nom': apprenant.nom,
            'photo_url': apprenant.photo_de_profil.url if apprenant.photo_de_profil else None,
            'quartier_ville': getattr(apprenant, 'quartier_ville', "Non spécifié"),
            'classe': apprenant.get_classe_display() if hasattr(apprenant, 'get_classe_display') else apprenant.classe,
            'matieres': apprenant.matieres_recherchees,
            'difficultes': [apprenant.description_difficultes] if apprenant.description_difficultes else [],
            'objectifs': [obj_dict.get(o, o) for o in apprenant.objectifs_motivations]
        }
    else:
        raise Http404("Type d'élève invalide.")

    return render(request, "core/profil_eleve.html", {
        "eleve": eleve_data,
        "is_owner": is_owner,
        "is_teacher": is_teacher
    })


# ==========================================
# ESPACE DE SUIVI PÉDAGOGIQUE
# ==========================================

@login_required
def suivi_engagement(request, engagement_id):
    from django.http import Http404
    engagement = get_object_or_404(Engagement, id=engagement_id)
    
    is_parent_apprenant = engagement.parent_apprenant == request.user
    is_prof = hasattr(request.user, 'teacher_profile') and engagement.professeur == request.user.teacher_profile
    if not (is_parent_apprenant or is_prof):
        raise Http404("Accès refusé.")
        
    seances = engagement.seances.all().order_by('-date_seance')[:5]
    
    return render(request, "core/suivi_engagement.html", {
        "engagement": engagement,
        "seances": seances,
        "is_parent_apprenant": is_parent_apprenant,
        "is_prof": is_prof,
    })

@login_required
def toutes_seances(request, engagement_id):
    from django.http import Http404
    engagement = get_object_or_404(Engagement, id=engagement_id)
    
    is_parent_apprenant = engagement.parent_apprenant == request.user
    is_prof = hasattr(request.user, 'profile') and engagement.professeur == request.user.profile
    if not (is_parent_apprenant or is_prof):
        raise Http404("Accès refusé.")
        
    seances = engagement.seances.all().order_by('-date_seance')
    
    mois = request.GET.get('mois')
    taux = request.GET.get('taux')
    
    if mois:
        try:
            from datetime import datetime
            mois_date = datetime.strptime(mois, "%Y-%m").date()
            seances = seances.filter(mois_index=mois_date)
        except ValueError:
            pass
            
    if taux == 'faible':
        seances = seances.filter(taux_maitrise_seance__lt=40)
    elif taux == 'moyen':
        seances = seances.filter(taux_maitrise_seance__gte=40, taux_maitrise_seance__lte=80)
    elif taux == 'excellent':
        seances = seances.filter(taux_maitrise_seance__gt=80)
        
    return render(request, "core/toutes_seances.html", {
        "engagement": engagement,
        "seances": seances,
    })

@login_required
def api_ajouter_seance(request, engagement_id):
    from .models import Seance, NotionSeance
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée."}, status=405)
        
    engagement = get_object_or_404(Engagement, id=engagement_id)
    if not (hasattr(request.user, 'profile') and engagement.professeur == request.user.profile):
        return JsonResponse({"error": "Accès refusé. Seul le professeur peut ajouter une séance."}, status=403)
        
    try:
        from datetime import datetime
        date_seance_str = request.POST.get('date_seance')
        date_seance = datetime.strptime(date_seance_str, "%Y-%m-%d").date()
        objectifs = request.POST.get('objectifs')
        difficultes_presentes = request.POST.get('difficultes_presentes') == 'oui'
        difficultes_rencontrees = request.POST.get('difficultes_rencontrees', '')
        taches_domicile = request.POST.get('taches_domicile', '')
        
        import json
        notions_data = request.POST.get('notions_json')
        if not notions_data:
            return JsonResponse({"error": "Aucune notion trouvée."}, status=400)
            
        notions = json.loads(notions_data)
        if len(notions) == 0:
            return JsonResponse({"error": "Au moins une notion est requise."}, status=400)
            
        total_points_obtenus = sum(int(n.get('score', 0)) for n in notions)
        total_points_max = len(notions) * 3
        taux_maitrise = (total_points_obtenus / total_points_max) * 100 if total_points_max > 0 else 0
        
        from decimal import Decimal
        
        seance = Seance.objects.create(
            engagement=engagement,
            date_seance=date_seance,
            objectifs=objectifs,
            difficultes_presentes=difficultes_presentes,
            difficultes_rencontrees=difficultes_rencontrees,
            taches_domicile=taches_domicile,
            total_points_obtenus=Decimal(str(total_points_obtenus)),
            total_points_max=Decimal(str(total_points_max)),
            taux_maitrise_seance=Decimal(str(round(taux_maitrise, 1))),
            mois_index=date_seance.replace(day=1)
        )
        
        for n in notions:
            NotionSeance.objects.create(
                seance=seance,
                nom_notion=n.get('nom'),
                score=int(n.get('score', 0))
            )
            
        if engagement.total_points_obtenus_matiere is None:
            engagement.total_points_obtenus_matiere = Decimal('0')
        if engagement.total_points_max_matiere is None:
            engagement.total_points_max_matiere = Decimal('0')
            
        engagement.total_points_obtenus_matiere += Decimal(str(total_points_obtenus))
        engagement.total_points_max_matiere += Decimal(str(total_points_max))
        
        if engagement.total_points_max_matiere > 0:
            engagement.taux_global_matiere = (engagement.total_points_obtenus_matiere / engagement.total_points_max_matiere) * 100
        
        engagement.save()
        
        return JsonResponse({"success": True, "message": "Séance ajoutée avec succès."})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@login_required
def api_valider_seance(request, seance_id):
    from .models import Seance
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée."}, status=405)
        
    seance = get_object_or_404(Seance, id=seance_id)
    if seance.engagement.parent_apprenant != request.user:
        return JsonResponse({"error": "Accès refusé. Seul le parent/apprenant peut valider."}, status=403)
        
    seance.validee = True
    seance.save()
    return JsonResponse({"success": True})


@login_required
def toggle_favori(request, prof_id):
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée."}, status=405)
    
    prof = get_object_or_404(TeacherProfile, id=prof_id)
    if request.user in prof.parents_favoris.all():
        prof.parents_favoris.remove(request.user)
        is_favorite = False
    else:
        prof.parents_favoris.add(request.user)
        is_favorite = True
        
    return JsonResponse({"success": True, "is_favorite": is_favorite})

@login_required
def masquer_engagement(request, eng_id):
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée."}, status=405)
        
    engagement = get_object_or_404(Engagement, id=eng_id)
    if engagement.parent_apprenant != request.user:
        return JsonResponse({"error": "Accès refusé."}, status=403)
        
    engagement.masque_par_parent = True
    engagement.save()
    return JsonResponse({"success": True})

@login_required
def masquer_engagement_prof(request, eng_id):
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée."}, status=405)
        
    engagement = get_object_or_404(Engagement, id=eng_id)
    if not hasattr(request.user, 'teacher_profile') or engagement.professeur != request.user.teacher_profile:
        return JsonResponse({"error": "Accès refusé."}, status=403)
        
    engagement.masque_pour_professeur = True
    engagement.save()
    return JsonResponse({"success": True})


@login_required
def api_toggle_essai(request):
    """Bascule l'activation de l'essai gratuit pour le professeur connecté."""
    try:
        teacher = request.user.teacher_profile
    except TeacherProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Accès réservé aux professeurs.'}, status=403)

    if request.method == 'POST':
        teacher.essai_gratuit_actif = not teacher.essai_gratuit_actif
        teacher.save()
        return JsonResponse({
            'success': True,
            'actif': teacher.essai_gratuit_actif,
            'message': 'Statut de l\'essai gratuit mis à jour.'
        })
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'}, status=405)


@login_required
def api_engagement_details(request, engagement_id):
    """API pour récupérer les détails complets d'un engagement (pour les modaux)."""
    engagement = get_object_or_404(Engagement, id=engagement_id)
    
    # Sécurité: Seuls les acteurs de l'engagement peuvent voir les détails
    is_prof = hasattr(request.user, 'teacher_profile') and engagement.professeur == request.user.teacher_profile
    is_client = engagement.parent_apprenant == request.user
    
    if not (is_prof or is_client):
        return JsonResponse({'error': 'Accès refusé'}, status=403)
        
    data = {
        'id': engagement.id,
        'matiere': engagement.matiere,
        'classe': engagement.get_classe_display(),
        'mode': engagement.get_mode_de_cours_display(),
        'mode_raw': engagement.mode_de_cours,
        'lieu': engagement.localisation_option,
        'budget': str(engagement.budget_convenu) if engagement.budget_convenu else None,
        'frequence': engagement.get_frequence_hebdomadaire_display(),
        'duree': engagement.get_duree_seance_display(),
        'duree_mois': engagement.duree_mois,
        'date_debut': engagement.date_debut.strftime("%d/%m/%Y") if engagement.date_debut else None,
        'status': engagement.statut_general,
        'type': engagement.type_engagement,
        'type_label': engagement.get_type_engagement_display(),
        'plateforme': engagement.plateforme_visio_preferee,
        # IDs for conversion logic
        'teacher_id': engagement.professeur.id,
        'teacher_name': f"{engagement.professeur.prenom} {engagement.professeur.nom}",
        'student_id': engagement.enfants_concernes.first().id if engagement.enfants_concernes.exists() else (engagement.parent_apprenant.apprenant.id if hasattr(engagement.parent_apprenant, 'apprenant') else None),
        'student_name': engagement.enfants_concernes.first().prenom if engagement.enfants_concernes.exists() else (engagement.parent_apprenant.apprenant.nom if hasattr(engagement.parent_apprenant, 'apprenant') else "Moi-même"),
        # Essai specific fields
        'date_essai': engagement.date_heure_essai.strftime("%d/%m/%Y") if engagement.date_heure_essai else None,
        'heure_debut': engagement.date_heure_essai.strftime("%H:%M") if engagement.date_heure_essai else None,
        'heure_fin': engagement.date_heure_fin_essai.strftime("%H:%M") if engagement.date_heure_fin_essai else None,
        'description_essai': engagement.description_essai,
    }
    
    return JsonResponse({'success': True, 'engagement': data})

@login_required
@require_http_methods(["POST"])
def api_fictional_payment(request):
    """API de paiement fictif interne pour les tests."""
    import json
    from .choices import TypeAbonnement
    from .models import Conversation, Abonnement
    
    try:
        data = json.loads(request.body)
        conversation_id = data.get('conversation_id')
        payment_type = data.get('payment_type') # 'standard' ou 'premium'
        
        if payment_type == 'standard':
            if not conversation_id:
                return JsonResponse({'error': 'ID de conversation requis'}, status=400)
            
            conversation = get_object_or_404(Conversation, id=conversation_id)
            if request.user not in conversation.participants.all():
                return JsonResponse({'error': 'Accès non autorisé'}, status=403)
                
            eng = conversation.engagement_actif
            if not eng:
                return JsonResponse({'error': 'Aucun engagement actif pour cette conversation'}, status=400)
                
            eng.paiement_effectue = True
            eng.save()
            return JsonResponse({'status': 'success', 'message': 'Paiement standard effectué (fictif)'})
            
        elif payment_type == 'premium':
            # Upgrade vers premium pour le mois en cours
            from datetime import timedelta
            abonnement = request.user.abonnements.first()
            if not abonnement:
                abonnement = Abonnement.objects.create(user=request.user)
            
            abonnement.type_abonnement = TypeAbonnement.ACCESS_PREMIUM
            abonnement.date_debut = timezone.now().date()
            abonnement.date_fin = timezone.now().date() + timedelta(days=30)
            abonnement.save()
            return JsonResponse({'status': 'success', 'message': 'Passage au plan Premium effectué (fictif)'})
            
        else:
            return JsonResponse({'error': 'Type de paiement invalide'}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_archive_conversation(request, conversation_id):
    """Archive ou désarchive une conversation pour l'utilisateur courant."""
    from .models import Conversation
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.user not in conversation.participants.all():
        return JsonResponse({'error': 'Non autorisé'}, status=403)
        
    if request.user in conversation.archivee_par.all():
        conversation.archivee_par.remove(request.user)
        is_archived = False
    else:
        conversation.archivee_par.add(request.user)
        is_archived = True
        
    return JsonResponse({'success': True, 'archivee': is_archived})


@login_required
@require_http_methods(["POST"])
def api_delete_conversation(request, conversation_id):
    """Soft-delete : masque la conversation pour l'utilisateur courant."""
    from .models import Conversation
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.user not in conversation.participants.all():
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    conversation.masquee_par.add(request.user)
    return JsonResponse({'success': True})
