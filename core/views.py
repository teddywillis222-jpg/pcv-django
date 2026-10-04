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



from django.db import transaction

from django.utils import timezone

from .forms import (

    ApprenantCreateProfileForm,

    EnfantForm,

    FinalisationCompteForm,

    LoginForm,

    ParentForm,

    SignUpForm,

)

from .choices import TypeAbonnement, StatutGeneral, EngagementType, ValidationStatus, Localisation, CourseMode

from .models import (
    Abonnement, Apprenant, Enfant, Parent, Profile, TeacherProfile,
    Engagement, Message, ProfessorAnnouncement, ProfileReaction, SiteConfiguration
)

from django.db.models import Q


from django.template.loader import render_to_string





def annotate_teachers_with_ratings(queryset):

    """

    Annote un queryset de TeacherProfile avec :

    - Les moyennes d'avis rÃ©els ou d'Ã©quipe (moyenne_avis, nombre_avis, has_real_reviews)

    - Le badge "Suivi Rigoureux" (suivi_rigoureux) selon la rÃ¨gle d'assiduitÃ© par rÃ©cence :

        * Condition 1 (Seuil) : >= 3 bilans de sÃ©ances enregistrÃ©s au total

        * Condition 2 (RÃ©cence) : SI engagement actif (FINALISE), le dernier bilan < 14 jours

                                   SI aucun engagement actif, la rÃ¨gle de rÃ©cence est ignorÃ©e

    """

    from django.db.models.functions import Coalesce, Cast, Now

    from django.db.models import (

        F, Case, When, Value, BooleanField, IntegerField,

        Avg, Count, DecimalField, FloatField, Max, Q, ExpressionWrapper, DurationField

    )

    from django.utils import timezone



    # Seuil : nombre total de bilans de sÃ©ances (Seance) enregistrÃ©s par ce prof

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

        #   - Soit aucun engagement actif (on ignore la rÃ©cence)

        #   - Soit le dernier bilan date de moins de SUIVI_RIGOUREUX_JOURS_RECENCE jours

        suivi_rigoureux=Case(

            # Seuil non atteint Ã¢â€ â€™ False (nouveaux profs ou profs qui n'ont jamais rempli)

            When(_nb_bilans_total__lt=settings.SUIVI_RIGOUREUX_SEUIL_BILANS, then=Value(False)),

            # Seuil atteint + aucun engagement actif Ã¢â€ â€™ True (bon passif, pas pÃ©nalisÃ©)

            When(_nb_engagements_actifs=0, then=Value(True)),

            # Seuil atteint + engagement actif + dernier bilan rÃ©cent Ã¢â€ â€™ True

            When(

                _nb_engagements_actifs__gt=0,

                _date_dernier_bilan__gte=date_limite_rigueur,

                then=Value(True)

            ),

            # Seuil atteint + engagement actif + dernier bilan trop ancien Ã¢â€ â€™ False

            default=Value(False),

            output_field=BooleanField()

        )

    )





def home(request):

    from django.utils import timezone

    import datetime

    

    # Date d'ouverture officielle : 15 Juin 2026

    ouverture_date = timezone.make_aware(datetime.datetime(2026, 6, 15, 0, 0, 0))

    if timezone.now() < ouverture_date:

        return render(request, "core/waiting.html")



    from .choices import ValidationStatus
    from .models import Quartier
    from django.db.models import Q
    from django.conf import settings

    # MatiÃ¨res cibles pour les profils recommandÃ©s sur la page d'accueil
    target_matieres_q = (
        Q(matiere_enseignee__icontains="Math") |
        Q(matiere_enseignee__icontains="Anglais") |
        Q(matiere_enseignee__icontains="SVT") |
        Q(matiere_enseignee__icontains="PCT") |
        Q(matiere_enseignee__icontains="Physique")
    )

    # RÃ©cupÃ©ration de la liste des emails recommandÃ©s et de test configurÃ©s dans settings
    recommended_emails = getattr(settings, 'RECOMMENDED_TEACHER_EMAILS', [])
    test_emails = getattr(settings, 'TEST_ACCOUNT_EMAILS', [])

    top_professeurs = []

    # 1. PrioritÃ© aux 4 profils spÃ©cifiques choisis pour la vitrine d'accueil
    if recommended_emails:
        recommended_qs = TeacherProfile.objects.select_related('user').filter(
            Q(user__email__in=recommended_emails) | Q(email__in=recommended_emails)
        )
        if test_emails:
            recommended_qs = recommended_qs.exclude(
                Q(user__email__in=test_emails) | Q(email__in=test_emails)
            )
        top_professeurs = list(annotate_teachers_with_ratings(recommended_qs[:4]))

    # 2. Si les 4 profils ne sont pas tous trouvÃ©s (ex: environnement local), complÃ©ter jusqu'Ã  4
    if len(top_professeurs) < 4:
        existing_ids = [p.id for p in top_professeurs]
        base_profs_qs = TeacherProfile.objects.select_related('user').filter(
            statut_de_validation=ValidationStatus.VALIDE
        ).filter(target_matieres_q).exclude(id__in=existing_ids)

        if test_emails:
            base_profs_qs = base_profs_qs.exclude(
                Q(user__email__in=test_emails) | Q(email__in=test_emails)
            )

        needed = 4 - len(top_professeurs)
        fillers = list(annotate_teachers_with_ratings(base_profs_qs.order_by('-profil_complet', '?')[:needed]))
        top_professeurs.extend(fillers)

    quartiers_disponibles = Quartier.objects.filter(
        professeurs__statut_de_validation=ValidationStatus.VALIDE
    ).distinct().order_by('ville', 'nom')

    return render(request, "core/home.html", {
        "top_professeurs": top_professeurs,
        "quartiers_disponibles": quartiers_disponibles,
    })



def faq(request):

    """Page FAQ - Questions frÃ©quentes"""

    return render(request, "core/faq.html")



def support(request):

    """Page Support - Aide et assistance"""

    return render(request, "core/support.html")



def cgu(request):

    """Page des Conditions GÃ©nÃ©rales d'Utilisation"""

    return render(request, "core/cgu.html")



def politique_confidentialite(request):

    """Page de la Politique de ConfidentialitÃ©"""

    return render(request, "core/politique_confidentialite.html")



@login_required

def messagerie(request):

    """Page Messagerie - Liste des discussions avec filtres et recherche intelligente."""

    from .choices import StatutGeneral

    from .models import Conversation, Profile as Role, Profile

    

    # SÃ©curitÃ© RÃ´le

    try:

        user_profile = request.user.profile

    except Profile.DoesNotExist:

        return redirect("finalisation_compte")



    # Base Queryset optimisÃ©

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



    # 3. Traitement des donnÃ©es pour le template (Contextualisation)

    formatted_conversations = []

    for conv in conversations:

        eng = conv.engagement_actif

        # DÃ©terminer le nom, la photo et l'initiale Ã  afficher

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

            enfants_liste = []

            if eng and eng.enfants_concernes.exists():

                enfants_liste = eng.enfants_concernes.all()

            if not enfants_liste:

                # Chercher un autre engagement dans cette conversation

                for e in conv.engagements.all():

                    if e.enfants_concernes.exists():

                        enfants_liste = e.enfants_concernes.all()

                        break

            if not enfants_liste and hasattr(conv.parent, 'parent'):

                # Prendre le premier enfant du parent par dÃ©faut

                enfants_liste = conv.parent.parent.enfants.all()

                

            if enfants_liste:

                enfants_names = ", ".join([e.prenom for e in enfants_liste])

                if len(enfants_names) > 18: enfants_names = enfants_names[:16] + "..."

                display_name = f"Parent de {enfants_names}"

            else:

                if conv.parent and hasattr(conv.parent, 'profile'):

                    if conv.parent.profile.role == Role.ROLE_APPRENANT and hasattr(conv.parent, 'apprenant'):

                        # Le modÃ¨le Apprenant n'a pas de prenom, on utilise nom + first_name du User

                        apprenant_nom = conv.parent.apprenant.nom or conv.parent.first_name or conv.parent.username

                        display_name = f"{apprenant_nom}"

                    elif hasattr(conv.parent, 'parent'):

                        display_name = f"Parent {conv.parent.parent.nom}"

                    else:

                        display_name = conv.parent.first_name or "Parent PCV"

                else:

                    display_name = "Utilisateur PCV"

            

            # Initiale basÃ©e sur le prÃ©nom de l'utilisateur parent

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

        statut_label = ""

        statut_class = "statut-default"

        

        if eng:

            from .choices import StatutGeneral

            if eng.statut_general in [StatutGeneral.FINALISE, StatutGeneral.ENGAGEMENT_FINALISE]:

                statut_label = "Actif"

                statut_class = "statut-active"

            elif eng.statut_general == StatutGeneral.TERMINE:

                statut_label = "TerminÃ©"

                statut_class = "statut-finished"

            elif eng.statut_general in [StatutGeneral.EN_ATTENTE, StatutGeneral.CONFIRME, StatutGeneral.EN_COURS, StatutGeneral.ESSAI_PROGRAMME, StatutGeneral.ESSAI_CONFIRME]:

                statut_label = "En cours"

                statut_class = "statut-pending"



        # Blocage Messagerie (SUPPRIMÃ‰)

        is_blocked = False



        # Backfill du dernier message si le champ est vide (conversations crÃ©Ã©es avant la correction)

        if not conv.dernier_message_texte:

            last_msg = conv.messages.order_by('-date_envoi').first()

            if last_msg:

                if last_msg.contenu_media:

                    try:

                        is_img = 'image' in last_msg.contenu_media.url

                    except Exception:

                        is_img = False

                    prefix = "ðŸ“· Photo" if is_img else "ðŸ“„ Fichier"

                    conv.dernier_message_texte = f"{prefix} {last_msg.contenu_texte}" if last_msg.contenu_texte else prefix

                else:

                    conv.dernier_message_texte = last_msg.contenu_texte

                conv.dernier_message_date = last_msg.date_envoi

                conv.dernier_message_auteur = last_msg.auteur

                conv.save(update_fields=['dernier_message_texte', 'dernier_message_date', 'dernier_message_auteur'])



        # Non-lus (utilise le compteur annotÃ© pour performance)

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

    

    if request.user.is_authenticated and request.user.email not in getattr(settings, 'TEST_ACCOUNT_EMAILS', []):

        if hasattr(request.user, 'parent_profile'):

            request.user.parent_profile.nb_recherches += 1

            request.user.parent_profile.save(update_fields=['nb_recherches'])

        elif hasattr(request.user, 'apprenant'):

            request.user.apprenant.nb_recherches += 1

            request.user.apprenant.save(update_fields=['nb_recherches'])



    from .choices import ValidationStatus, CourseMode, Localisation, ClassLevel, SupportCategory, Matiere

    professeurs = TeacherProfile.objects.select_related('user').prefetch_related('quartiers_couverts').filter(
        statut_de_validation=ValidationStatus.VALIDE
    )

    

    # RÃ©cupÃ©ration des paramÃ¨tres de recherche

    matiere = request.GET.get('matiere', '').strip()

    localisation = request.GET.get('localisation', '').strip()

    classe = request.GET.get('classe', '').strip()

    prix = request.GET.get('prix', '').strip()

    mode = request.GET.get('mode', '').strip()

    soutien = request.GET.get('soutien', '').strip()



    if matiere:

        professeurs = professeurs.filter(matiere_enseignee__icontains=matiere)

    if localisation:

        professeurs = professeurs.filter(quartiers_couverts__id=localisation)

    if classe:

        from django.db.models import Case, When, Value, BooleanField

        professeurs = professeurs.filter(

            Q(classes_expertise__icontains=classe) | Q(classes_enseignees__icontains=classe)

        ).annotate(

            is_expert_classe=Case(

                When(classes_expertise__icontains=classe, then=Value(True)),

                default=Value(False),

                output_field=BooleanField()

            )

        )

    if mode:

        professeurs = professeurs.filter(modes_de_cours__icontains=mode)

    if soutien:

        professeurs = professeurs.filter(categories_de_soutien__icontains=soutien)

        

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



    # 3. Annotation des ratings + badge Suivi Rigoureux via le helper centralisÃ©

    professeurs = annotate_teachers_with_ratings(professeurs)



    # 4. Tri des rÃ©sultats

    sort_by = request.GET.get('sort', '').strip()

    if sort_by == 'recent_active':

        professeurs = professeurs.order_by('-user__last_login', '-id')

    else:

        # Ordre par défaut : Actifs récemment > Score fiabilité > Moyenne avis > Profil complet
        # Si filtre classe : Expert de la classe en premier

        sort_args = []

        if classe:
            sort_args.append('-is_expert_classe')

        sort_args.extend([
            '-user__last_login',
            '-score_fiabilite',
            '-moyenne_avis',
            '-profil_complet',
        ])

        professeurs = professeurs.order_by(*sort_args)



    # Contexte Parent/Enfants

    parent_children = []

    parent_children_json = "[]"

    if request.user.is_authenticated and hasattr(request.user, 'parent'):

        parent_children = list(request.user.parent.enfants.all().values('id', 'prenom'))

        parent_children_json = json.dumps(parent_children)



    # --- SEO Dynamique ---

    seo_title = "Rechercher un professeur particulier au BÃ©nin | ProfChezVous"

    seo_description = "Trouvez le professeur idÃ©al pour vos cours Ã  domicile au BÃ©nin. SÃ©lectionnez votre matiÃ¨re, votre quartier et votre niveau."



    localisation_name = ""
    if localisation:
        from .models import Quartier
        try:
            q = Quartier.objects.get(id=localisation)
            localisation_name = q.nom
        except Quartier.DoesNotExist:
            pass

    if matiere and localisation_name:

        seo_title = f"Meilleurs Professeurs de {matiere} Ã  {localisation_name} | ProfChezVous"

        seo_description = f"DÃ©couvrez nos professeurs de {matiere} certifiÃ©s disponibles Ã  {localisation_name}. Soutien scolaire de qualitÃ© Ã  domicile."

    elif matiere:

        seo_title = f"Cours particuliers de {matiere} au BÃ©nin | ProfChezVous"

        seo_description = f"Trouvez un professeur de {matiere} compÃ©tent pour des cours Ã  domicile partout au BÃ©nin. Tous niveaux."

    elif localisation_name:

        seo_title = f"Professeurs particuliers Ã  {localisation_name} | ProfChezVous"

        seo_description = f"Besoin d'un prof Ã  {localisation_name} ? DÃ©couvrez notre sÃ©lection d'enseignants vÃ©rifiÃ©s pour vos enfants."



    context = {

        'professeurs': professeurs,

        'matiere': matiere,

        'localisation': localisation,
        
        'localisation_name': localisation_name,

        'classe': classe,

        'prix': prix,

        'mode': mode,

        'soutien': soutien,

        'sort_by': sort_by,

        'parent_children': parent_children,

        'parent_children_json': parent_children_json,

        'seo_title': seo_title,

        'seo_description': seo_description,

        'searched_quartier_id': int(localisation) if localisation else None,
    }

    # Quartiers dynamiques : seulement ceux avec au moins un prof validÃ©
    from .models import Quartier
    context['quartiers_disponibles'] = Quartier.objects.filter(
        professeurs__statut_de_validation=ValidationStatus.VALIDE
    ).distinct().order_by('ville', 'nom')

    

    return render(request, "core/recherche.html", context)





def send_activation_email(request, user, next_url=None):

    from django.contrib.auth.tokens import default_token_generator

    from django.utils.http import urlsafe_base64_encode

    from django.utils.encoding import force_bytes

    from django.urls import reverse

    from django.core.mail import send_mail

    from django.conf import settings

    

    token = default_token_generator.make_token(user)

    uid = urlsafe_base64_encode(force_bytes(user.pk))

    link = request.build_absolute_uri(

        reverse('activate_account', kwargs={'uidb64': uid, 'token': token})

    )

    if next_url:
        import urllib.parse
        link += '?next=' + urllib.parse.quote(next_url)

    

    # Remplacement sÃ©curisÃ© par https en production si nÃ©cessaire

    if 'profchezvousapp.com' in link and link.startswith('http://'):

        link = link.replace('http://', 'https://')

    

    sujet = "Activation de votre compte Prof Chez Vous"

    message = f"Bonjour {user.first_name or user.username},\n\nMerci de vous Ãªtre inscrit(e) sur Prof Chez Vous.\n\nVeuillez cliquer sur le lien suivant pour activer votre compte :\n{link}\n\nÃ€ trÃ¨s vite,\nL'Ã©quipe Prof Chez Vous."

    

    try:

        send_mail(

            subject=sujet,

            message=message,

            from_email=settings.DEFAULT_FROM_EMAIL,

            recipient_list=[user.email],

            fail_silently=False,

        )

        return True

    except Exception as e:

        import logging

        logging.getLogger(__name__).error(f"Erreur d'envoi d'email Ã  {user.email}: {e}")

        return False





def signup(request):

    if request.user.is_authenticated:

        return redirect("post_signup_redirect")



    next_url = request.POST.get('next') or request.GET.get('next')



    if request.method == "POST":

        form = SignUpForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            user.is_active = False  # DÃ©sactivation jusqu'Ã  validation de l'email

            user.save()

            

            role = form.cleaned_data["role"]
            telephone = form.cleaned_data["telephone"]
            
            Profile.objects.create(user=user, role=role, telephone=telephone)
            
            # --- CrÃ©ation automatique du Profil Parent ---
            if role == Profile.ROLE_PARENT:
                from .models import Parent
                Parent.objects.get_or_create(user=user)
            elif role == Profile.ROLE_APPRENANT:
                from .models import Apprenant
                Apprenant.objects.get_or_create(user=user)

            # CrÃ©ation automatique d'abonnement (Standard, 2000f)
            Abonnement.objects.create(

                user=user,

                type_abonnement=TypeAbonnement.STANDARD,

                prix=f"{settings.DEFAULT_ENGAGEMENT_PRICE}{settings.DEFAULT_CURRENCY} par engagement",

                date_debut=date.today(),

            )

            

            # --- GÃ©nÃ©ration et envoi du token ---

            send_activation_email(request, user, next_url=next_url)

            

            # --- Rattachement au programme ambassadeur ---
            if role == Profile.ROLE_PROF:
                referral_id = request.COOKIES.get('pcv_referral_id') or request.session.get('referral_id')
                if referral_id:
                    try:
                        from referrals.models import Referral
                        referral = Referral.objects.get(id=referral_id)
                        if referral.status == 'VISITED' and referral.referred_teacher is None:
                            referral.referred_teacher = user
                            referral.status = 'ACCOUNT_CREATED'
                            from django.utils import timezone
                            referral.account_created_at = timezone.now()
                            referral.save()
                    except Exception:
                        pass
                        
            request.session['verification_email_sent'] = user.email

            

            if next_url:

                request.session['post_activation_redirect'] = next_url

                

            response = redirect("login")
            if 'referral_id' in request.session:
                del request.session['referral_id']
            response.delete_cookie('pcv_referral_id')
            return response

    else:

        form = SignUpForm()



    return render(request, "core/signup.html", {

        "form": form,

        "redirect_field_name": "next",

        "redirect_field_value": next_url

    })





def resend_activation_view(request):

    from django.contrib.auth.models import User

    from django.contrib import messages

    

    if request.method == "POST":

        email = request.POST.get("email")

        if email:

            user = User.objects.filter(email=email).first()

            if user:

                if user.is_active:

                    messages.info(request, "Ce compte est dÃ©jÃ  activÃ©. Vous pouvez vous connecter.")

                    return redirect("login")

                else:

                    send_activation_email(request, user)

                    messages.success(request, "Un nouveau lien d'activation vous a Ã©tÃ© envoyÃ© par e-mail.")

                    return redirect("login")

            else:

                messages.success(request, "Si ce compte existe et n'est pas encore activÃ©, un nouveau lien d'activation vous a Ã©tÃ© envoyÃ©.")

                return redirect("login")

                

    return render(request, "core/resend_activation.html")





def activate_account(request, uidb64, token):

    from django.contrib.auth.models import User

    from django.contrib.auth.tokens import default_token_generator

    from django.utils.http import urlsafe_base64_decode

    from django.utils.encoding import force_str

    from django.contrib import messages

    from django.contrib.auth import login

    

    try:

        uid = force_str(urlsafe_base64_decode(uidb64))

        user = User.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):

        user = None



    if user is not None and default_token_generator.check_token(user, token):

        user.is_active = True

        user.save()

        messages.success(request, "Votre compte a Ã©tÃ© activÃ© avec succÃ¨s. Bienvenue !")

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        

        # Redirection : prioritÃ© session > query string > fallback
        post_activation_redirect = (
            request.session.pop('post_activation_redirect', None)
            or request.GET.get('next')
        )

        if post_activation_redirect:

            return redirect(post_activation_redirect)

            

        return redirect("post_signup_redirect")

    else:

        messages.error(request, "Le lien d'activation est invalide ou a expirÃ©.")

        return redirect("home")





def login_view(request):

    next_url = request.POST.get('next') or request.GET.get('next')

    

    if request.user.is_authenticated:

        if next_url:

            return redirect(next_url)

        return redirect("post_signup_redirect")



    if request.method == "POST":

        form = LoginForm(request, data=request.POST)

        if form.is_valid():

            user = form.get_user()

            from django.contrib import messages

            messages.success(request, f"Heureux de vous revoir, {user.first_name} !")

            from django.contrib.auth import login

            login(request, user)

            

            if next_url:

                return redirect(next_url)

            return redirect("post_signup_redirect")

    else:

        form = LoginForm()



    verification_email_sent = request.session.pop('verification_email_sent', None)



    return render(request, "core/login.html", {

        "form": form,

        "redirect_field_name": "next",

        "redirect_field_value": next_url,

        "verification_email_sent": verification_email_sent

    })





def finalisation_compte(request):

    """Page pour finaliser le compte (rÃ´le + nom) aprÃ¨s Google Login."""

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

            telephone = form.cleaned_data["telephone"]

            profile, _ = Profile.objects.get_or_create(user=request.user, defaults={"role": role, "telephone": telephone})

            if profile.role != role or profile.telephone != telephone:

                profile.role = role

                profile.telephone = telephone

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

    Redirection intelligente aprÃ¨s connexion ou inscription.

    VÃ©rifie l'existence du profil mÃ©tier (Prof, Parent, Apprenant) pour orienter l'utilisateur.

    """

    if not request.user.is_authenticated:

        return redirect("home")



    # 1. Staff / Admin

    if request.user.is_staff or request.user.is_superuser:

        return redirect("/admin/")



    # 2. RÃ©cupÃ©ration du profil de base

    try:

        profile = request.user.profile

    except Profile.DoesNotExist:

        # Cas rare si le signal n'a pas fonctionnÃ©

        return redirect("home")



    # 3. Logique de redirection directe par rÃ´le

    

    # --- RÃ”LE : PROFESSEUR ---

    if profile.role == Profile.ROLE_PROF:

        teacher = getattr(request.user, "teacher_profile", None)

        if teacher:

            from .choices import ValidationStatus

            if teacher.statut_de_validation == ValidationStatus.VALIDE:

                return redirect("prof_dashboard")

            return redirect("prof_attente_dashboard")

        return redirect("prof_create_profile")



    # --- RÃ”LE : PARENT ---

    elif profile.role == Profile.ROLE_PARENT:

        # Profilage progressif : le parent n'a plus besoin de complÃ©ter de profil

        return redirect("parent_dashboard")



    # --- RÃ”LE : APPRENANT (Ã‰lÃ¨ve autonome) ---
    elif profile.role == Profile.ROLE_APPRENANT:
        # Profilage progressif : l'apprenant n'a plus besoin de complÃ©ter de profil
        return redirect("apprenant_dashboard")



    # Par dÃ©faut

    return redirect("home")





from .forms import TeacherProfileForm, TeacherVideoPresentationForm



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

        elif teacher_instance.statut_de_validation != ValidationStatus.INCOMPLET:

            return redirect("prof_attente_dashboard")



    if request.method == "POST":

        form = TeacherProfileForm(request.POST, request.FILES, instance=teacher_instance)

        if form.is_valid():

            teacher = form.save(commit=False)

            teacher.user = request.user

            teacher.telephone_whatsapp = request.user.profile.telephone

            

            # Gestion intelligente du nom (Allauth split ou Nom complet)

            full_name = request.user.get_full_name() or request.user.first_name or request.user.username

            if " " in full_name and not request.user.last_name:

                teacher.prenom, teacher.nom = full_name.split(" ", 1)

            else:

                teacher.prenom = request.user.first_name

                teacher.nom = request.user.last_name or " "



            teacher.statut_de_validation = ValidationStatus.EN_ATTENTE

            teacher.message_admin = ""

            teacher.save()

            form.save_m2m()  # Sauvegarde des M2M (quartiers_couverts, etc.)

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

            "email": request.user.email,

            "telephone_whatsapp": request.user.profile.telephone

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

    

    # On ne redirige plus automatiquement pour permettre d'afficher le message de succÃ¨s sur cette page

    # if teacher_instance.statut_de_validation == ValidationStatus.VALIDE:

    #     return redirect("prof_dashboard")



    if request.method == "POST":

        from django.contrib import messages

        presentation = request.POST.get("presentation", "").strip()

        methodologie = request.POST.get("methodologie", "").strip()

        exp_str = request.POST.get("annees_d_experience", "").strip()

        disponibilites = request.POST.getlist("disponibilites")

        

        errors = []

        if len(presentation) < 800:

            errors.append("La prÃ©sentation doit contenir au moins 150 mots (env. 800 caractÃ¨res).")

        if len(methodologie) < 800:

            errors.append("La mÃ©thodologie doit contenir au moins 150 mots (env. 800 caractÃ¨res).")

            

        try:

            exp_val = int(exp_str)

            if exp_val < 0:

                errors.append("L'expÃ©rience ne peut pas Ãªtre nÃ©gative.")

        except ValueError:

            errors.append("Les annÃ©es d'expÃ©rience doivent Ãªtre un nombre entier valide.")



        if errors:

            for error in errors:

                messages.error(request, error)

        else:

            teacher_instance.presentation = presentation

            teacher_instance.methodologie = methodologie

            teacher_instance.annees_d_experience = exp_val

            teacher_instance.grille_disponibilites = disponibilites

            teacher_instance.save()

            messages.success(request, "Votre vitrine a Ã©tÃ© mise Ã  jour avec succÃ¨s !")

            

        return redirect("prof_attente_dashboard")



    # Calcul pourcentage complÃ©tion

    completion = teacher_instance.completion_percentage

    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    

    return render(request, "core/prof_attente_dashboard.html", {

        "teacher": teacher_instance,

        "completion": completion,

        "jours": jours

    })





@login_required

def prof_edit_profile(request):

    """Page d'Ã©dition du profil pour le professeur (Workflow complet)"""

    try:

        profile = request.user.profile

        teacher = request.user.teacher_profile

    except (Profile.DoesNotExist, TeacherProfile.DoesNotExist):

        return redirect("home")



    if profile.role != Profile.ROLE_PROF:

        return redirect("home")



    if request.method == "POST":

        form = TeacherProfileForm(request.POST, request.FILES, instance=teacher, is_editing=True)

        if form.is_valid():

            teacher = form.save(commit=False)

            teacher.grille_disponibilites = request.POST.getlist("disponibilites")

            teacher.save()

            # On sauvegarde aussi les relations many-to-many du formulaire

            form.save_m2m()

            return redirect("prof_dashboard")

    else:

        form = TeacherProfileForm(instance=teacher, is_editing=True)



    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]



    return render(request, "core/prof_edit_profile.html", {

        "form": form,

        "teacher": teacher,

        "jours": jours,

        "localisation_choices": Localisation.CHOICES

    })





@login_required

def prof_video_presentation(request):
    """Page de gestion et de soumission multi-vidÃ©os YouTube du professeur."""
    from .forms import TeacherVideoSubmissionForm
    from .models import TeacherVideo
    from django.contrib import messages

    try:
        profile = request.user.profile
        teacher = request.user.teacher_profile
    except (Profile.DoesNotExist, TeacherProfile.DoesNotExist):
        return redirect("home")

    if profile.role != Profile.ROLE_PROF:
        return redirect("home")

    site_config = SiteConfiguration.get_solo()
    if not site_config.allow_teacher_video_submissions:
        messages.warning(request, "La soumission et la gestion des vidÃ©os de prÃ©sentation sont temporairement dÃ©sactivÃ©es par l'administration.")
        return redirect("prof_dashboard")

    if request.method == "POST":
        form = TeacherVideoSubmissionForm(request.POST)
        if form.is_valid():
            video = form.save(teacher=teacher)
            messages.success(
                request,
                "Votre vidÃ©o a Ã©tÃ© soumise avec succÃ¨s ! Elle est dÃ©sormais en cours d'examen par notre Ã©quipe. "
                "Vous recevrez une notification par email dÃ¨s qu'elle sera validÃ©e."
            )
            return redirect("prof_video_presentation")
        else:
            messages.error(request, "Une erreur est survenue lors de la soumission de votre lien vidÃ©o.")
    else:
        form = TeacherVideoSubmissionForm()

    # Liste ordonnÃ©e des vidÃ©os du professeur
    videos = teacher.videos.all().order_by("-date_soumission")

    from django.core.cache import cache
    guide_video = cache.get("guide_video_prof")
    if guide_video is None:
        from .models import RessourceProfesseur
        from django.db.models import Q
        guide_video = RessourceProfesseur.objects.filter(actif=True).filter(
            Q(titre__icontains="vidÃ©o") | Q(titre__icontains="video")
        ).first()
        cache.set("guide_video_prof", guide_video if guide_video else False, 86400)
    elif guide_video is False:
        guide_video = None

    return render(request, "core/prof_video_presentation.html", {
        "form": form,
        "teacher": teacher,
        "videos": videos,
        "ValidationStatus": ValidationStatus,
        "guide_video": guide_video,
    })


@login_required
def prof_delete_video(request, video_id):
    """Permet au professeur de supprimer une de ses vidÃ©os."""
    from .models import TeacherVideo
    from django.contrib import messages

    if request.method == "POST":
        try:
            teacher = request.user.teacher_profile
            video = TeacherVideo.objects.get(id=video_id, teacher=teacher)
            video.delete()
            messages.success(request, "La vidÃ©o a Ã©tÃ© supprimÃ©e avec succÃ¨s.")
        except (TeacherProfile.DoesNotExist, TeacherVideo.DoesNotExist):
            messages.error(request, "VidÃ©o introuvable ou action non autorisÃ©e.")

    return redirect("prof_video_presentation")






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



    # 1. Gestion des Engagements

    engagements_base = teacher.engagements.select_related(

        'parent_apprenant', 'parent_apprenant__profile', 'parent_apprenant__apprenant'

    ).prefetch_related(

        'enfants_concernes', 'conversation'

    ).order_by("-date_creation")

    

    engs_tous = list(engagements_base)

    

    for eng in engs_tous:

        eng.check_and_update_essai_status()

    

    engs_essais_programmes = [e for e in engs_tous if e.statut_general == StatutGeneral.ESSAI_PROGRAMME]

    engs_essais_confirmes = [e for e in engs_tous if e.statut_general in [StatutGeneral.ESSAI_CONFIRME, StatutGeneral.ESSAI_REALISE]]

    engs_finalises = [e for e in engs_tous if e.statut_general == StatutGeneral.FINALISE]

    engs_termines = [e for e in engs_tous if e.statut_general == StatutGeneral.TERMINE]



    # 2. Statistiques dynamiques (calculÃ©es en mÃ©moire pour Ã©viter d'autres requÃªtes)

    nb_actifs = sum(1 for e in engs_tous if e.statut_general == StatutGeneral.FINALISE and e.type_engagement != EngagementType.ESSAI)

    nb_termines = sum(1 for e in engs_tous if e.statut_general == StatutGeneral.TERMINE and e.type_engagement != EngagementType.ESSAI)

    

    # 3. Centre de Notifications (Messages non lus)

    unread_messages_count = Message.objects.filter(

        destinataire=request.user,

        lu=False

    ).count()



    # 4. Parents Favoris

    parents_favoris = teacher.parents_favoris.all()



    context = {

        "teacher": teacher,

        "engs_essais_programmes": engs_essais_programmes,

        "engs_essais_confirmes": engs_essais_confirmes,

        "engs_finalises": engs_finalises,

        "engs_termines": engs_termines,

        "engs_tous": engs_tous,

        "unread_count": unread_messages_count,

        "parents_favoris": parents_favoris,

        "completion": teacher.completion_percentage,

        "nb_actifs": nb_actifs,

        "nb_termines": nb_termines,

        "badge_essais_programmes": len(engs_essais_programmes),

        "badge_essais_confirmes": len(engs_essais_confirmes),

        "show_welcome_popup": not request.user.profile.a_vu_popup_bienvenue,
        "show_visite_guidee": not teacher.a_vu_visite_guidee,

    }



    # Annonce

    announcement = ProfessorAnnouncement.objects.filter(is_active=True, target_audience__in=['PROF', 'ALL']).order_by('-created_at').first()

    if announcement and not announcement.dismissed_by.filter(id=request.user.id).exists():

        context['announcement'] = announcement



    # Statistiques Ambassadeur

    ambassador_stats = None

    if teacher.statut_de_validation == 'APPROVED':

        from referrals.models import Ambassador, Referral, Reward, ReferralProgram

        ambassador, _ = Ambassador.objects.get_or_create(user=request.user)

        

        referrals = Referral.objects.filter(referrer=request.user)

        rewards_pending = Reward.objects.filter(teacher=request.user, status='PENDING')

        rewards_paid = Reward.objects.filter(teacher=request.user, status='PAID')

        

        ambassador_stats = {

            'ambassador': ambassador,

            'visits_count': referrals.exclude(visited_at__isnull=True).count(),

            'accounts_count': referrals.filter(status__in=['ACCOUNT_CREATED', 'PROFILE_COMPLETED', 'UNDER_REVIEW', 'VERIFIED', 'REWARD_PENDING', 'REWARD_PAID']).count(),

            'profiles_completed_count': referrals.filter(status__in=['PROFILE_COMPLETED', 'UNDER_REVIEW', 'VERIFIED', 'REWARD_PENDING', 'REWARD_PAID']).count(),

            'verified_count': referrals.filter(status__in=['VERIFIED', 'REWARD_PENDING', 'REWARD_PAID']).count(),

            'total_pending_amount': sum([r.amount for r in rewards_pending]) if rewards_pending else 0,

            'total_paid_amount': sum([r.amount for r in rewards_paid]) if rewards_paid else 0,

            'current_reward': ReferralProgram.get_current_amount(),

            'referrals': referrals.exclude(status='PENDING').order_by('-created_at')[:10],

            'rewards': Reward.objects.filter(teacher=request.user).order_by('-created_at')[:10]

        }

    context['ambassador_stats'] = ambassador_stats
    context['site_config'] = SiteConfiguration.get_solo()

    from django.db.models import Sum
    from core.models import OperationScoreFiabilite
    ops = OperationScoreFiabilite.objects.filter(professeur=teacher, statut='VALIDE').values('type_operation').annotate(total=Sum('points'))
    stats_fiabilite = {
        'JOURNAL': 0,
        'REACTIVITE': 0,
        'ENGAGEMENT_TERMINE': 0,
        'AVIS': 0,
    }
    for op in ops:
        stats_fiabilite[op['type_operation']] = op['total'] or 0
    context['stats_fiabilite'] = stats_fiabilite


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

                parent_instance.numero_whatsapp = request.user.profile.telephone

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



    has_child_form_errors = False
    if request.method == "POST":
        enfant_form = EnfantForm(request.POST)
        if enfant_form.is_valid():
            enfant = enfant_form.save(commit=False)
            enfant.parent = parent
            enfant.save()
            from django.urls import reverse
            return redirect(f"{reverse('parent_dashboard')}?enfant_id={enfant.id}")
        else:
            has_child_form_errors = True
    else:
        enfant_form = EnfantForm()



    enfants = parent.enfants.all()



    # 1. SÃ©lection de l'enfant actif (par URL, sinon le 1er par dÃ©faut)

    enfant_id = request.GET.get("enfant_id")

    active_enfant = enfants.filter(id=enfant_id).first() if enfant_id else enfants.first()



    # 2. Recommandations dynamiques basÃ©es sur l'enfant actif et le parent
    from django.db.models import Q, Case, When, Value, IntegerField
    recommandations = TeacherProfile.objects.filter(statut_de_validation=ValidationStatus.VALIDE).select_related('user')
    
    q_matieres = Q()
    if active_enfant and active_enfant.matieres:
        for mat in active_enfant.matieres:
            q_matieres |= Q(matiere_enseignee__icontains=mat)

    q_classe_expert = Q()
    q_classe_enseignee = Q()
    if active_enfant and active_enfant.classe:
        q_classe_expert = Q(classes_expertise__icontains=active_enfant.classe)
        q_classe_enseignee = Q(classes_enseignees__icontains=active_enfant.classe)

    q_quartier = Q()
    if parent.quartier_ville_id:
        # Utilisation de id__in pour Ã©viter les duplications dues au LEFT JOIN du ManyToMany
        prof_ids_in_quartier = TeacherProfile.quartiers_couverts.through.objects.filter(
            quartier_id=parent.quartier_ville_id
        ).values_list('teacherprofile_id', flat=True)
        q_quartier = Q(id__in=prof_ids_in_quartier)

    # Pour Ã©viter l'erreur "An empty Q() can't be used as a When() condition", on les remplace par une condition toujours fausse si elles sont vides.
    valid_q_matieres = q_matieres if q_matieres else Q(pk__isnull=True)
    valid_q_classe_expert = q_classe_expert if q_classe_expert else Q(pk__isnull=True)
    valid_q_classe_enseignee = q_classe_enseignee if q_classe_enseignee else Q(pk__isnull=True)
    valid_q_quartier = q_quartier if q_quartier else Q(pk__isnull=True)

    score_annotation = (
        Case(When(valid_q_matieres, then=Value(100)), default=Value(0), output_field=IntegerField()) +
        Case(When(valid_q_classe_expert, then=Value(15)), When(valid_q_classe_enseignee, then=Value(5)), default=Value(0), output_field=IntegerField()) +
        Case(When(valid_q_quartier, then=Value(2)), default=Value(0), output_field=IntegerField())
    )

    # Appliquer l'annotation et trier par score dÃ©croissant

    # puis badge suivi rigoureux comme critÃ¨re secondaire

    recommandations_annotees = recommandations.annotate(

        match_score=score_annotation

    ).filter(match_score__gt=0).order_by("-match_score", "-profil_complet", "-est_certifie", "?")[:8]

    

    # Appliquer les ratings avant la conversion en liste (car .annotate n'existe que sur QuerySet)

    recommandations_annotees = annotate_teachers_with_ratings(recommandations_annotees)

    recommandations_list = list(recommandations_annotees)

    

    # ComplÃ©ter avec d'autres profs si insuffisant

    if len(recommandations_list) < 8:

        fallback = recommandations.exclude(id__in=[r.id for r in recommandations_list]).order_by("?")[:8 - len(recommandations_list)]

        # Appliquer les ratings aussi sur le fallback

        fallback = annotate_teachers_with_ratings(fallback)

        recommandations_list.extend(list(fallback))

        

    recommandations = recommandations_list



    # 3. Engagements : On prend TOUS les engagements du parent pour Ãªtre sÃ»r de ne rien rater

    # (MÃªme si certains n'ont pas Ã©tÃ© correctement liÃ©s Ã  un enfant lors de la crÃ©ation)

    engagements_base_all = request.user.engagements_client.select_related(
        'professeur', 'professeur__user'
    ).prefetch_related(
        'enfants_concernes', 'conversation', 'professeur__parents_favoris'
    )
    
    engagements_base = engagements_base_all.filter(masque_par_parent=False)
    engagements_base_masques = engagements_base_all.filter(masque_par_parent=True)
    
    from django.db.models import Q
    engagements = engagements_base.filter(
        Q(enfants_concernes=active_enfant) | Q(enfants_concernes__isnull=True)
    ).distinct().order_by("-date_creation")
    
    engagements_masques_qs = engagements_base_masques.filter(
        Q(enfants_concernes=active_enfant) | Q(enfants_concernes__isnull=True)
    ).distinct().order_by("-date_creation")
    
    engagements_tous = list(engagements)
    for eng in engagements_tous:
        eng.check_and_update_essai_status()
        
    engagements_masques_list = list(engagements_masques_qs)
    for eng in engagements_masques_list:
        eng.check_and_update_essai_status()

    engs_essais_programmes = [e for e in engagements_tous if e.statut_general == StatutGeneral.ESSAI_PROGRAMME]
    engs_essais_confirmes = [e for e in engagements_tous if e.statut_general in [StatutGeneral.ESSAI_CONFIRME, StatutGeneral.ESSAI_REALISE]]
    engs_finalises = [e for e in engagements_tous if e.statut_general == StatutGeneral.FINALISE]
    engs_termines = [e for e in engagements_tous if e.statut_general == StatutGeneral.TERMINE]



    # 4. DonnÃ©es additionnelles

    favoris = request.user.professeurs_favoris.select_related('user').all()

    abonnement = getattr(parent, "abonnement", None)

    # Annotation des ratings + badge Suivi Rigoureux, puis tri : certifiÃ©s, badge, note

    favoris = annotate_teachers_with_ratings(favoris).order_by(

        '-est_certifie', '-suivi_rigoureux', '-profil_complet', '-moyenne_avis'

    )



    # Annonce (Parents/Apprenants)

    announcement = ProfessorAnnouncement.objects.filter(is_active=True, target_audience__in=['PARENT_APPRENANT', 'ALL']).order_by('-created_at').first()

    context = {

        "parent_details": parent,

        "enfants": enfants,

        "active_enfant": active_enfant,

        "recommandations": recommandations,

        "engagements_essais_programmes": engs_essais_programmes,

        "engagements_essais_confirmes": engs_essais_confirmes,

        "engagements_finalises": engs_finalises,

        "engagements_termines": engs_termines,
        "engagements_masques": engagements_masques_list,

        "engagements_tous": engagements_tous,

        "abonnement": abonnement,

        "favoris": favoris,

        "enfant_form": enfant_form,

        "has_child_form_errors": has_child_form_errors,

        "show_welcome_popup": not request.user.profile.a_vu_popup_bienvenue,

        "badge_essais_programmes": len(engs_essais_programmes),

        "badge_essais_confirmes": len(engs_essais_confirmes),

    }

    

    if announcement and not announcement.dismissed_by.filter(id=request.user.id).exists():

        context['announcement'] = announcement



    return render(request, "core/parent_dashboard.html", context)









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

            apprenant.telephone = request.user.profile.telephone

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



    return render(request, "core/apprenant_create_profile.html", {

        "form": form,

        "is_edit": apprenant_instance is not None

    })





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



    from .choices import ValidationStatus, StatutGeneral, EngagementType, ObjectifMotivation, CreneauDisponibilite, ClassLevel



    # 1. Recommandations dynamiques basÃ©es sur la classe, matiÃ¨res et localisation de l'apprenant
    from django.db.models import Q, Case, When, Value, IntegerField
    base_recommandations = TeacherProfile.objects.filter(statut_de_validation=ValidationStatus.VALIDE).select_related('user')
    
    q_matieres = Q()
    if apprenant.matieres_recherchees:
        for mat in apprenant.matieres_recherchees:
            q_matieres |= Q(matiere_enseignee__icontains=mat)

    q_classe_expert = Q()
    q_classe_enseignee = Q()
    if apprenant.classe:
        q_classe_expert = Q(classes_expertise__icontains=apprenant.classe)
        q_classe_enseignee = Q(classes_enseignees__icontains=apprenant.classe)

    q_quartier = Q()
    if apprenant.quartier_ville_id:
        # Utilisation de id__in pour Ã©viter les duplications dues au LEFT JOIN du ManyToMany
        prof_ids_in_quartier = TeacherProfile.quartiers_couverts.through.objects.filter(
            quartier_id=apprenant.quartier_ville_id
        ).values_list('teacherprofile_id', flat=True)
        q_quartier = Q(id__in=prof_ids_in_quartier)

    score_annotation = (
        Case(When(q_matieres, then=Value(3)), default=Value(0), output_field=IntegerField()) +
        Case(When(q_classe_expert, then=Value(5)), When(q_classe_enseignee, then=Value(2)), default=Value(0), output_field=IntegerField()) +
        Case(When(q_quartier, then=Value(1)), default=Value(0), output_field=IntegerField())
    )

    # Appliquer le score et limiter aux 8 meilleurs rÃ©sultats

    recommandations_annotees = base_recommandations.annotate(

        reco_score=score_annotation

    ).filter(reco_score__gt=0).order_by("-reco_score", "-profil_complet", "-est_certifie", "?")[:8]

    

    # Appliquer les ratings avant la conversion en liste (car .annotate n'existe que sur QuerySet)

    recommandations_annotees = annotate_teachers_with_ratings(recommandations_annotees)

    recommandations_list = list(recommandations_annotees)

    

    # ComplÃ©ter avec d'autres profs si insuffisant

    if len(recommandations_list) < 8:

        fallback = base_recommandations.exclude(

            id__in=[r.id for r in recommandations_list]

        ).order_by("?")[:8 - len(recommandations_list)]

        # Appliquer les ratings aussi sur le fallback

        fallback = annotate_teachers_with_ratings(fallback)

        recommandations_list.extend(list(fallback))

        

    recommandations = recommandations_list



    # 2. Engagements filtrÃ©s pour l'apprenant (parent_apprenant=request.user)

    engagements = request.user.engagements_client.select_related(

        'professeur', 'professeur__user'

    ).prefetch_related(

        'enfants_concernes', 'conversation', 'professeur__parents_favoris'

    ).order_by("-date_creation")

    engagements_tous = list(engagements)

    for eng in engagements_tous:

        eng.check_and_update_essai_status()



    engs_essais_programmes = [e for e in engagements_tous if e.statut_general == StatutGeneral.ESSAI_PROGRAMME]

    engs_essais_confirmes = [e for e in engagements_tous if e.statut_general in [StatutGeneral.ESSAI_CONFIRME, StatutGeneral.ESSAI_REALISE]]

    engs_finalises = [e for e in engagements_tous if e.statut_general == StatutGeneral.FINALISE]

    engs_termines = [e for e in engagements_tous if e.statut_general == StatutGeneral.TERMINE]



    # 3. Abonnement & Favoris

    abonnement = request.user.abonnements.first()

    favoris = TeacherProfile.objects.select_related('user').filter(parents_favoris=request.user)



    # Annotation des ratings + badge Suivi Rigoureux, puis tri : certifiÃ©s, badge, note

    favoris = annotate_teachers_with_ratings(favoris).order_by(

        '-est_certifie', '-suivi_rigoureux', '-profil_complet', '-moyenne_avis'

    )



    context = {

        "apprenant": apprenant,

        "recommandations": recommandations,

        "engagements_essais_programmes": engs_essais_programmes,

        "engagements_essais_confirmes": engs_essais_confirmes,

        "engagements_finalises": engs_finalises,

        "engagements_termines": engs_termines,
        "engagements_masques": engagements_masques_list,

        "engagements_tous": engagements_tous,

        "abonnement": abonnement,

        "favoris": favoris,

        "show_welcome_popup": not request.user.profile.a_vu_popup_bienvenue,

        "badge_essais_programmes": len(engs_essais_programmes),

        "badge_essais_confirmes": len(engs_essais_confirmes),

    }



    # Annonce (Parents/Apprenants)

    announcement = ProfessorAnnouncement.objects.filter(is_active=True, target_audience__in=['PARENT_APPRENANT', 'ALL']).order_by('-created_at').first()

    if announcement and not announcement.dismissed_by.filter(id=request.user.id).exists():

        context['announcement'] = announcement



    return render(request, "core/apprenant_dashboard.html", context)





@login_required

def gestion_plan(request):

    from .models import Profile

    

    # SÃ©curitÃ© RÃ´le

    try:

        user_profile = request.user.profile

        # IncrÃ©menter les vues pour les statistiques de lancement (sauf comptes de test)

        if request.user.email not in getattr(settings, 'TEST_ACCOUNT_EMAILS', []):

            user_profile.nb_vues_page_plan += 1

            user_profile.save(update_fields=['nb_vues_page_plan'])

    except Profile.DoesNotExist:

        return redirect("finalisation_compte")



    context = {}

    return render(request, "core/gestion_plan.html", context)





@login_required

@require_http_methods(["POST"])

def downgrade_to_standard(request):

    from django.utils import timezone

    from .models import Abonnement, TypeAbonnement

    

    # CrÃ©er un abonnement standard Ã  partir d'aujourd'hui

    Abonnement.objects.create(

        user=request.user,

        type_abonnement=TypeAbonnement.STANDARD,

        date_debut=timezone.now().date()

    )

    # L'historique des engagements payants ou non sera gÃ©rÃ© par la logique existante 

    # de verrouillage (is_blocked) qui s'appuie sur le plan en cours.

    return redirect('gestion_plan')







# Vues pour le systÃ¨me de recherche et profils hybride

def track_teacher_view(request, teacher_profile):

    from django.utils import timezone

    from datetime import timedelta

    from .models import VueProfil, Profile

    

    # Nettoyage paresseux des anciennes vues (vieux de plus de 60 jours)

    limit_date = timezone.now() - timedelta(days=60)

    VueProfil.objects.filter(professeur_vise=teacher_profile, date_consultation__lt=limit_date).delete()



    if not request.user.is_authenticated:

        session_key = f'viewed_prof_{teacher_profile.id}_{timezone.now().date()}'

        if not request.session.get(session_key):

            request.session[session_key] = True

            return True

        return False

        

    try:

        # Ne pas compter si le visiteur est un prof

        if request.user.profile.role == Profile.ROLE_PROF:

            return False

    except Profile.DoesNotExist:

        pass

        

    # Ne pas compter si c'est le professeur lui-mÃªme

    if request.user.id == teacher_profile.user.id:

        return False

        

    # Ne pas compter pour les comptes de test

    if getattr(settings, 'TEST_ACCOUNT_EMAILS', []) and request.user.email in settings.TEST_ACCOUNT_EMAILS:

        return False

        

    start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    

    vue_exists = VueProfil.objects.filter(

        professeur_vise=teacher_profile,

        visiteur_utilisateur=request.user,

        date_consultation__gte=start_of_day

    ).exists()

    

    is_new_view = False

    if not vue_exists:

        VueProfil.objects.create(

            professeur_vise=teacher_profile,

            visiteur_utilisateur=request.user

        )

        is_new_view = True

        # Recalcul de nb_vues_total basÃ© sur les vues conservÃ©es (max 60 jours)

        teacher_profile.nb_vues_total = VueProfil.objects.filter(professeur_vise=teacher_profile).count()

        

        # Calcul des vues du mois (pour info, depuis le dÃ©but du mois)

        first_day_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        teacher_profile.nb_vues_mois = VueProfil.objects.filter(

            professeur_vise=teacher_profile, 

            date_consultation__gte=first_day_of_month

        ).count()

        

        teacher_profile.save(update_fields=['nb_vues_total', 'nb_vues_mois'])

        

    return is_new_view



def seo_directory_page(request, subject_slug, city_slug):

    """Page de rÃ©pertoire dynamique (SEO Programmatique)

    

    Optimisations appliquÃ©es :

    - select_related('user') pour la FK directe

    - prefetch_related('parents_favoris') pour le M2M utilisÃ© dans _teacher_card.html

    - annotate_teachers_with_ratings() pour avis/badges en une seule requÃªte SQL

    - Paginator Django natif (12 profs/page) pour limiter le DOM

    - AgrÃ©gation Avg sur le queryset filtrÃ©, pas sur la page paginÃ©e

    """

    from django.utils.text import slugify

    from django.db.models import Avg

    from django.http import Http404

    from django.core.paginator import Paginator

    from .choices import Matiere, Localisation, ValidationStatus, ClassLevel

    import random

    

    # â”€â”€ 1. Reverse mapping (slug â†’ nom rÃ©el) â”€â”€

    subject_name = None

    city_name = None

    

    for mat in Matiere.LISTE:

        if slugify(mat) == subject_slug:

            subject_name = mat

            break

            

    from .models import Quartier
    villes = Quartier.objects.exclude(ville='').values_list('ville', flat=True).distinct()
    for v in villes:
        if slugify(v) == city_slug:
            city_name = v
            break

    if not city_name:
        raise Http404("Ville non reconnue")
    if not subject_name:
        raise Http404("MatiÃ¨re non reconnue")

    # â”€â”€ 2. Queryset optimisÃ© (Anti N+1) â”€â”€
    queryset = (
        TeacherProfile.objects
        .select_related('user')                 # FK directe â†’ 1 JOIN
        .prefetch_related('parents_favoris')     # M2M favoris â†’ 1 requÃªte sÃ©parÃ©e
        .filter(statut_de_validation=ValidationStatus.VALIDE)
        .filter(quartiers_couverts__ville__iexact=city_name)
        .filter(matiere_enseignee__icontains=subject_name)
        .distinct()
    )

    

    # â”€â”€ 2.5 Filtrage Additionnel sur place â”€â”€

    classe_filter = request.GET.get('classe', '').strip()

    prix_filter = request.GET.get('prix', '').strip()



    if classe_filter:

        from django.db.models import Q, Case, When, Value, BooleanField

        queryset = queryset.filter(

            Q(classes_expertise__icontains=classe_filter) | Q(classes_enseignees__icontains=classe_filter)

        ).annotate(

            is_expert_classe=Case(

                When(classes_expertise__icontains=classe_filter, then=Value(True)),

                default=Value(False),

                output_field=BooleanField()

            )

        )

        

    if prix_filter:

        from django.conf import settings

        thresholds = [int(t) for t in settings.PRICE_THRESHOLDS]

        if prix_filter == f"0-{thresholds[0]}":

            queryset = queryset.filter(tarif_horaire__lt=thresholds[0])

        elif prix_filter == f"{thresholds[0]}-{thresholds[1]}":

            queryset = queryset.filter(tarif_horaire__gte=thresholds[0], tarif_horaire__lte=thresholds[1])

        elif prix_filter == f"{thresholds[1]}-{thresholds[2]}":

            queryset = queryset.filter(tarif_horaire__gte=thresholds[1], tarif_horaire__lte=thresholds[2])

        elif prix_filter == f"{thresholds[2]}+":

            queryset = queryset.filter(tarif_horaire__gt=thresholds[2])



    teachers_qs = queryset

    

    fallback_active = False

    if not teachers_qs.exists() and not classe_filter and not prix_filter:

        teachers_qs = TeacherProfile.objects.select_related('user').filter(
            statut_de_validation=ValidationStatus.VALIDE, quartiers_couverts__ville__iexact=city_name
        ).distinct()

        fallback_active = True

    

    # Annotations (avis, badges) â€” une seule passe SQL

    teachers_qs = annotate_teachers_with_ratings(teachers_qs)

    

    # Tri : certifiÃ© d'abord, puis meilleure note, puis rÃ©cent

    teachers_qs = teachers_qs.order_by('-est_certifie', '-moyenne_avis', '-id')

    

    # Comptage et tarif moyen sur le queryset COMPLET (avant pagination)

    teacher_count = teachers_qs.count()

    avg_price_aggr = teachers_qs.aggregate(Avg('tarif_horaire'))

    average_price = avg_price_aggr['tarif_horaire__avg']

    average_price = int(average_price) if average_price else 2500

    

    # â”€â”€ 3. Pagination (12 cartes/page pour mobile lÃ©ger) â”€â”€

    paginator = Paginator(teachers_qs, 12)

    page_number = request.GET.get('page', 1)

    teachers_page = paginator.get_page(page_number)

    

    available_classes = ClassLevel.get_choices()

    

    # â”€â”€ 4. FAQ dynamique â”€â”€

    faq_items = [

        {

            "question": f"Comment fonctionne la sÃ©lection des professeurs de {subject_name} Ã  {city_name} ?",

            "answer": f"Chaque profil indÃ©pendant inscrit sur Prof Chez Vous passe un processus de validation strict. Un enseignant ne peut proposer ses services dans une discipline que s'il a fourni des preuves concrÃ¨tes et vÃ©rifiÃ©es de ses compÃ©tences pour cette matiÃ¨re spÃ©cifique."

        },

        {

            "question": f"Quel est le tarif d'un accompagnement personnalisÃ© sur cette page ?",

            "answer": f"Le tarif moyen constatÃ© pour les cours de {subject_name} dans la zone de {city_name} s'Ã©lÃ¨ve Ã  {average_price} FCFA par heure. Les enseignants fixent leurs tarifs de maniÃ¨re indÃ©pendante, notamment en fonction de la classe de l'apprenant (de la 6Ã¨me Ã  la Terminale)."

        },

        {

            "question": f"Comment s'assurer du suivi des cours ?",

            "answer": "La plateforme met Ã  disposition des outils pour tracer l'Ã©volution pÃ©dagogique. L'enseignant Ã©tablit un score de maÃ®trise initial lors du premier contact et consigne un journal de session aprÃ¨s chaque intervention pour documenter le travail effectuÃ©."

        }

    ]

    

    # â”€â”€ 5. Maillage interne â”€â”€

    all_cities = [v for v in villes if slugify(v) != city_slug]

    random.shuffle(all_cities)

    neighboring_cities = [{"name": c, "slug": slugify(c)} for c in all_cities[:4]]

    

    all_subj = [m for m in Matiere.LISTE if slugify(m) != subject_slug]

    random.shuffle(all_subj)

    other_subjects = [{"name": s, "slug": slugify(s)} for s in all_subj[:4]]



    context = {

        "subject": {"name": subject_name, "slug": subject_slug},

        "city": {"name": city_name, "slug": city_slug},

        "teacher_count": teacher_count,

        "average_price": average_price,

        "teachers_list": teachers_page,       # Page paginÃ©e, pas le queryset brut

        "available_classes": available_classes,

        "faq_items": faq_items,

        "neighboring_cities": neighboring_cities,

        "other_subjects": other_subjects,

        "fallback_active": fallback_active,

        "current_classe": classe_filter,

        "current_prix": prix_filter,

    }

    

    return render(request, "core/seo_directory.html", context)



def professeur_detail(request, teacher_slug):

    """Page profil professeur dynamique pour SEO avec robustesse accrue"""

    from .choices import CourseMode, ClassLevel

    teacher = get_object_or_404(TeacherProfile.objects.select_related('user').prefetch_related('evaluations_recues', 'diplomes'), slug=teacher_slug)

    

    is_new_view = track_teacher_view(request, teacher)

    

    if is_new_view:

        # Statistiques de lancement

        teacher.nb_vues_profil += 1

        teacher.save(update_fields=['nb_vues_profil'])

        

        if request.user.is_authenticated and request.user.email not in getattr(settings, 'TEST_ACCOUNT_EMAILS', []):

            if hasattr(request.user, 'parent_profile'):

                request.user.parent_profile.nb_profils_consultes += 1

                request.user.parent_profile.save(update_fields=['nb_profils_consultes'])

            elif hasattr(request.user, 'apprenant'):

                request.user.apprenant.nb_profils_consultes += 1

                request.user.apprenant.save(update_fields=['nb_profils_consultes'])

    

    # Calcul des stats sÃ©curisÃ©

    from django.db.models import Avg, Count

    from .choices import EngagementType

    engs_stats = teacher.engagements.filter(type_engagement=EngagementType.ESSAI).exclude(temps_reponse_prof__isnull=True)

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



    # Badge "Suivi Rigoureux" "â€ calculÃ© sur l'instance unique (mÃªme rÃ¨gle que l'annotation SQL)

    from django.utils import timezone as tz

    _date_limite = tz.now() - tz.timedelta(days=settings.SUIVI_RIGOUREUX_JOURS_RECENCE)

    _nb_bilans = teacher.engagements.filter(

        seances__objectifs__gt=''

    ).aggregate(total=Count('seances', distinct=True))['total'] or 0

    _nb_actifs = teacher.engagements.filter(statut_general=StatutGeneral.FINALISE).count()



    if _nb_bilans < settings.SUIVI_RIGOUREUX_SEUIL_BILANS:

        # Seuil non atteint Ã¢â€ â€™ pas de badge

        teacher.suivi_rigoureux = False

    elif _nb_actifs == 0:

        # Bon passif, pas d'engagement actif Ã¢â€ â€™ badge conservÃ©

        teacher.suivi_rigoureux = True

    else:

        # Engagement actif : vÃ©rifier la rÃ©cence du dernier bilan

        from django.db.models import Max as _Max

        _last_bilan = teacher.engagements.filter(

            seances__objectifs__gt=''

        ).aggregate(last=_Max('seances__creee_le'))['last']

        teacher.suivi_rigoureux = (_last_bilan is not None and _last_bilan >= _date_limite)

    

    # Auth context

    is_parent = False

    is_premium = False

    can_schedule_trial = True

    parent_children = []

    parent_children_json = "[]"

    existing_engagement = None

    existing_engagement_json = "null"

    existing_conversation_id = None

    

    if request.user.is_authenticated:

        # is_premium est vrai si l'utilisateur a un abonnement actif ACCESS_PREMIUM

        if hasattr(request.user, 'profile') and request.user.profile.current_plan == TypeAbonnement.ACCESS_PREMIUM:

            is_premium = True

        elif hasattr(request.user, 'profile'):

            essais_utilises = request.user.engagements_client.filter(

                type_engagement=EngagementType.ESSAI

            ).count()

            if essais_utilises >= 1:

                can_schedule_trial = False



        # VÃ©rifier conversation existante

        from .models import Conversation

        conv = Conversation.objects.filter(participants=request.user).filter(participants=teacher.user).first()

        if conv:

            existing_conversation_id = conv.id



        if hasattr(request.user, 'profile') and request.user.profile.role == Profile.ROLE_PARENT:

            is_parent = True

            if hasattr(request.user, 'parent'):

                parent_children = list(request.user.parent.enfants.all().values('id', 'prenom'))

                parent_children_json = json.dumps(parent_children)

                

        # VÃ©rifier engagement existant (prioritÃ© Ã  l'attente pour modification)

        existing_engagement_obj = teacher.engagements.filter(

            parent_apprenant=request.user,

            statut_general__in=[StatutGeneral.EN_ATTENTE, StatutGeneral.ESSAI_PROGRAMME]

        ).first()

        

        if not existing_engagement_obj:

            # Sinon vÃ©rifier s'il y a un engagement actif

            existing_engagement_obj = teacher.engagements.filter(

                parent_apprenant=request.user,

                statut_general__in=[StatutGeneral.CONFIRME, StatutGeneral.EN_COURS, StatutGeneral.ESSAI_CONFIRME, StatutGeneral.ESSAI_REALISE]

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

                'type': 'essai' if existing_engagement_obj.type_engagement == EngagementType.ESSAI else 'standard',

                'enfant_id': existing_engagement_obj.enfants_concernes.first().id if hasattr(existing_engagement_obj, 'enfants_concernes') and existing_engagement_obj.enfants_concernes.exists() else (existing_engagement_obj.enfants_concernes.id if hasattr(existing_engagement_obj.enfants_concernes, 'id') else None),

                'classe': existing_engagement_obj.classe,

                'localisation': existing_engagement_obj.localisation_option,

                'date_debut': existing_engagement_obj.date_debut.strftime('%Y-%m-%d') if existing_engagement_obj.date_debut else None,

                'budget': str(existing_engagement_obj.budget_convenu) if existing_engagement_obj.budget_convenu else None,

                'duree_mois': existing_engagement_obj.duree_mois,

                'date_essai': timezone.localtime(existing_engagement_obj.date_heure_essai).strftime('%Y-%m-%dT%H:%M') if existing_engagement_obj.date_heure_essai else None,

                'description_essai': existing_engagement_obj.description_essai,

                'indications_geographiques': existing_engagement_obj.indications_geographiques,

            })



    # Conversion des codes en noms lisibles

    mode_map = dict(CourseMode.CHOICES)

    class_map = dict(ClassLevel.CHOICES)

    readable_expertise = [class_map.get(c, c) for c in getattr(teacher, 'classes_expertise', [])]

    readable_classes = [class_map.get(c, c) for c in getattr(teacher, 'classes_enseignees', [])]

    readable_modes = [mode_map.get(m, m) for m in getattr(teacher, 'modes_de_cours', [])]

        

    # --- Open Graph : calcul serveur de l'URL image pour Facebook/WhatsApp/LinkedIn ---
    # On utilise le SDK Cloudinary pour gÃ©nÃ©rer l'URL avec transformations,
    # ce qui est plus fiable que la manipulation regex cÃ´tÃ© template.
    og_image_width = 1200
    og_image_height = 630
    og_image_url = None

    if teacher.photo_de_profil:
        try:
            raw_url = teacher.photo_de_profil.url
            if raw_url and 'res.cloudinary.com' in str(raw_url):
                try:
                    import cloudinary.utils
                    import re
                    import os
                    
                    # Extraire le public_id directement de l'URL existante ou du nom
                    raw_str = str(raw_url)
                    parts = raw_str.split('/upload/')
                    if len(parts) == 2:
                        path = parts[1]
                        path = re.sub(r'^v\d+/', '', path)
                        public_id = os.path.splitext(path)[0]
                    else:
                        public_id = os.path.splitext(teacher.photo_de_profil.name)[0]
                        if not public_id.startswith('media/'):
                            public_id = f"media/{public_id}"
                    
                    # CORRECTIF MAJEUR : Si la base de donnÃ©es a perdu le dossier parent, on le force
                    # (Cloudinary stocke bien dans teachers/profile_photos/ mais la DB renvoie parfois media/IMG_...)
                    if 'teachers/profile_photos/' not in public_id:
                        public_id = public_id.replace('media/', 'media/teachers/profile_photos/')
                    
                    og_image_url, _ = cloudinary.utils.cloudinary_url(
                        public_id,
                        width=og_image_width,
                        height=og_image_height,
                        crop="fill",
                        gravity="face",
                        format="jpg",
                        quality="auto",
                        secure=True
                    )
                except Exception:
                    # Fallback : utiliser l'URL brute avec injection de transformation
                    from core.templatetags.image_utils import cloudinary_og
                    og_image_url = cloudinary_og(raw_url)
            elif raw_url:
                # Image locale (pas Cloudinary)
                og_image_url = request.build_absolute_uri(raw_url)
                og_image_width = 800
                og_image_height = 1000
        except Exception:
            og_image_url = None

    if not og_image_url:
        from django.templatetags.static import static
        og_image_url = request.build_absolute_uri(static('core/images/logo_pr.jpg'))
        og_image_width = 500
        og_image_height = 500

    context = {

        'teacher': teacher,

        'teacher_slug': teacher_slug,

        'user': request.user,

        'temps_moyen_reponse': temps_moyen_reponse,

        'engagements_actifs': engagements_actifs,

        'is_parent': is_parent,

        'is_premium': is_premium,

        'can_schedule_trial': can_schedule_trial,

        'readable_modes': readable_modes,

        'readable_expertise': readable_expertise,

        'readable_classes': readable_classes,

        'parent_children': parent_children,

        'parent_children_json': parent_children_json,

        'existing_engagement': existing_engagement,

        'existing_engagement_json': existing_engagement_json,

        'existing_conversation_id': existing_conversation_id,

        'days_list': ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],

        'og_image_url': og_image_url,

        'og_image_width': og_image_width,

        'og_image_height': og_image_height,

    }



    # --- SEO: Professeurs Similaires ---

    related_teachers = TeacherProfile.objects.filter(

        statut_de_validation=ValidationStatus.VALIDE

    ).exclude(id=teacher.id)



    # PrioritÃ© 1: MÃªme matiÃ¨re (plus flexible avec icontains)

    same_matiere = related_teachers.filter(matiere_enseignee__icontains=teacher.matiere_enseignee)

    if same_matiere.count() >= 4:

        related_teachers = same_matiere.order_by('?')[:4]

    else:

        # PrioritÃ© 2: MÃªme ville/quartier

        same_loc = related_teachers.filter(quartiers_couverts__in=teacher.quartiers_couverts.all())

        related_teachers = (same_matiere | same_loc).distinct().order_by('?')[:4]



    context['related_teachers'] = annotate_teachers_with_ratings(related_teachers)

    

    return render(request, "core/professeur_detail.html", context)





@require_http_methods(["GET"])

def api_teacher_profile(request, teacher_slug):

    """API pour rÃ©cupÃ©rer les donnÃ©es du professeur (pour le side panel) avec gestion d'erreur robuste"""

    try:

        from .choices import CourseMode, ClassLevel

        teacher = TeacherProfile.objects.select_related('user').prefetch_related(
            'videos',
            'quartiers_couverts',
            'diplomes',
            'engagements'
        ).get(slug=teacher_slug)

        is_new_view = track_teacher_view(request, teacher)
        if is_new_view:
            teacher.nb_vues_profil += 1
            teacher.save(update_fields=['nb_vues_profil'])

        # Calcul des stats sÃ©curisÃ©
        from django.db.models import Avg, Count

        engs_stats = teacher.engagements.exclude(temps_reponse_prof__isnull=True)
        temps_moyen_reponse = engs_stats.aggregate(avg=Avg('temps_reponse_prof'))['avg'] if engs_stats.exists() else None

        engagements_actifs = teacher.engagements.filter(
            statut_general__in=[StatutGeneral.EN_COURS, StatutGeneral.CONFIRME, StatutGeneral.FINALISE]
        ).count()

        # Professeurs similaires pour le Side Panel (optimisÃ© sans order_by('?'))
        related_teachers = TeacherProfile.objects.filter(
            statut_de_validation=ValidationStatus.VALIDE
        ).exclude(id=teacher.id).select_related('user').prefetch_related('quartiers_couverts')

        same_matiere = related_teachers.filter(matiere_enseignee__icontains=teacher.matiere_enseignee)
        if same_matiere.count() >= 4:
            related_teachers = same_matiere.order_by('-id')[:4]
        else:
            same_loc = related_teachers.filter(quartiers_couverts__in=teacher.quartiers_couverts.all())
            related_teachers = (same_matiere | same_loc).distinct().order_by('-id')[:4]

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

        

        # Contexte d'authentification sÃ©curisÃ©

        is_parent = False

        is_premium = False

        can_schedule_trial = True

        parent_children = []

        existing_engagement = None

        existing_conversation_id = None

        existing_engagement_obj = None

        existing_engagement_dict = None

        

        if request.user.is_authenticated:

            # VÃ©rifier conversation existante

            from .models import Conversation

            conv = Conversation.objects.filter(participants=request.user).filter(participants=teacher.user).first()

            if conv:

                existing_conversation_id = conv.id

                

            try:

                # is_premium est vrai si l'utilisateur a un abonnement actif ACCESS_PREMIUM

                if hasattr(request.user, 'profile') and request.user.profile.current_plan == TypeAbonnement.ACCESS_PREMIUM:

                    is_premium = True

                elif hasattr(request.user, 'profile'):

                    essais_utilises = request.user.engagements_client.filter(

                        type_engagement=EngagementType.ESSAI

                    ).count()

                    if essais_utilises >= 1:

                        can_schedule_trial = False



                if hasattr(request.user, 'profile') and request.user.profile.role == Profile.ROLE_PARENT:

                    is_parent = True

                    if hasattr(request.user, 'parent'):

                        parent_children = list(request.user.parent.enfants.all().values('id', 'prenom'))

                

                # VÃ©rifier engagement existant (prioritÃ© Ã  l'attente pour modification)

                existing_engagement_obj = teacher.engagements.filter(

                    parent_apprenant=request.user,

                    statut_general__in=[StatutGeneral.EN_ATTENTE, StatutGeneral.ESSAI_PROGRAMME]

                ).first()

                

                if not existing_engagement_obj:

                    # Sinon vÃ©rifier s'il y a un engagement actif

                    existing_engagement_obj = teacher.engagements.filter(

                        parent_apprenant=request.user,

                        statut_general__in=[StatutGeneral.CONFIRME, StatutGeneral.EN_COURS, StatutGeneral.ESSAI_CONFIRME, StatutGeneral.ESSAI_REALISE]

                    ).first()



                existing_engagement_dict = None

                if existing_engagement_obj:

                    existing_engagement_dict = {

                        'id': existing_engagement_obj.id,

                        'matiere': existing_engagement_obj.matiere,

                        'mode_de_cours': existing_engagement_obj.mode_de_cours,

                        'frequence': existing_engagement_obj.frequence_hebdomadaire,

                        'duree': existing_engagement_obj.duree_seance,

                        'status': existing_engagement_obj.statut_general,

                        'type': 'essai' if existing_engagement_obj.type_engagement == EngagementType.ESSAI else 'standard',

                        'enfant_id': existing_engagement_obj.enfants_concernes.first().id if hasattr(existing_engagement_obj, 'enfants_concernes') and hasattr(existing_engagement_obj.enfants_concernes, 'exists') and existing_engagement_obj.enfants_concernes.exists() else (existing_engagement_obj.enfants_concernes.id if hasattr(existing_engagement_obj, 'enfants_concernes') and hasattr(existing_engagement_obj.enfants_concernes, 'id') else None),

                        'classe': existing_engagement_obj.classe,

                        'localisation': existing_engagement_obj.localisation_option,

                        'date_debut': existing_engagement_obj.date_debut.strftime('%Y-%m-%d') if existing_engagement_obj.date_debut else None,

                        'budget': str(existing_engagement_obj.budget_convenu) if existing_engagement_obj.budget_convenu else None,

                        'duree_mois': existing_engagement_obj.duree_mois,

                        'date_essai': timezone.localtime(existing_engagement_obj.date_heure_essai).strftime('%Y-%m-%dT%H:%M') if existing_engagement_obj.date_heure_essai else None,

                        'description_essai': existing_engagement_obj.description_essai,

                        'indications_geographiques': existing_engagement_obj.indications_geographiques,

                    }

            except Exception:

                pass

        

        # Conversion des codes en noms lisibles

        mode_map = dict(CourseMode.CHOICES)

        class_map = dict(ClassLevel.CHOICES)

        readable_expertise = [class_map.get(c, c) for c in getattr(teacher, 'classes_expertise', [])]

        readable_classes = [class_map.get(c, c) for c in getattr(teacher, 'classes_enseignees', [])]

        readable_modes = [mode_map.get(m, m) for m in getattr(teacher, 'modes_de_cours', [])]

            

        html = render_to_string('core/components/teacher_profile.html', {

            'teacher': teacher,

            'user': request.user,

            'is_side_panel': True,

            'temps_moyen_reponse': temps_moyen_reponse,

            'engagements_actifs': engagements_actifs,

            'is_parent': is_parent,

            'is_premium': is_premium,

            'can_schedule_trial': can_schedule_trial,

            'existing_conversation_id': existing_conversation_id,

            'readable_modes': readable_modes,

            'readable_expertise': readable_expertise,

            'readable_classes': readable_classes,

            'related_teachers': related_teachers,

            'days_list': ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],

            'parent_children': parent_children,

            'existing_engagement': existing_engagement_obj

        }, request=request)

        

        return JsonResponse({

            'html': html,

            'parent_children': parent_children,

            'existing_engagement': existing_engagement_dict,

            'existing_conversation_id': existing_conversation_id,

        })

        

    except TeacherProfile.DoesNotExist:

        return JsonResponse({'error': 'Professeur non trouvÃ©'}, status=404)

    except Exception as e:

        import traceback

        print(traceback.format_exc()) # Log l'erreur complÃ¨te sur Render

        return JsonResponse({'error': f"Erreur interne: {str(e)}"}, status=500)





@csrf_exempt

@require_http_methods(["POST"])

def api_engagement(request):

    """API pour crÃ©er une proposition d'engagement (Standard ou Essai)"""

    if not request.user.is_authenticated:

        return JsonResponse({'error': 'Utilisateur non authentifiÃ©'}, status=401)

    

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

        

        # CrÃ©er la conversation si besoin

        # Pour faire simple on associe juste l'engagement

        

        engagement_type_str = data.get('engagement_type', 'standard')

        type_eng = EngagementType.ESSAI if engagement_type_str == 'essai' else EngagementType.NORMAL

        if type_eng == EngagementType.ESSAI:
            essais_utilises = request.user.engagements_client.filter(
                type_engagement=EngagementType.ESSAI
            ).count()
            if essais_utilises >= 1:
                return JsonResponse({'error': 'Vous avez dÃ©jÃ  utilisÃ© votre essai gratuit.'}, status=400)

        # Recherche d'un engagement existant non terminÃ©

        existing = Engagement.objects.filter(

            professeur=teacher,

            parent_apprenant=request.user

        ).exclude(statut_general__in=[StatutGeneral.TERMINE, StatutGeneral.ANNULE, StatutGeneral.REFUSE, StatutGeneral.FINALISE, StatutGeneral.ENGAGEMENT_FINALISE]).first()



        engagement = None

        if existing:

            if existing.type_engagement == EngagementType.ESSAI and type_eng == EngagementType.NORMAL:

                from django.utils import timezone

                dt_fin = existing.date_heure_fin_essai or existing.date_heure_essai

                if dt_fin and dt_fin > timezone.now():

                    return JsonResponse({'error': "Vous avez un cours d'essai programmÃ© avec ce professeur. Vous pourrez basculer sur un engagement standard une fois la sÃ©ance complÃ©tÃ©e (date et heure passÃ©es) ou en annulant l'essai en cours."}, status=400)

                

                if existing.statut_general in [StatutGeneral.EN_ATTENTE, StatutGeneral.ESSAI_PROGRAMME]:

                    engagement = existing

                else:

                    # Allow creating a new standard engagement without raising error

                    pass

            elif existing.statut_general in [StatutGeneral.EN_ATTENTE, StatutGeneral.ESSAI_PROGRAMME]:

                engagement = existing

            else:

                return JsonResponse({'error': 'Vous avez dÃ©jÃ  un engagement actif ou confirmÃ© avec ce professeur.'}, status=400)



        is_new_engagement = False

        if not engagement:

            engagement = Engagement(

                professeur=teacher,

                parent_apprenant=request.user,

                statut_general=StatutGeneral.ESSAI_PROGRAMME

            )

            is_new_engagement = True

            

        engagement.type_engagement = type_eng

        raw_matiere = data.get('matiere', [])
        if isinstance(raw_matiere, str):
            raw_matiere = [raw_matiere] if raw_matiere else []
        engagement.matiere = ', '.join(raw_matiere)

        engagement.classe = data.get('classe', '')

        engagement.mode_de_cours = data.get('course_mode', '')

        loc_val = str(data.get('localisation', '')).strip()
        q_obj = None
        if loc_val.isdigit():
            from .models import Quartier
            q_obj = Quartier.objects.filter(id=int(loc_val)).first()
            if q_obj:
                loc_val = f"{q_obj.nom} ({q_obj.ville})" if q_obj.ville else q_obj.nom
        engagement.localisation_option = loc_val

        # SÃ©curitÃ© : indications gÃ©ographiques uniquement pour les essais (anti-contournement)

        engagement.indications_geographiques = data.get('indications_geographiques', '') if type_eng == EngagementType.ESSAI else ''

        engagement.plateforme_visio_preferee = data.get('plateforme_visio', '')

        

        if type_eng == EngagementType.ESSAI:

            from django.utils.dateparse import parse_datetime

            from django.utils.timezone import make_aware, is_naive

            

            date_essai_str = data.get('date_essai')

            if date_essai_str:

                dt = parse_datetime(date_essai_str)

                if dt and is_naive(dt): dt = make_aware(dt)

                engagement.date_heure_essai = dt

            

            date_fin_essai_str = data.get('date_fin_essai')

            if date_fin_essai_str:

                dt_fin = parse_datetime(date_fin_essai_str)

                if dt_fin and is_naive(dt_fin): dt_fin = make_aware(dt_fin)

                engagement.date_heure_fin_essai = dt_fin

                

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
        nouveau_prenom_enfant = data.get('nouveau_prenom_enfant')
        
        from .models import Enfant
        enfant = None

        if enfant_id and str(enfant_id).isdigit():

            try:

                enfant = Enfant.objects.get(id=int(enfant_id))

                # VÃ©rifier que l'enfant appartient bien au parent (sÃ©curitÃ©)

                if hasattr(request.user, 'parent') and enfant.parent != request.user.parent:
                    enfant = None

            except (Enfant.DoesNotExist, ValueError):

                pass

        if not enfant and nouveau_prenom_enfant and hasattr(request.user, 'parent'):
            prenom = nouveau_prenom_enfant.strip()
            if prenom:
                enfant = Enfant.objects.create(
                    parent=request.user.parent,
                    prenom=prenom,
                    classe=data.get('classe', ''),
                    matieres=raw_matiere,
                    mode_de_cours=data.get('course_mode', ''),
                    quartier_ville=q_obj
                )

        if enfant:
            engagement.enfants_concernes.clear()
            engagement.enfants_concernes.add(enfant)

        # Fallback : si aucun enfant n'est liÃ© et que le parent n'en a qu'un seul

        if not engagement.enfants_concernes.exists() and hasattr(request.user, 'parent'):

            enfants = request.user.parent.enfants.all()

            if enfants.count() == 1:

                engagement.enfants_concernes.add(enfants.first())



        engagement.save()

        # --- PROFILAGE PROGRESSIF APPRENANT ---
        if hasattr(request.user, 'apprenant') and request.user.profile.role == Profile.ROLE_APPRENANT:
            apprenant = request.user.apprenant
            # Mise Ã  jour des informations si elles ne sont pas encore renseignÃ©es
            if not apprenant.classe and data.get('classe'):
                apprenant.classe = data.get('classe')
            if not apprenant.matieres_recherchees and raw_matiere:
                apprenant.matieres_recherchees = raw_matiere
            if not apprenant.preference_de_cours and data.get('course_mode'):
                apprenant.preference_de_cours = data.get('course_mode')
            if not apprenant.quartier_ville and q_obj:
                apprenant.quartier_ville = q_obj
            apprenant.save()

        # --- DEBUT NOTIFICATION WHATSAPP PROFESSEUR ---
        if is_new_engagement:
            import threading

            from .services import send_whatsapp_notification

            # EngagementType est dÃ©jÃ  disponible au niveau global ou local selon le contexte du fichier

            

            teacher_phone = getattr(engagement.professeur, 'telephone_whatsapp', None)

            if not teacher_phone and hasattr(engagement.professeur, 'user'):

                if hasattr(engagement.professeur.user, 'parent'):

                    teacher_phone = getattr(engagement.professeur.user.parent, 'numero_whatsapp', None)

                elif hasattr(engagement.professeur.user, 'apprenant'):

                    teacher_phone = getattr(engagement.professeur.user.apprenant, 'telephone', None)

                

            if teacher_phone:

                prof_name = f"{engagement.professeur.prenom} {engagement.professeur.nom}".strip()

                type_str = "un cours d'ESSAI GRATUIT" if engagement.type_engagement == EngagementType.ESSAI else "une proposition d'ENGAGEMENT STANDARD"

                matiere_str = engagement.matiere

                

                msg_body = (

                    f"Bonjour Professeur {prof_name}, Bonne nouvelle ! Vous avez reÃ§u {type_str} "

                    f"de la part d'un parent pour la matiÃ¨re {matiere_str}. "

                    "Connectez-vous vite sur profchezvousapp.com pour consulter les dÃ©tails et accepter la demande. "

                    "L'Ã©quipe Prof Chez Vous."

                )

                # Envoi asynchrone pour ne pas bloquer la rÃ©ponse HTTP

                threading.Thread(target=send_whatsapp_notification, args=(teacher_phone, msg_body)).start()

        # --- FIN NOTIFICATION WHATSAPP PROFESSEUR ---



        # --- DEBUT NOTIFICATION EMAIL PROFESSEUR ---

        if is_new_engagement and engagement.type_engagement == EngagementType.ESSAI:

            from .utils_emails import send_essai_scheduled_email

            professor_user = engagement.professeur.user

            send_essai_scheduled_email(professor_user, engagement)

        # --- FIN NOTIFICATION EMAIL PROFESSEUR ---



        return JsonResponse({

            'success': True,

            'message': 'Votre proposition d\'engagement a Ã©tÃ© enregistrÃ©e avec succÃ¨s.',

            'engagement_id': engagement.id

        })

    except Exception as e:

        return JsonResponse({'error': str(e)}, status=500)





@csrf_exempt

@login_required

@require_http_methods(["POST"])

@transaction.atomic

def api_engagement_action(request, engagement_id):

    """API pour qu'un professeur accepte ou refuse un engagement."""

    from .choices import StatutGeneral, ConversationStatus, EngagementType

    from .models import Engagement, Conversation, Message

    

    engagement = get_object_or_404(Engagement, id=engagement_id)

    

    # SÃ©curitÃ©: Seul le professeur concernÃ© peut agir

    if not hasattr(request.user, 'teacher_profile') or engagement.professeur != request.user.teacher_profile:

        return JsonResponse({'error': 'Action non autorisÃ©e'}, status=403)

        

    try:

        data = json.loads(request.body)

        action = data.get('action') # 'accepter' ou 'refuser'

        

        # SÃ©curitÃ©: Ne pas agir sur un engagement dÃ©jÃ  traitÃ©

        if engagement.statut_general not in [StatutGeneral.EN_ATTENTE, StatutGeneral.ESSAI_PROGRAMME]:

            return JsonResponse({'error': 'Cet engagement a dÃ©jÃ  Ã©tÃ© traitÃ©.'}, status=400)



        if action == 'accepter':

            if engagement.type_engagement == EngagementType.ESSAI:

                engagement.statut_general = StatutGeneral.ESSAI_CONFIRME

            else:

                engagement.statut_general = StatutGeneral.CONFIRME

            engagement.date_confirmation = timezone.now()
            try:
                from .services_fiabilite import attribuer_points_reactivite
                attribuer_points_reactivite(engagement, engagement.date_confirmation)
            except Exception as e:
                pass

            

            # Calcul du temps de rÃ©ponse (en minutes)

            from decimal import Decimal

            diff = engagement.date_confirmation - engagement.date_creation

            engagement.temps_reponse_prof = Decimal(str(round(diff.total_seconds() / 60, 2)))

            

            # 1. Trouver ou CrÃ©er la conversation (plus robuste que get_or_create)

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

            

            # 2. Lier l'engagement Ã  la conversation

            engagement.conversation = conversation

            

            # 3. Mettre Ã  jour l'engagement actif de la conversation

            conversation.engagement_actif = engagement

            conversation.save()

            

            # 4. Mettre Ã  jour les stats du professeur

            teacher = engagement.professeur

            teacher.nb_engagements_confirmes = Engagement.objects.filter(

                professeur=teacher, 

                statut_general=StatutGeneral.CONFIRME

            ).exclude(type_engagement=EngagementType.ESSAI).count()

            

            # Message automatique supprimÃ© selon la demande


            # Mise Ã  jour du temps de rÃ©ponse moyen (basÃ© uniquement sur les essais)

            from .choices import EngagementType

            responses = Engagement.objects.filter(

                professeur=teacher, 

                temps_reponse_prof__isnull=False,

                type_engagement=EngagementType.ESSAI

            ).values_list('temps_reponse_prof', flat=True)

            

            if responses:

                total_time = sum(responses)

                if engagement.type_engagement == EngagementType.ESSAI:

                    total_time += engagement.temps_reponse_prof

                    teacher.temps_moyen_reponse = total_time / (len(responses) + 1)

                else:

                    teacher.temps_moyen_reponse = total_time / len(responses)

            elif engagement.type_engagement == EngagementType.ESSAI:

                teacher.temps_moyen_reponse = engagement.temps_reponse_prof

            

            teacher.save()

            engagement.save()

            

            # --- DEBUT NOTIFICATION WHATSAPP PARENT ---

            import threading

            from .services import send_whatsapp_notification

            

            parent_phone = None

            if hasattr(engagement.parent_apprenant, 'parent'):

                parent_phone = getattr(engagement.parent_apprenant.parent, 'numero_whatsapp', None)

            elif hasattr(engagement.parent_apprenant, 'apprenant'):

                parent_phone = getattr(engagement.parent_apprenant.apprenant, 'telephone', None)

                

            if parent_phone:

                parent_name = engagement.parent_apprenant.first_name or "Parent"

                prof_name = f"{engagement.professeur.prenom} {engagement.professeur.nom}".strip()

                type_str = "votre cours d'essai" if engagement.type_engagement == EngagementType.ESSAI else "votre engagement standard"

                

                msg_body = (

                    f"Bonjour {parent_name}, Le Professeur {prof_name} vient de CONFIRMER {type_str} "

                    f"pour votre enfant ! Vous pouvez dÃ¨s Ã  prÃ©sent vous connecter sur votre espace pour consulter son planning de cours. "

                    "Merci pour votre confiance, L'Ã©quipe Prof Chez Vous."

                )

                # Envoi asynchrone

                threading.Thread(target=send_whatsapp_notification, args=(parent_phone, msg_body)).start()

            # --- FIN NOTIFICATION WHATSAPP PARENT ---



            # --- DEBUT NOTIFICATION EMAIL PARENT/APPRENANT ---

            if engagement.type_engagement == EngagementType.ESSAI:

                from .utils_emails import send_essai_confirmed_email

                parent_user = engagement.parent_apprenant

                send_essai_confirmed_email(parent_user, engagement)

            # --- FIN NOTIFICATION EMAIL PARENT/APPRENANT ---



            return JsonResponse({'success': True, 'message': 'Engagement acceptÃ©', 'conversation_id': conversation.id})

            

        elif action == 'refuser':

            engagement.statut_general = StatutGeneral.REFUSE

            engagement.save()

            return JsonResponse({'success': True, 'message': 'Engagement refusÃ©'})

            

        else:

            return JsonResponse({'error': 'Action inconnue'}, status=400)

            

    except Exception as e:

        return JsonResponse({'error': str(e)}, status=500)





@login_required

def conversation_detail(request, conversation_id):

    """Page de discussion privÃ©e entre deux participants."""

    from .choices import StatutGeneral, TypeAbonnement

    from .models import Conversation, Message, Profile as Role

    from django.contrib import messages as django_messages

    

    conversation = get_object_or_404(Conversation, id=conversation_id)

    

    # SÃ©curitÃ© stricte: VÃ©rification que l'utilisateur est bien participant

    if request.user not in conversation.participants.all():

        django_messages.error(request, "AccÃ¨s non autorisÃ© Ã  cette conversation.")

        return redirect("messagerie")

    

    # VÃ©rification que l'utilisateur a un profil valide

    try:

        user_profile = request.user.profile

    except Role.DoesNotExist:

        django_messages.error(request, "Profil utilisateur incomplet. Veuillez finaliser votre compte.")

        return redirect("finalisation_compte")

        

    # Charger les messages avec marquage de changement de date

    raw_messages = conversation.messages.all().order_by("date_envoi")

    chat_messages = []

    last_date = None

    has_shown_finalization_badge = False

    

    eng = conversation.engagement_actif
    if eng:
        eng.check_and_update_essai_status()
        
    # DÃ©terminer le rÃ´le

    user_role = request.user.profile.role if hasattr(request.user, 'profile') else None

    

    # VÃ©rifier l'abonnement via la propriÃ©tÃ© current_plan (gÃ¨re l'expiration)

    from .choices import TypeAbonnement, Localisation, EngagementType

    is_premium = (

        hasattr(request.user, 'profile')

        and request.user.profile.current_plan == TypeAbonnement.ACCESS_PREMIUM

    )

    is_trial = eng and eng.type_engagement == EngagementType.ESSAI

    

    for msg in raw_messages:

        # Masquage Paywall supprimÃ© (La messagerie est dÃ©sormais normale, fluide et accessible Ã  tous)

        msg.is_locked = False

        

        msg_date = msg.date_envoi.date()

        msg.changed_date = (msg_date != last_date)

        

        if eng and eng.date_finalisation and msg.date_envoi >= eng.date_finalisation and not has_shown_finalization_badge:

            msg.is_first_after_finalization = True

            msg.date_finalisation_display = eng.date_finalisation

            has_shown_finalization_badge = True

        else:

            msg.is_first_after_finalization = False

            

        chat_messages.append(msg)

        last_date = msg_date

    

    # Marquer la conversation comme lue selon le rÃ´le

    if user_profile.role in [Role.ROLE_PARENT, Role.ROLE_APPRENANT]:

        conversation.conversation_lue_par_parent = True

    elif user_profile.role == Role.ROLE_PROF:

        conversation.conversation_lue_par_prof = True

    conversation.save()

    

    # Marquer les messages reÃ§us comme lus (messages oÃ¹ l'utilisateur est destinataire)

    conversation.messages.filter(destinataire=request.user, lu=False).update(

        lu=True, date_lecture=timezone.now()

    )

    

    # Engagements liÃ©s

    linked_engagements = conversation.engagements.prefetch_related('enfants_concernes').order_by("-date_creation")

    

    # Logique de blocage (cohÃ©rente avec api_send_message)

    is_blocked = False

    hide_input = False

    blocking_message = ""

    # eng, is_premium, is_trial, user_role sont dÃ©jÃ  dÃ©finis plus haut

    

    from .models import Profile

    is_user_prof = (user_role == Profile.ROLE_PROF) or (conversation.professeur and request.user == conversation.professeur.user)



    if eng and user_role in ['PARENT', 'APPRENANT']:

        # 1. BloquÃ© si en attente ou refusÃ©

        if eng.statut_general in ['EN_ATTENTE', 'REFUSE']:

            is_blocked = True

            hide_input = True

            blocking_message = "En attente de la confirmation du professeur." if eng.statut_general == 'EN_ATTENTE' else "Cet engagement a Ã©tÃ© refusÃ©."

        # Plus de blocage liÃ© au paiement.

                

    is_eligible_to_finalize = True  # On autorise par dÃ©faut



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

    

    # Enfants du parent pour le filtre

    parent_children = []

    if user_role == Role.ROLE_PARENT and hasattr(request.user, 'parent'):

        parent_children = request.user.parent.enfants.all()

    elif user_role == Role.ROLE_PROF and conversation.parent and hasattr(conversation.parent, 'parent'):

        parent_children = conversation.parent.parent.enfants.all()

        

    # Nom Ã  afficher (rÃ¨gles dynamiques)

    eng = conversation.engagement_actif

    other_role = other_user.profile.role if other_user and hasattr(other_user, 'profile') else None

    

    if other_role == Role.ROLE_PROF:

        p = conversation.professeur

        raw_name = f"{p.prenom} {p.nom}" if p else "Inconnu"

        if len(raw_name) > 20: raw_name = raw_name[:18] + "..."

        display_name = f"Prof. {raw_name}"

    elif other_role == Role.ROLE_APPRENANT:

        display_name = other_user.get_full_name() or other_user.username

    elif other_role == Role.ROLE_PARENT:

        enfants_liste = []

        if eng and eng.enfants_concernes.exists():

            enfants_liste = eng.enfants_concernes.all()

        if not enfants_liste:

            # Chercher un autre engagement dans cette conversation

            for e in conversation.engagements.all():

                if e.enfants_concernes.exists():

                    enfants_liste = e.enfants_concernes.all()

                    break

        if not enfants_liste and hasattr(other_user, 'parent'):

            # Prendre le premier enfant du parent par dÃ©faut

            enfants_liste = other_user.parent.enfants.all()

            

        if enfants_liste:

            enfants_names = ", ".join([e.prenom for e in enfants_liste])

            if len(enfants_names) > 18: enfants_names = enfants_names[:16] + "..."

            display_name = f"Parent de {enfants_names}"

        else:

            p_name = other_user.get_full_name() or other_user.username

            if len(p_name) > 15: p_name = p_name[:13] + "..."

            display_name = f"Parent ({p_name})"

    else:

        display_name = "Interlocuteur PCV"



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

    

    # SÃ©curitÃ© stricte

    if request.user not in conversation.participants.all():

        return JsonResponse({'error': 'Non autorisÃ©'}, status=403)

    

    # Suppression de la validation anti-spam stricte (5 msg/min) pour permettre 

    # des envois successifs fluides aux utilisateurs autorisÃ©s (Premium/PayÃ©).

        

    # VÃ©rifier le blocage (mÃªme logique que conversation_detail)

    from .choices import TypeAbonnement, EngagementType

    user_role = None

    try:

        user_role = request.user.profile.role

    except Exception:

        pass



    if user_role in ['PARENT', 'APPRENANT']:

        active_eng = conversation.engagement_actif

        if active_eng:

            if active_eng.statut_general in ['EN_ATTENTE', 'REFUSE']:

                return JsonResponse({'error': 'En attente de la confirmation du professeur.' if active_eng.statut_general == 'EN_ATTENTE' else 'Cet engagement a Ã©tÃ© refusÃ©.'}, status=403)

            # Plus de blocage liÃ© au paiement.



    try:

        texte = request.POST.get('texte', '').strip()

        fichier = request.FILES.get('fichier')

        

        # Validation renforcÃ©e du contenu

        if not texte and not fichier:

            return JsonResponse({'error': 'Un message ou un fichier est requis'}, status=400)

        

        if texte and len(texte) > 2000:

            return JsonResponse({'error': 'Le message ne peut pas dÃ©passer 2000 caractÃ¨res'}, status=400)

            

        if request.user == conversation.parent:

            destinataire = conversation.professeur.user if conversation.professeur else None

        else:

            destinataire = conversation.parent

            

        if not destinataire:

            return JsonResponse({'error': 'Destinataire introuvable (profil incomplet ou supprimÃ©).'}, status=400)

        

        message = Message.objects.create(

            conversation=conversation,

            auteur=request.user,

            destinataire=destinataire,

            contenu_texte=texte,

            contenu_media=fichier

        )

        

        # Mettre Ã  jour la conversation

        if fichier:

            is_image = fichier.content_type.startswith('image/')

            prefix = "Ã°Å¸â€œÂ· Photo" if is_image else "Ã°Å¸â€œâ€ž Fichier"

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

        

        # Envoi d'email de notification au destinataire en arriÃ¨re-plan
        import threading
        from .utils_emails import send_new_message_email
        threading.Thread(
            target=send_new_message_email,
            args=(destinataire, request.user, message.contenu_texte, conversation.id)
        ).start()

        

        return JsonResponse({

            'success': True,

            'message_id': message.id,

            'date': timezone.localtime(message.date_envoi).strftime("%H:%M")

        })

        

    except Exception as e:

        return JsonResponse({'error': str(e)}, status=500)





@login_required

@require_http_methods(["GET"])

def api_fetch_new_messages(request, conversation_id):

    """API pour rÃ©cupÃ©rer les nouveaux messages (Polling AJAX)."""

    from .models import Conversation

    from django.utils import timezone

    

    conversation = get_object_or_404(Conversation, id=conversation_id)

    

    if request.user not in conversation.participants.all():

        return JsonResponse({'error': 'Non autorisÃ©'}, status=403)

        

    last_msg_id = request.GET.get('last_msg_id', 0)

    try:

        last_msg_id = int(last_msg_id)

    except ValueError:

        last_msg_id = 0

        

    new_messages = conversation.messages.filter(id__gt=last_msg_id).order_by('date_envoi')

    

    # Marquer les messages reÃ§us comme lus

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



    # GÃ©rer newly_read: les messages de l'utilisateur qui Ã©taient non lus et qui sont passÃ©s Ã  lu

    unread_ids_str = request.GET.get('unread_ids', '')

    newly_read = []

    if unread_ids_str:

        unread_ids = [int(x) for x in unread_ids_str.split(',') if x.strip().isdigit()]

        if unread_ids:

            newly_read = list(conversation.messages.filter(id__in=unread_ids, lu=True).values_list('id', flat=True))



    from .choices import TypeAbonnement, EngagementType

    eng = conversation.engagement_actif

    user_role = request.user.profile.role if hasattr(request.user, 'profile') else None

    is_premium = (

        hasattr(request.user, 'profile')

        and request.user.profile.current_plan == TypeAbonnement.ACCESS_PREMIUM

    )

    is_trial = eng and eng.type_engagement == EngagementType.ESSAI

    

    messages_data = []

    for msg in new_messages:

        texte = msg.contenu_texte

        file_url = msg.contenu_media.url if msg.contenu_media else None

        file_name = msg.contenu_media.name.split('/')[-1] if msg.contenu_media else None

        is_locked = False

        

        # Masquage Paywall supprimÃ© (La messagerie est dÃ©sormais accessible Ã  tous)

        is_locked = False

        

        messages_data.append({

            'id': msg.id,

            'text': texte,

            'fichier_url': file_url,

            'fichier_nom': file_name,

            'date': timezone.localtime(msg.date_envoi).strftime("%H:%M"),

            'is_mine': msg.auteur == request.user,

            'lu': msg.lu,

            'is_locked': is_locked

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

        return JsonResponse({'error': 'Non autorisÃ©'}, status=403)

        

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

        loc_val = str(data.get('localisation', engagement.localisation_option)).strip()
        if loc_val.isdigit():
            from .models import Quartier
            q = Quartier.objects.filter(id=int(loc_val)).first()
            if q:
                loc_val = f"{q.nom} ({q.ville})" if q.ville else q.nom
        engagement.localisation_option = loc_val

        # SÃ©curitÃ© : indications gÃ©ographiques uniquement pour les essais (anti-contournement)

        if engagement.type_engagement == EngagementType.ESSAI:

            engagement.indications_geographiques = data.get('indications_geographiques', engagement.indications_geographiques)

        else:

            engagement.indications_geographiques = ''

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

    """API pour qu'un parent finalise un engagement aprÃ¨s accord."""

    from .choices import StatutGeneral

    from .models import Engagement

    

    engagement = get_object_or_404(Engagement, id=engagement_id)

    

    if engagement.parent_apprenant != request.user:

        return JsonResponse({'error': 'Action non autorisÃ©e'}, status=403)

        

    try:

        engagement.statut_general = StatutGeneral.FINALISE

        engagement.save()

        

        # Mettre Ã  jour stats prof

        teacher = engagement.professeur

        teacher.nb_engagements_finalises = Engagement.objects.filter(professeur=teacher, statut_general=StatutGeneral.FINALISE).count()

        teacher.save()

        

        return JsonResponse({'success': True, 'message': 'Engagement finalisÃ© avec succÃ¨s'})

    except Exception as e:

        return JsonResponse({'error': str(e)}, status=500)



@login_required

@require_http_methods(["POST"])

def api_mark_popup_partage_vu(request):

    """API pour marquer le popup d'incitation au partage comme vu par le professeur."""

    if not hasattr(request.user, 'role') or request.user.role != 'PROFESSEUR':

        return JsonResponse({'error': 'Action non autorisÃ©e'}, status=403)

        

    try:

        prof = request.user.teacher_profile

        prof.popup_partage_vu = True

        prof.save(update_fields=['popup_partage_vu'])

        return JsonResponse({'success': True})

    except Exception as e:

        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)



# --- ADMIN DASHBOARD (SPA & API) ---

from django.utils import timezone

from datetime import timedelta

from django.db.models import Avg, Count

from .models import Evaluation


from django.http import FileResponse, Http404

@login_required
def admin_telecharger_photo_hd(request, prof_id):
    if not request.user.is_superuser:
        raise Http404("AccÃ¨s refusÃ©")
    
    prof = get_object_or_404(TeacherProfile, pk=prof_id)
    if not prof.photo_de_profil:
        raise Http404("Aucune photo disponible")
    
    # Ouvre le fichier original directement depuis le stockage (Cloudinary)
    try:
        import requests
        from django.http import HttpResponse
        
        # Cloudinary direct stream to avoid potential 'open()' issues on remote storage
        response = requests.get(prof.photo_de_profil.url, stream=True)
        if response.status_code == 200:
            file_ext = prof.photo_de_profil.name.split('.')[-1] if '.' in prof.photo_de_profil.name else 'jpg'
            file_name = f"photo_hd_{prof.prenom}_{prof.nom}.{file_ext}"
            
            http_response = HttpResponse(response.raw, content_type=response.headers.get('content-type'))
            http_response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return http_response
        else:
            raise Http404("Fichier distant introuvable")
    except Exception as e:
        # Fallback to standard Django FileResponse
        file_ext = prof.photo_de_profil.name.split('.')[-1] if '.' in prof.photo_de_profil.name else 'jpg'
        file_name = f"photo_hd_{prof.prenom}_{prof.nom}.{file_ext}"
        return FileResponse(
            prof.photo_de_profil.open('rb'), 
            as_attachment=True, 
            filename=file_name
        )


@login_required
def debug_admin_pcv(request):

    """Point d'entrÃ©e du dashboard administrateur"""
    if not request.user.is_superuser:
        return redirect('home')

    return render(request, "core/admin_dashboard/base.html")



def admin_api_accueil(request):

    """Retourne le HTML partiel pour l'accueil du dashboard"""

    from django.core.cache import cache

    

    # OPTIMISATION NEON : Mise en cache des stats du dashboard admin pendant 15 minutes

    context = cache.get('admin_dashboard_context')

    

    if not context:

        from django.contrib.auth import get_user_model

        User = get_user_model()

        

        # 1. Statistiques Globales

        total_inscrits = User.objects.filter(is_superuser=False).count()

        total_parents = Profile.objects.filter(role=Profile.ROLE_PARENT).count()

        total_apprenants = Profile.objects.filter(role=Profile.ROLE_APPRENANT).count()

        total_professeurs = Profile.objects.filter(role=Profile.ROLE_PROF).count()

        

        total_users_avec_role = total_parents + total_apprenants + total_professeurs

        total_incomplets = total_inscrits - total_users_avec_role

    

        engagements = Engagement.objects.all()
        
        # Mise Ã  jour des statuts (Essai ConfirmÃ© -> Essai RÃ©alisÃ©) pour affichage frais dans le dashboard admin
        for eng in engagements.filter(statut_general='ESSAI_CONFIRME', type_engagement='ESSAI'):
            eng.check_and_update_essai_status()
        stats_engagements = engagements.values('statut_general').annotate(count=Count('id'))

        dict_engagements = {stat['statut_general']: stat['count'] for stat in stats_engagements}

        total_engagements = engagements.count()

    

        evaluations = Evaluation.objects.all()

        total_evaluations = evaluations.count()

        moyenne_generale = evaluations.aggregate(Avg('note'))['note__avg'] or 0

    

        # Nouvelles statistiques de lancement

        from django.db.models import Sum

        from .models import Parent, TeacherProfile, Apprenant, Seance, Message, PageAnalytics

        from .choices import EngagementType

    

        parent_recherches = Parent.objects.aggregate(total=Sum('nb_recherches'))['total'] or 0

        apprenant_recherches = Apprenant.objects.aggregate(total=Sum('nb_recherches'))['total'] or 0

        total_recherches = parent_recherches + apprenant_recherches

        

        parent_profils = Parent.objects.aggregate(total=Sum('nb_profils_consultes'))['total'] or 0

        apprenant_profils = Apprenant.objects.aggregate(total=Sum('nb_profils_consultes'))['total'] or 0

        total_profils_consultes = parent_profils + apprenant_profils

        

        total_vues_profil = TeacherProfile.objects.aggregate(total=Sum('nb_vues_profil'))['total'] or 0

        total_vues_plan = Profile.objects.aggregate(total=Sum('nb_vues_page_plan'))['total'] or 0

        total_vues_suivi = Profile.objects.aggregate(total=Sum('nb_vues_suivi'))['total'] or 0

        total_connexions = Profile.objects.aggregate(total=Sum('nb_connexions'))['total'] or 0

        

        total_seances = Seance.objects.count()

        total_messages = Message.objects.count()

        

        essais_programmes = engagements.filter(type_engagement=EngagementType.ESSAI, statut_general=StatutGeneral.ESSAI_PROGRAMME).count()

        essais_confirmes = engagements.filter(type_engagement=EngagementType.ESSAI, statut_general=StatutGeneral.ESSAI_CONFIRME).count()

        essais_realises = engagements.filter(type_engagement=EngagementType.ESSAI, statut_general=StatutGeneral.ESSAI_REALISE).count()

        engagements_finalises = engagements.filter(statut_general__in=[StatutGeneral.FINALISE, StatutGeneral.ENGAGEMENT_FINALISE]).count()

        

        taux_conversion = 0

        if essais_realises > 0:

            taux_conversion = round((engagements_finalises / essais_realises) * 100, 1)

    

        # 2. Engagements Prioritaires

        # Condition: Statut "En attente" + Parent/Apprenant Access+ Premium + DÃ©lai >= 30 min

        limite_temps = timezone.now() - timedelta(minutes=30)

        engagements_prioritaires = list(Engagement.objects.filter(

            statut_general=StatutGeneral.EN_ATTENTE,

            date_creation__lte=limite_temps,

            parent_apprenant__abonnements__type_abonnement=TypeAbonnement.ACCESS_PREMIUM

        ).select_related('parent_apprenant').distinct())

    

        context = {

            'total_inscrits': total_inscrits,

            'total_parents': total_parents,

            'total_apprenants': total_apprenants,

            'total_professeurs': total_professeurs,

            'total_incomplets': total_incomplets,

            'total_engagements': total_engagements,

            'dict_engagements': dict_engagements,

            'StatutGeneral': StatutGeneral,

            'total_evaluations': total_evaluations,

            'moyenne_generale': round(moyenne_generale, 1),

            'engagements_prioritaires': engagements_prioritaires,

            'total_recherches': total_recherches,

            'total_profils_consultes': total_profils_consultes,

            'total_vues_profil': total_vues_profil,

            'essais_programmes': essais_programmes,

            'essais_confirmes': essais_confirmes,

            'essais_realises': essais_realises,

            'engagements_finalises': engagements_finalises,

            'taux_conversion': taux_conversion,

            'total_vues_plan': total_vues_plan,

            'total_vues_suivi': total_vues_suivi,

            'total_connexions': total_connexions,

            'total_seances': total_seances,

            'total_messages': total_messages,

            'vues_page_ressources': PageAnalytics.objects.filter(page_name='Centre de Ressources').values_list('view_count', flat=True).first() or 0,

        }

        

        cache.set('admin_dashboard_context', context, 60 * 15)

    return render(request, "core/admin_dashboard/partials/accueil.html", context)



def admin_api_professeurs(request):

    """Retourne le HTML partiel pour la liste des professeurs selon le filtre"""

    statut = request.GET.get('statut', ValidationStatus.EN_ATTENTE)

    # Optimisation N+1 (Ã‰vite les crashs si beaucoup de profils)
    professeurs = TeacherProfile.objects.filter(
        statut_de_validation=statut
    ).select_related('user').prefetch_related(
        'quartiers_couverts', 'diplomes'
    ).order_by('-user__date_joined')

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

    try:

        prof = get_object_or_404(TeacherProfile, id=prof_id)

        action = request.POST.get('action')

        

        if action == 'valider':

            prof.statut_de_validation = ValidationStatus.VALIDE

            prof.save()

            # L'email de fÃ©licitations est envoyÃ© automatiquement par le model save()

            return JsonResponse({'success': True, 'message': 'Professeur valid\u00e9 avec succ\u00e8s.'})

            

        elif action == 'incomplet':

            raison = request.POST.get('raison', 'Informations incomplÃ¨tes.')

            prof.message_admin = raison

            prof.statut_de_validation = ValidationStatus.INCOMPLET

            prof.save()

            # L'email de dossier incomplet est envoyÃ© automatiquement par le model save()

            return JsonResponse({'success': True, 'message': 'Statut mis \u00e0 jour et email envoy\u00e9.'})

            

        elif action == 'valider_note':

            note = request.POST.get('note', '')

            print(f"[SIMULATION EMAIL] Email envoyÃ© Ã  {prof.email} avec la note d'Ã©valuation: {note}")

            return JsonResponse({'success': True, 'message': 'Note enregistr\u00e9e et email envoy\u00e9.'})

        return JsonResponse({'success': False, 'error': 'Action non reconnue.'}, status=400)

    except Exception as e:

        import traceback

        traceback.print_exc()

        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def admin_api_videos(request):
    """Retourne le HTML partiel pour la modÃ©ration des vidÃ©os selon le filtre de statut."""
    from .models import TeacherVideo
    statut = request.GET.get('statut', TeacherVideo.STATUT_EN_ATTENTE)
    search = request.GET.get('q', '').strip()

    videos = TeacherVideo.objects.select_related('teacher', 'teacher__user')

    if statut in [TeacherVideo.STATUT_EN_ATTENTE, TeacherVideo.STATUT_VALIDE, TeacherVideo.STATUT_REFUSE]:
        videos = videos.filter(statut_validation=statut)

    if search:
        videos = videos.filter(
            models.Q(teacher__nom__icontains=search) |
            models.Q(teacher__prenom__icontains=search) |
            models.Q(titre__icontains=search)
        )

    videos = videos.order_by('-date_soumission')

    # Compteurs pour les badges de filtres
    count_attente = TeacherVideo.objects.filter(statut_validation=TeacherVideo.STATUT_EN_ATTENTE).count()
    count_valide = TeacherVideo.objects.filter(statut_validation=TeacherVideo.STATUT_VALIDE).count()
    count_refuse = TeacherVideo.objects.filter(statut_validation=TeacherVideo.STATUT_REFUSE).count()

    context = {
        'videos': videos,
        'statut_actif': statut,
        'search_query': search,
        'count_attente': count_attente,
        'count_valide': count_valide,
        'count_refuse': count_refuse,
        'TeacherVideo': TeacherVideo,
        'site_config': SiteConfiguration.get_solo(),
    }
    return render(request, "core/admin_dashboard/partials/videos.html", context)


@csrf_exempt
@require_http_methods(["POST"])
def admin_api_toggle_video_feature(request):
    """Bascule (active/dÃ©sactive) l'accÃ¨s des professeurs Ã  la soumission et gestion des vidÃ©os."""
    config = SiteConfiguration.get_solo()
    action = request.POST.get('action')

    if action == 'toggle':
        config.allow_teacher_video_submissions = not config.allow_teacher_video_submissions
        config.save()
    elif action == 'set':
        state = request.POST.get('state') == 'true'
        config.allow_teacher_video_submissions = state
        config.save()

    status_str = "dÃ©bloquÃ©e (active)" if config.allow_teacher_video_submissions else "bloquÃ©e (dÃ©sactivÃ©e)"
    return JsonResponse({
        'success': True,
        'allow_teacher_video_submissions': config.allow_teacher_video_submissions,
        'message': f"FonctionnalitÃ© des vidÃ©os professeur {status_str}."
    })


@csrf_exempt
@require_http_methods(["POST"])
def admin_api_video_action(request, video_id):
    """Action de modÃ©ration d'une vidÃ©o (valider ou refuser avec suggestions)."""
    from .models import TeacherVideo
    from .utils_emails import send_video_approved_email, send_video_rejected_email
    import threading

    video = get_object_or_404(TeacherVideo, id=video_id)
    action = request.POST.get('action')

    if action == 'valider':
        video.statut_validation = TeacherVideo.STATUT_VALIDE
        video.date_validation = timezone.now()
        if request.user.is_authenticated:
            video.valide_par = request.user
        video.save()

        # Envoi d'email de validation en arriÃ¨re-plan
        threading.Thread(target=send_video_approved_email, args=(video,)).start()

        return JsonResponse({
            'success': True,
            'message': f"La vidÃ©o de {video.teacher.prenom} {video.teacher.nom} a Ã©tÃ© validÃ©e avec succÃ¨s. Un email de confirmation lui a Ã©tÃ© envoyÃ©."
        })

    elif action == 'refuser':
        suggestions = request.POST.get('suggestions', '').strip()
        if not suggestions:
            return JsonResponse({
                'success': False,
                'error': "Veuillez prÃ©ciser vos conseils et axes d'amÃ©lioration pour le professeur."
            }, status=400)

        video.statut_validation = TeacherVideo.STATUT_REFUSE
        video.motif_refus_suggestions = suggestions
        video.date_validation = timezone.now()
        if request.user.is_authenticated:
            video.valide_par = request.user
        video.save()

        # Envoi d'email de refus/suggestions en arriÃ¨re-plan
        threading.Thread(target=send_video_rejected_email, args=(video, suggestions)).start()

        return JsonResponse({
            'success': True,
            'message': f"La vidÃ©o a Ã©tÃ© refusÃ©e. Les suggestions d'amÃ©lioration ont Ã©tÃ© envoyÃ©es par email Ã  {video.teacher.prenom} {video.teacher.nom}."
        })

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
        enfant = get_object_or_404(Enfant.objects.select_related('quartier_ville', 'parent'), id=id_eleve)
        
        if hasattr(request.user, 'parent') and enfant.parent == request.user.parent:
            is_owner = True
        elif not is_teacher:
            raise Http404("Profil introuvable ou accÃ¨s refusÃ©.")
            
        obj_text = enfant.objectif_principal
        objectifs = []
        difficultes = []
        if obj_text and "DIFFICULTÃ‰S:" in obj_text:
            parts = obj_text.split("DIFFICULTÃ‰S:")
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
        apprenant = get_object_or_404(Apprenant.objects.select_related('quartier_ville', 'user'), id=id_eleve)

        

        if apprenant.user == request.user:

            is_owner = True

        elif not is_teacher:

            raise Http404("Profil introuvable ou accÃ¨s refusÃ©.")

            

        eleve_data = {

            'type': 'apprenant',

            'id': apprenant.id,

            'nom': apprenant.nom,

            'photo_url': apprenant.photo_de_profil.url if apprenant.photo_de_profil else None,

            'quartier_ville': getattr(apprenant, 'quartier_ville', "Non spÃ©cifiÃ©"),

            'classe': apprenant.get_classe_display() if hasattr(apprenant, 'get_classe_display') else apprenant.classe,

            'matieres': apprenant.matieres_recherchees,

            'difficultes': [apprenant.description_difficultes] if apprenant.description_difficultes else [],

            'objectifs': [obj_dict.get(o, o) for o in apprenant.objectifs_motivations]

        }

    else:

        raise Http404("Type d'Ã©lÃ¨ve invalide.")



    return render(request, "core/profil_eleve.html", {

        "eleve": eleve_data,

        "is_owner": is_owner,

        "is_teacher": is_teacher,

        "missing_info": not eleve_data['difficultes'] or not eleve_data['objectifs']

    })



@login_required

def edit_enfant(request, id_enfant):

    enfant = get_object_or_404(Enfant, id=id_enfant)

    

    if not hasattr(request.user, 'parent') or enfant.parent != request.user.parent:

        from django.http import HttpResponseForbidden

        return HttpResponseForbidden("Vous n'avez pas l'autorisation de modifier ce profil.")

        

    parent = request.user.parent

        

    if request.method == "POST":

        from .forms import EditEnfantForm

        form = EditEnfantForm(request.POST, instance=enfant)

        if form.is_valid():

            parent.numero_whatsapp = form.cleaned_data['numero_whatsapp']

            parent.save()

            form.save()

            from django.contrib import messages

            messages.success(request, f"Le profil de {enfant.prenom} a Ã©tÃ© mis Ã  jour.")

            return redirect("profil_eleve", type_eleve='enfant', id_eleve=enfant.id)

    else:

        # PrÃ©-remplir les champs multiples si nÃ©cessaire

        initial = {'numero_whatsapp': parent.numero_whatsapp}

        obj_text = enfant.objectif_principal

        if obj_text and "DIFFICULTÃ‰S:" in obj_text:

            parts = obj_text.split("DIFFICULTÃ‰S:")

            obj_str = parts[0].replace("OBJECTIFS:", "").strip()

            diff_str = parts[1].strip()

            initial['objectifs_motivations'] = [o.strip() for o in obj_str.split(',') if o.strip()]

            initial['difficultes_predefinies'] = [d.strip() for d in diff_str.split(',') if d.strip()]

        

        from .forms import EditEnfantForm

        form = EditEnfantForm(instance=enfant, initial=initial)

        

    return render(request, "core/edit_enfant.html", {

        "form": form,

        "enfant": enfant

    })







# ==========================================

# ESPACE DE SUIVI PÃ‰DAGOGIQUE

# ==========================================



@login_required

def suivi_engagement(request, engagement_id):

    from django.http import Http404

    engagement = get_object_or_404(Engagement, id=engagement_id)

    

    is_parent_apprenant = engagement.parent_apprenant == request.user

    is_prof = hasattr(request.user, 'teacher_profile') and engagement.professeur == request.user.teacher_profile

    if not (is_parent_apprenant or is_prof):

        raise Http404("AccÃ¨s refusÃ©.")

        

    # IncrÃ©menter le compteur de consultation pour la collecte de donnÃ©es (sauf comptes de test)

    if is_parent_apprenant and hasattr(request.user, 'profile') and request.user.email not in getattr(settings, 'TEST_ACCOUNT_EMAILS', []):

        request.user.profile.nb_vues_suivi += 1

        request.user.profile.save(update_fields=['nb_vues_suivi'])

        

    seances = engagement.seances.prefetch_related('notions').order_by('-date_seance')[:5]

    

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

    is_prof = hasattr(request.user, 'teacher_profile') and engagement.professeur == request.user.teacher_profile

    is_apprenant = hasattr(request.user, 'apprenant') and engagement.parent_apprenant == request.user # L'apprenant est l'utilisateur liÃ© Ã  l'engagement

    

    if not (is_parent_apprenant or is_prof or is_apprenant):

        raise Http404("AccÃ¨s refusÃ©.")

        

    seances = engagement.seances.prefetch_related('notions').order_by('-date_seance')

    

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

        return JsonResponse({"error": "MÃ©thode non autorisÃ©e."}, status=405)

        

    engagement = get_object_or_404(Engagement, id=engagement_id)

    is_prof = hasattr(request.user, 'teacher_profile') and engagement.professeur == request.user.teacher_profile

    

    if not is_prof:

        return JsonResponse({"error": "AccÃ¨s refusÃ©. Seul le professeur peut ajouter une sÃ©ance."}, status=403)

        

    try:

        from datetime import datetime

        date_seance_str = request.POST.get('date_seance')

        date_seance = datetime.strptime(date_seance_str, "%Y-%m-%d").date()

        

        # VÃ©rification : 1 seule sÃ©ance par jour

        if Seance.objects.filter(engagement=engagement, date_seance=date_seance).exists():

            return JsonResponse({"error": f"Vous avez dÃ©jÃ  enregistrÃ© une sÃ©ance pour la date du {date_seance.strftime('%d/%m/%Y')}."}, status=400)

            

        objectifs = request.POST.get('objectifs')

        difficultes_presentes = request.POST.get('difficultes_presentes') == 'oui'

        difficultes_rencontrees = request.POST.get('difficultes_rencontrees', '')

        taches_domicile = request.POST.get('taches_domicile', '')

        

        import json

        notions_data = request.POST.get('notions_json')

        if not notions_data:

            return JsonResponse({"error": "Aucune notion trouvÃ©e."}, status=400)

            

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

        

        return JsonResponse({"success": True, "message": "SÃ©ance ajoutÃ©e avec succÃ¨s."})

        

    except Exception as e:

        return JsonResponse({"error": str(e)}, status=400)



@login_required

def api_valider_seance(request, seance_id):

    from .models import Seance

    if request.method != "POST":

        return JsonResponse({"error": "MÃ©thode non autorisÃ©e."}, status=405)

        

    seance = get_object_or_404(Seance, id=seance_id)

    if seance.engagement.parent_apprenant != request.user:

        return JsonResponse({"error": "AccÃ¨s refusÃ©. Seul le parent/apprenant peut valider."}, status=403)

        

    seance.validee = True

    seance.save()

    try:
        from .services_fiabilite import attribuer_points_journal
        attribuer_points_journal(seance)
    except Exception:
        pass

    return JsonResponse({"success": True})





import json

from django.db.models import F



def api_track_teacher_views(request):

    """

    Endpoint pour incrÃ©menter le nombre d'apparitions (vues) des professeurs

    lorsque leur carte entre rÃ©ellement dans le champ visuel sur la page de recherche.

    """

    if request.method != "POST":

        return JsonResponse({"error": "MÃ©thode non autorisÃ©e."}, status=405)

        

    # Ignorer les comptes de test

    if request.user.is_authenticated and getattr(settings, 'TEST_ACCOUNT_EMAILS', []) and request.user.email in settings.TEST_ACCOUNT_EMAILS:

        return JsonResponse({"success": True, "tracked": 0, "ignored": True})

        

    try:

        data = json.loads(request.body)

        prof_ids = data.get('prof_ids', [])

        

        if prof_ids and isinstance(prof_ids, list):

            # Ne garder que les entiers valides

            valid_ids = [int(pid) for pid in prof_ids if str(pid).isdigit()]

            if valid_ids:

                from .models import TeacherProfile

                TeacherProfile.objects.filter(id__in=valid_ids).update(

                    nombre_apparitions_recherche=F('nombre_apparitions_recherche') + 1,

                    nombre_apparitions_mois=F('nombre_apparitions_mois') + 1

                )

                return JsonResponse({"success": True, "tracked": len(valid_ids)})

                

        return JsonResponse({"success": False, "error": "DonnÃ©es invalides."})

    except Exception as e:

        return JsonResponse({"error": str(e)}, status=400)





@login_required

def toggle_favori(request, prof_id):

    if request.method != "POST":

        return JsonResponse({"error": "MÃ©thode non autorisÃ©e."}, status=405)

    

    prof = get_object_or_404(TeacherProfile, id=prof_id)

    if request.user in prof.parents_favoris.all():

        prof.parents_favoris.remove(request.user)

        is_favorite = False

    else:

        prof.parents_favoris.add(request.user)

        is_favorite = True

        # IncrÃ©menter le compteur historique (ne dÃ©crÃ©mente jamais)

        prof.total_favoris_historique += 1

        prof.save(update_fields=['total_favoris_historique'])

        

    return JsonResponse({"success": True, "is_favorite": is_favorite})



@login_required

def masquer_engagement(request, eng_id):

    if request.method != "POST":

        return JsonResponse({"error": "MÃ©thode non autorisÃ©e."}, status=405)

        

    engagement = get_object_or_404(Engagement, id=eng_id)

    if engagement.parent_apprenant != request.user:

        return JsonResponse({"error": "AccÃ¨s refusÃ©."}, status=403)

        

    try:
        import json
        data = json.loads(request.body)
        action = data.get("action", "masquer")
    except:
        action = "masquer"

    if action == "demasquer":
        engagement.masque_par_parent = False
        engagement.masque_pour_parent = False
    else:
        engagement.masque_par_parent = True
        engagement.masque_pour_parent = True

    engagement.save()

    return JsonResponse({"success": True})



@login_required

def masquer_engagement_prof(request, eng_id):

    if request.method != "POST":

        return JsonResponse({"error": "MÃ©thode non autorisÃ©e."}, status=405)

        

    engagement = get_object_or_404(Engagement, id=eng_id)

    if not hasattr(request.user, 'teacher_profile') or engagement.professeur != request.user.teacher_profile:

        return JsonResponse({"error": "AccÃ¨s refusÃ©."}, status=403)

        

    try:
        import json
        data = json.loads(request.body)
        action = data.get("action", "masquer")
    except:
        action = "masquer"

    if action == "demasquer":
        engagement.masque_pour_professeur = False
    else:
        engagement.masque_pour_professeur = True

    engagement.save()

    return JsonResponse({"success": True})





@login_required

def api_toggle_essai(request):

    """Bascule l'activation de l'essai gratuit pour le professeur connectÃ©."""

    try:

        teacher = request.user.teacher_profile

    except TeacherProfile.DoesNotExist:

        return JsonResponse({'success': False, 'error': 'AccÃ¨s rÃ©servÃ© aux professeurs.'}, status=403)



    if request.method == 'POST':

        teacher.essai_gratuit_actif = not teacher.essai_gratuit_actif

        teacher.save()

        return JsonResponse({

            'success': True,

            'actif': teacher.essai_gratuit_actif,

            'message': 'Statut de l\'essai gratuit mis Ã  jour.'

        })

    

    return JsonResponse({'success': False, 'error': 'MÃ©thode non autorisÃ©e.'}, status=405)





@login_required

def api_engagement_details(request, engagement_id):

    """API pour rÃ©cupÃ©rer les dÃ©tails complets d'un engagement (pour les modaux)."""

    engagement = get_object_or_404(

        Engagement.objects.select_related(

            'professeur', 'parent_apprenant', 'parent_apprenant__apprenant', 'parent_apprenant__profile'

        ).prefetch_related('enfants_concernes'), 

        id=engagement_id

    )

    

    # SÃ©curitÃ©: Seuls les acteurs de l'engagement peuvent voir les dÃ©tails

    is_prof = hasattr(request.user, 'teacher_profile') and engagement.professeur == request.user.teacher_profile

    is_client = engagement.parent_apprenant == request.user

    

    if not (is_prof or is_client):

        return JsonResponse({'error': 'AccÃ¨s refusÃ©'}, status=403)

        

    data = {

        'id': engagement.id,

        'matiere': engagement.matiere,

        'classe': engagement.get_classe_display(),

        'mode': engagement.get_mode_de_cours_display(),

        'mode_raw': engagement.mode_de_cours,

        'lieu': engagement.get_localisation_display,

        'indications_geographiques': engagement.indications_geographiques,

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

        'student_name': engagement.enfants_concernes.first().prenom if engagement.enfants_concernes.exists() else (engagement.parent_apprenant.apprenant.nom if hasattr(engagement.parent_apprenant, 'apprenant') else "Moi-mÃªme"),

        # Essai specific fields

        'date_essai': timezone.localtime(engagement.date_heure_essai).strftime("%d/%m/%Y") if engagement.date_heure_essai else None,

        'heure_debut': timezone.localtime(engagement.date_heure_essai).strftime("%H:%M") if engagement.date_heure_essai else None,

        'heure_fin': timezone.localtime(engagement.date_heure_fin_essai).strftime("%H:%M") if engagement.date_heure_fin_essai else None,

        'description_essai': engagement.description_essai,

        'client_role': engagement.parent_apprenant.profile.role if hasattr(engagement.parent_apprenant, 'profile') else 'PARENT',

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

                return JsonResponse({'error': 'AccÃ¨s non autorisÃ©'}, status=403)

                

            eng = conversation.engagement_actif

            if not eng:

                return JsonResponse({'error': 'Aucun engagement actif pour cette conversation'}, status=400)

                

            eng.paiement_effectue = True

            eng.save()

            return JsonResponse({'status': 'success', 'message': 'Paiement standard effectuÃ© (fictif)'})

            

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

            return JsonResponse({'status': 'success', 'message': 'Passage au plan Premium effectuÃ© (fictif)'})

            

        else:

            return JsonResponse({'error': 'Type de paiement invalide'}, status=400)

            

    except Exception as e:

        return JsonResponse({'error': str(e)}, status=500)





@login_required

@require_http_methods(["POST"])

def api_archive_conversation(request, conversation_id):

    """Archive ou dÃ©sarchive une conversation pour l'utilisateur courant."""

    from .models import Conversation

    conversation = get_object_or_404(Conversation, id=conversation_id)

    if request.user not in conversation.participants.all():

        return JsonResponse({'error': 'Non autorisÃ©'}, status=403)

        

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

        return JsonResponse({'error': 'Non autorisÃ©'}, status=403)

    conversation.masquee_par.add(request.user)

    return JsonResponse({'success': True})





@login_required

@require_http_methods(["GET"])

def api_ping(request):

    """

    Endpoint lÃ©ger appelÃ© toutes les X secondes par le front-end

    pour vÃ©rifier s'il y a des mises Ã  jour d'engagements ou de messages.

    """

    import datetime

    

    last_check_str = request.GET.get('last_check')

    has_updates = False

    

    if last_check_str:

        try:

            last_check = datetime.datetime.fromtimestamp(int(last_check_str) / 1000.0, tz=datetime.timezone.utc)

            

            # VÃ©rifier les nouveaux messages non lus

            if Message.objects.filter(destinataire=request.user, lu=False, date_envoi__gt=last_check).exists():

                has_updates = True

            

            # VÃ©rifier les mises Ã  jour d'engagement

            if not has_updates:

                user_engs = Engagement.objects.filter(

                    Q(professeur__user=request.user) | Q(parent_apprenant=request.user)

                )

                if user_engs.filter(date_mise_a_jour__gt=last_check).exists():

                    has_updates = True

        except Exception:

            pass

            

    return JsonResponse({'has_updates': has_updates})







@login_required

def api_toggle_essai(request):

    """Bascule l'activation de l'essai gratuit pour le professeur connectÃ©."""

    try:

        teacher = request.user.teacher_profile

    except TeacherProfile.DoesNotExist:

        return JsonResponse({'success': False, 'error': 'AccÃ¨s rÃ©servÃ© aux professeurs.'}, status=403)



    if request.method == 'POST':

        teacher.essai_gratuit_actif = not teacher.essai_gratuit_actif

        teacher.save()

        return JsonResponse({

            'success': True,

            'actif': teacher.essai_gratuit_actif,

            'message': 'Statut de l\'essai gratuit mis Ã  jour.'

        })

    

    return JsonResponse({'success': False, 'error': 'MÃ©thode non autorisÃ©e.'}, status=405)









@login_required

@require_http_methods(["POST"])

def api_mark_welcome_seen(request):

    try:

        request.user.profile.a_vu_popup_bienvenue = True

        request.user.profile.save(update_fields=['a_vu_popup_bienvenue'])

        return JsonResponse({'success': True})

    except Exception as e:

        return JsonResponse({'success': False, 'error': str(e)})





@login_required

@require_http_methods(["POST"])

def dismiss_announcement(request, pk):

    try:

        from .models import ProfessorAnnouncement

        announcement = ProfessorAnnouncement.objects.get(pk=pk, is_active=True)

        announcement.dismissed_by.add(request.user)

        return JsonResponse({'status': 'success'})

    except Exception as e:

        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)





from django.contrib.admin.views.decorators import staff_member_required

from django.contrib import messages

from .forms import AnnouncementForm



@staff_member_required

def create_announcement(request):

    from .models import ProfessorAnnouncement

    if request.method == 'POST':

        form = AnnouncementForm(request.POST)

        if form.is_valid():

            announcement = form.save(commit=False)

            if announcement.is_active:

                # DÃ©sactiver TOUTES les annonces prÃ©cÃ©dentes actives

                ProfessorAnnouncement.objects.filter(is_active=True).update(is_active=False)

            announcement.save()

            messages.success(request, "L'annonce a Ã©tÃ© publiÃ©e avec succÃ¨s !")

            return redirect('create_announcement')

    else:

        form = AnnouncementForm()



    return render(request, 'core/admin_create_announcement.html', {'form': form})



# --- IntÃ©gration FedaPay ---



@login_required

def payer_engagement(request, engagement_id):

    """Vue pour initialiser le paiement et rediriger vers FedaPay."""

    engagement = get_object_or_404(Engagement, id=engagement_id)

    

    # VÃ©rifications de sÃ©curitÃ©

    if request.user != engagement.parent_apprenant:

        from django.http import HttpResponseForbidden

        return HttpResponseForbidden("Vous n'Ãªtes pas autorisÃ© Ã  payer cet engagement.")

    if engagement.paiement_effectue:

        messages.info(request, "Ce paiement a dÃ©jÃ  Ã©tÃ© effectuÃ©.")

        if engagement.conversation:

            return redirect('conversation_detail', conversation_id=engagement.conversation.id)

        return redirect('parent_dashboard')



    from .services import initier_paiement_engagement

    from django.urls import reverse

    

    # Construction de l'URL de callback (retour utilisateur / webhook interne)

    callback_url = request.build_absolute_uri(reverse('fedapay_callback'))

    

    try:

        payment_url = initier_paiement_engagement(engagement, request.user, callback_url)

        return redirect(payment_url)

    except Exception as e:

        print(f"Ã°Å¸â€Â´ ERREUR FEDAPAY : {str(e)}")

        # On relÃ¨ve l'erreur pour qu'elle s'affiche en gros sur votre Ã©cran (DEBUG=True)

        raise e





import json

from django.views.decorators.csrf import csrf_exempt



@csrf_exempt

def fedapay_callback(request):

    """

    Webhook / Callback pour recevoir le statut de la transaction FedaPay.

    """

    status = request.GET.get('status')

    transaction_id = request.GET.get('id')

    

    if not transaction_id:

        try:

            payload = json.loads(request.body)

            transaction_id = payload.get('entity', {}).get('id')

            status = payload.get('entity', {}).get('status')

        except:

            pass



    if transaction_id and status:

        from .models import TransactionFedaPay

        try:

            local_txn = TransactionFedaPay.objects.get(transaction_id=str(transaction_id))

            local_txn.statut = status

            

            if status == 'approved':

                import django.utils.timezone as timezone

                local_txn.date_validation = timezone.now()

                # DÃ©bloquer la messagerie

                engagement = local_txn.engagement

                engagement.paiement_effectue = True

                engagement.save()

            

            local_txn.save()

            

            # Si c'est une requÃªte GET, on redirige l'utilisateur

            if request.method == 'GET':

                if status == 'approved':

                    return redirect('paiement_succes', engagement_id=local_txn.engagement.id)

                else:

                    return redirect('paiement_echec', engagement_id=local_txn.engagement.id)

                    

        except TransactionFedaPay.DoesNotExist:

            pass



    return JsonResponse({'status': 'ok'})



@login_required

def paiement_succes(request, engagement_id):

    engagement = get_object_or_404(Engagement, id=engagement_id)

    return render(request, 'core/paiement_succes.html', {'engagement': engagement})



@login_required

def paiement_echec(request, engagement_id):

    engagement = get_object_or_404(Engagement, id=engagement_id)

    return render(request, 'core/paiement_echec.html', {'engagement': engagement})



@login_required

def payer_premium(request):

    """Vue pour initialiser le paiement Premium et rediriger vers FedaPay."""

    from .services import initier_paiement_abonnement

    from django.urls import reverse

    

    callback_url = request.build_absolute_uri(reverse('fedapay_premium_callback'))

    

    try:

        payment_url = initier_paiement_abonnement(request.user, callback_url)

        return redirect(payment_url)

    except Exception as e:

        messages.error(request, f"Erreur lors de l'initialisation du paiement : {str(e)}")

        return redirect('gestion_plan')



@csrf_exempt

def fedapay_premium_callback(request):

    """Webhook / Callback pour l'abonnement Premium FedaPay."""

    status = request.GET.get('status')

    transaction_id = request.GET.get('id')

    

    if not transaction_id:

        try:

            payload = json.loads(request.body)

            transaction_id = payload.get('entity', {}).get('id')

            status = payload.get('entity', {}).get('status')

        except:

            pass



    if transaction_id and status:

        from .models import TransactionFedaPay

        try:

            local_txn = TransactionFedaPay.objects.get(transaction_id=str(transaction_id), type_transaction='ABONNEMENT')

            local_txn.statut = status

            

            if status == 'approved' and not local_txn.date_validation:

                import django.utils.timezone as timezone

                local_txn.date_validation = timezone.now()

                # Mettre Ã  jour l'abonnement de l'utilisateur

                from .choices import TypeAbonnement

                abonnement = local_txn.user.abonnements.order_by('-id').first()

                if abonnement:

                    abonnement.type_abonnement = TypeAbonnement.ACCESS_PREMIUM

                    abonnement.date_debut = timezone.now().date()

                    from datetime import timedelta

                    abonnement.date_fin = timezone.now().date() + timedelta(days=30)

                    abonnement.save()

            

            local_txn.save()

            

            if request.method == 'GET':

                if status == 'approved':

                    messages.success(request, "Votre abonnement Access+ Premium a Ã©tÃ© activÃ© avec succÃ¨s !")

                else:

                    messages.error(request, "Le paiement de votre abonnement a Ã©chouÃ© ou a Ã©tÃ© annulÃ©.")

                return redirect('gestion_plan')

                

        except TransactionFedaPay.DoesNotExist:

            pass



    return JsonResponse({'status': 'ok'})



# --- NOUVEAUX ENDPOINTS : EVALUATION ET CONSENTEMENT MUTUEL ---

from django.views.decorators.http import require_POST



@login_required

@require_POST

def api_rate_professeur(request, engagement_id):

    import json

    from .models import Evaluation

    try:

        engagement = Engagement.objects.get(id=engagement_id)

        if engagement.parent_apprenant != request.user:

            return JsonResponse({'error': 'AccÃ¨s refusÃ©. Vous n\'Ãªtes pas autorisÃ© Ã  Ã©valuer ce professeur.'}, status=403)

            

        data = json.loads(request.body)

        note = int(data.get('note', 0))

        commentaire = data.get('commentaire', '').strip()

        

        if note < 1 or note > 5:

            return JsonResponse({'error': 'La note doit Ãªtre comprise entre 1 et 5.'}, status=400)

            

        # VÃ©rifier si une Ã©valuation existe dÃ©jÃ  pour ce couple parent/professeur

        evaluation, created = Evaluation.objects.update_or_create(

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

        return JsonResponse({

            'success': True, 

            'message': 'Ã‰valuation enregistrÃ©e avec succÃ¨s.' if created else 'Ã‰valuation mise Ã  jour avec succÃ¨s.',

            'note': note

        })

    except Exception as e:

        return JsonResponse({'error': str(e)}, status=500)



@login_required

@require_POST

def api_demander_annulation(request, engagement_id):

    engagement = get_object_or_404(Engagement, id=engagement_id)

    

    # VÃ©rification des droits

    is_prof = hasattr(request.user, 'teacher_profile') and engagement.professeur == request.user.teacher_profile

    is_parent = engagement.parent_apprenant == request.user

    

    if not (is_prof or is_parent):

        return JsonResponse({'error': 'AccÃ¨s refusÃ©.'}, status=403)

        

    if engagement.statut_general == StatutGeneral.ANNULE:

        return JsonResponse({'error': 'Cet engagement est dÃ©jÃ  annulÃ©.'}, status=400)

        

    if engagement.annulation_initiee_par is None:

        # 1. Initiation

        engagement.annulation_initiee_par = request.user

        engagement.save()

        return JsonResponse({'success': True, 'action': 'initiated', 'message': 'Demande d\'annulation envoyÃ©e. En attente de confirmation de l\'autre partie.'})

    elif engagement.annulation_initiee_par != request.user:

        # 2. Confirmation par l'autre partie

        engagement.annulation_confirmee = True

        engagement.statut_general = StatutGeneral.ANNULE

        engagement.save()

        return JsonResponse({'success': True, 'action': 'confirmed', 'message': 'Annulation confirmÃ©e. L\'engagement est maintenant annulÃ©.'})

    else:

        return JsonResponse({'error': 'Vous avez dÃ©jÃ  initiÃ© cette demande.'}, status=400)



@login_required

@require_POST

def api_demander_cloture(request, engagement_id):

    engagement = get_object_or_404(Engagement, id=engagement_id)

    

    is_prof = hasattr(request.user, 'teacher_profile') and engagement.professeur == request.user.teacher_profile

    is_parent = engagement.parent_apprenant == request.user

    

    if not (is_prof or is_parent):

        return JsonResponse({'error': 'AccÃ¨s refusÃ©.'}, status=403)

        

    if engagement.statut_general == StatutGeneral.TERMINE:

        return JsonResponse({'error': 'Cet engagement est dÃ©jÃ  terminÃ©.'}, status=400)

        

    if engagement.cloture_initiee_par is None:

        # 1. Initiation

        engagement.cloture_initiee_par = request.user

        engagement.save()

        return JsonResponse({'success': True, 'action': 'initiated', 'message': 'Demande de clÃ´ture envoyÃ©e. En attente de confirmation de l\'autre partie.'})

    elif engagement.cloture_initiee_par != request.user:

        # 2. Confirmation par l'autre partie

        engagement.cloture_confirmee = True

        engagement.statut_general = StatutGeneral.TERMINE

        engagement.save()

        try:
            from .services_fiabilite import attribuer_points_engagement_termine
            attribuer_points_engagement_termine(engagement)
        except Exception:
            pass

        return JsonResponse({'success': True, 'action': 'confirmed', 'message': 'ClÃ´ture confirmÃ©e. L\'engagement est maintenant terminÃ©.'})

    else:

        return JsonResponse({'error': 'Vous avez dÃ©jÃ  initiÃ© cette demande.'}, status=400)



@login_required

def finalisation_engagement(request, engagement_id):

    engagement = get_object_or_404(Engagement, id=engagement_id)

    

    # VÃ©rification des droits d'accÃ¨s

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

    return render(request, 'core/finalisation_engagement.html', context)



def charte_essai_gratuit(request):

    """

    Affiche la page de la charte de l'essai gratuit.

    """

    return render(request, 'core/charte_essai.html')





def ressources_professeurs_view(request):

    from .models import RessourceProfesseur, FAQProfesseur, PageAnalytics

    from django.db.models import F



    # Analytics increment

    analytics, created = PageAnalytics.objects.get_or_create(page_name="Centre de Ressources")

    PageAnalytics.objects.filter(pk=analytics.pk).update(view_count=F('view_count') + 1)



    ressources = RessourceProfesseur.objects.filter(actif=True)

    faqs = FAQProfesseur.objects.filter(actif=True)

    guide_officiel = ressources.filter(est_guide_officiel=True).first()

    

    trusted_teachers = TeacherProfile.objects.filter(statut_de_validation='APPROVED').exclude(photo_de_profil='').order_by('-id')[:4]

    context = {

        'ressources': ressources,

        'faqs': faqs,

        'guide_officiel': guide_officiel,

        'trusted_teachers': trusted_teachers,
    }

    return render(request, 'core/ressources_professeurs.html', context)





# --- ADMIN DASHBOARD RESSOURCES ET FAQ ---

from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse

from django.shortcuts import render, get_object_or_404

from .models import RessourceProfesseur, FAQProfesseur



def admin_api_ressources(request):

    ressources = RessourceProfesseur.objects.all().order_by('ordre_affichage', '-date_creation')

    return render(request, 'core/admin_dashboard/partials/ressources.html', {'ressources': ressources})



def admin_api_faqs(request):

    faqs = FAQProfesseur.objects.all().order_by('ordre_affichage')

    return render(request, 'core/admin_dashboard/partials/faqs.html', {'faqs': faqs})



@csrf_exempt

def admin_api_ressources_action(request):

    if request.method == 'POST':

        action = request.POST.get('action')

        res_id = request.POST.get('id')

        

        if action == 'delete':

            RessourceProfesseur.objects.filter(id=res_id).delete()

            return JsonResponse({'success': True, 'message': 'Ressource supprimÃ©e.'})

            

        elif action == 'toggle_actif':

            res = get_object_or_404(RessourceProfesseur, id=res_id)

            res.actif = not res.actif

            res.save()

            return JsonResponse({'success': True, 'message': 'Statut modifiÃ©.'})

            

        elif action == 'save':

            titre = request.POST.get('titre', '')

            description = request.POST.get('description', '')

            lien_externe = request.POST.get('lien_externe', '')

            ordre = request.POST.get('ordre_affichage', 0)

            est_guide = request.POST.get('est_guide_officiel') == 'on'

            fichier = request.FILES.get('fichier_pdf')

            

            # Si est_guide_officiel est cochÃ©, dÃ©cocher les autres

            if est_guide:

                RessourceProfesseur.objects.all().update(est_guide_officiel=False)

                

            if res_id:  # Edit

                res = get_object_or_404(RessourceProfesseur, id=res_id)

                res.titre = titre

                res.description = description

                res.lien_externe = lien_externe

                res.ordre_affichage = ordre

                res.est_guide_officiel = est_guide

                if fichier:

                    res.fichier_pdf = fichier

                res.save()

                return JsonResponse({'success': True, 'message': 'Ressource modifiÃ©e.'})

            else:  # Create

                RessourceProfesseur.objects.create(

                    titre=titre,

                    description=description,

                    lien_externe=lien_externe,

                    ordre_affichage=ordre,

                    est_guide_officiel=est_guide,

                    fichier_pdf=fichier

                )

                return JsonResponse({'success': True, 'message': 'Ressource crÃ©Ã©e.'})

                

    return JsonResponse({'error': 'MÃ©thode non autorisÃ©e'}, status=400)



@csrf_exempt

def admin_api_faqs_action(request):

    if request.method == 'POST':

        action = request.POST.get('action')

        faq_id = request.POST.get('id')

        

        if action == 'delete':

            FAQProfesseur.objects.filter(id=faq_id).delete()

            return JsonResponse({'success': True, 'message': 'FAQ supprimÃ©e.'})

            

        elif action == 'toggle_actif':

            faq = get_object_or_404(FAQProfesseur, id=faq_id)

            faq.actif = not faq.actif

            faq.save()

            return JsonResponse({'success': True, 'message': 'Statut modifiÃ©.'})

            

        elif action == 'save':

            question = request.POST.get('question', '')

            reponse = request.POST.get('reponse', '')

            ordre = request.POST.get('ordre_affichage', 0)

            

            if faq_id:

                faq = get_object_or_404(FAQProfesseur, id=faq_id)

                faq.question = question

                faq.reponse = reponse

                faq.ordre_affichage = ordre

                faq.save()

                return JsonResponse({'success': True, 'message': 'FAQ modifiÃ©e.'})

            else:

                FAQProfesseur.objects.create(

                    question=question,

                    reponse=reponse,

                    ordre_affichage=ordre

                )

                return JsonResponse({'success': True, 'message': 'FAQ crÃ©Ã©e.'})

                

    return JsonResponse({'error': 'MÃ©thode non autorisÃ©e'}, status=400)





from django.http import Http404



def download_ressource_prof(request, res_id):

    """

    Vue publique pour tÃ©lÃ©charger dynamiquement un fichier de ressource.

    Redirige vers l'URL du fichier avec forÃ§age du tÃ©lÃ©chargement (fl_attachment).

    """

    from .models import RessourceProfesseur

    from django.shortcuts import get_object_or_404, redirect

    

    res = get_object_or_404(RessourceProfesseur, id=res_id)

    if not res.fichier_pdf:

        raise Http404("Fichier non disponible.")

    

    url = res.fichier_pdf.url

    # Pour forcer le tÃ©lÃ©chargement (cross-origin) via Cloudinary, on injecte fl_attachment

    if 'cloudinary' in url and '/upload/' in url and 'fl_attachment' not in url:

        url = url.replace('/upload/', '/upload/fl_attachment/', 1)

        

    return redirect(url)





@csrf_exempt

@require_POST

def create_search_alert(request):

    """

    API endpoint pour recevoir l'alerte de recherche (Ajax).

    """

    from .models import SearchAlert

    from django.core.mail import send_mail

    from django.conf import settings

    import json

    

    try:

        data = json.loads(request.body)

        contact = data.get('contact', '').strip()

        matiere = data.get('matiere', '').strip()

        localisation = data.get('localisation', '').strip()

        

        if not contact:

            return JsonResponse({"success": False, "error": "Le contact est requis."})

            

        alert = SearchAlert.objects.create(

            contact_info=contact,

            matiere=matiere,

            localisation=localisation

        )

        

        # Envoi d'email Ã  l'admin

        admin_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'hello@profchezvous.com')

        sujet = f"[ProfChezVous] Nouvelle alerte de recherche - {matiere}"

        message = (

            f"Une nouvelle alerte de recherche a Ã©tÃ© crÃ©Ã©e (Aucun rÃ©sultat trouvÃ©).\n\n"

            f"Contact : {contact}\n"

            f"MatiÃ¨re recherchÃ©e : {matiere}\n"

            f"Localisation : {localisation}\n\n"

            f"Connectez-vous Ã  l'admin pour suivre ce lead."

        )

        

        try:

            send_mail(

                sujet,

                message,

                admin_email,

                [admin_email],

                fail_silently=True,

            )

        except Exception as e:

            # Ne pas bloquer l'utilisateur si l'email Ã©choue

            pass

            

        return JsonResponse({"success": True, "message": "Alerte crÃ©Ã©e avec succÃ¨s."})

        

    except Exception as e:

        return JsonResponse({"success": False, "error": str(e)})





@csrf_exempt

@require_http_methods(["POST"])

def toggle_reaction(request, prof_id):

    """Toggle a ðŸ‘ reaction on a teacher's presentation or methodology section.

    Works for both logged-in users and anonymous visitors (via session key)."""

    prof = get_object_or_404(TeacherProfile, id=prof_id)

    

    try:

        data = json.loads(request.body)

    except (json.JSONDecodeError, ValueError):

        return JsonResponse({"success": False, "error": "DonnÃ©es invalides."}, status=400)

    

    section = data.get("section")

    if section not in ("presentation", "methodologie"):

        return JsonResponse({"success": False, "error": "Section invalide."}, status=400)

    

    # Assurer qu'une session existe (mÃªme pour les anonymes)

    if not request.session.session_key:

        request.session.create()

    

    # DÃ©terminer l'identifiant unique du visiteur

    if request.user.is_authenticated:

        lookup = {"professeur": prof, "section": section, "user": request.user}

    else:

        lookup = {"professeur": prof, "section": section, "session_key": request.session.session_key, "user": None}

    

    existing = ProfileReaction.objects.filter(**lookup).first()

    

    if existing:

        # Retirer le like

        existing.delete()

        if section == "presentation":

            prof.likes_presentation = max(0, (prof.likes_presentation or 0) - 1)

            prof.save(update_fields=["likes_presentation"])

        else:

            prof.likes_methodologie = max(0, (prof.likes_methodologie or 0) - 1)

            prof.save(update_fields=["likes_methodologie"])

        liked = False

    else:

        # Ajouter le like

        ProfileReaction.objects.create(**lookup)

        if section == "presentation":

            prof.likes_presentation = (prof.likes_presentation or 0) + 1

            prof.save(update_fields=["likes_presentation"])

        else:

            prof.likes_methodologie = (prof.likes_methodologie or 0) + 1

            prof.save(update_fields=["likes_methodologie"])

        liked = True

    

    count = (prof.likes_presentation or 0) if section == "presentation" else (prof.likes_methodologie or 0)

    return JsonResponse({"success": True, "liked": liked, "count": count})





@login_required

def prof_stats_view(request):

    """Page complÃ¨te de statistiques pour le professeur connectÃ©."""

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



    # Statistiques des engagements

    engagements = teacher.engagements.all()

    nb_contrats_actifs = engagements.filter(

        statut_general=StatutGeneral.FINALISE

    ).exclude(type_engagement=EngagementType.ESSAI).count()

    nb_contrats_total = engagements.exclude(

        type_engagement=EngagementType.ESSAI

    ).exclude(

        statut_general__in=[StatutGeneral.REFUSE, StatutGeneral.ANNULE]

    ).count()



    context = {

        "teacher": teacher,

        "vues_mois": teacher.nombre_apparitions_mois,

        "visites_mois": teacher.nb_vues_mois,

        "contrats_actifs": nb_contrats_actifs,

        "contrats_total": nb_contrats_total,

        "total_favoris": teacher.total_favoris_historique,

        "likes_presentation": teacher.likes_presentation,

        "likes_methodologie": teacher.likes_methodologie,

    }



    return render(request, "core/prof_stats.html", context)







def test_ui_cards(request):

    "Vue de test pour comparer les designs de cartes professeur."

    teacher = TeacherProfile.objects.first()

    return render(request, "core/test_ui_cards.html", {"teacher": teacher})








# --- ADMIN API: AMBASSADEURS ---
from django.db.models import Sum

@login_required
def admin_api_ambassadeurs(request):
    """Retourne la liste des recommandations et des paiements en attente."""
    if not request.user.is_superuser:
        return JsonResponse({"error": "Non autorisÃ©"}, status=403)
        
    try:
        from referrals.models import Referral, Reward, Ambassador
    except ImportError:
        return HttpResponse("<div>L'application referrals n'est pas installÃ©e.</div>")
        
    # Stats globales
    total_paid = Reward.objects.filter(status='PAID').aggregate(total=Sum('amount'))['total'] or 0
    total_pending = Reward.objects.filter(status='PENDING').aggregate(total=Sum('amount'))['total'] or 0
    
    # Recommandations nÃ©cessitant une action (Paiement)
    pending_rewards = Referral.objects.filter(status='REWARD_PENDING').order_by('-created_at')
    
    # Autres recommandations rÃ©centes
    recent_referrals = Referral.objects.exclude(status='REWARD_PENDING').order_by('-created_at')[:20]
    
    context = {
        'total_paid': total_paid,
        'total_pending': total_pending,
        'pending_rewards': pending_rewards,
        'recent_referrals': recent_referrals,
    }
    return render(request, "core/admin_dashboard/partials/ambassadeurs.html", context)

@login_required
def admin_api_ambassadeurs_action(request):
    """Action sur les ambassadeurs (payer une rÃ©compense, annuler, etc.)."""
    if not request.user.is_superuser or request.method != 'POST':
        return JsonResponse({"error": "Non autorisÃ©"}, status=403)
        
    action = request.POST.get('action')
    referral_id = request.POST.get('referral_id')
    
    try:
        from referrals.models import Referral
        referral = Referral.objects.get(id=referral_id)
        
        if action == 'mark_paid':
            if referral.status == 'REWARD_PENDING' and hasattr(referral, 'reward'):
                referral.status = 'REWARD_PAID'
                referral.reward_paid_at = timezone.now()
                referral.save()
                
                reward = referral.reward
                reward.status = 'PAID'
                reward.payment_date = timezone.now()
                reward.admin = request.user
                reward.save()
                
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"error": "Ã‰tat invalide pour paiement."}, status=400)
                
        elif action == 'cancel_referral':
            # Annuler ou refuser une recommandation
            referral.status = 'REJECTED'
            referral.save()
            if hasattr(referral, 'reward') and referral.reward.status == 'PENDING':
                referral.reward.status = 'CANCELLED'
                referral.reward.save()
            return JsonResponse({"success": True})
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
        
    return JsonResponse({"error": "Action inconnue."}, status=400)

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

def selection_personnalisee(request, uuid):
    from .models import ParentSelection
    from django.shortcuts import get_object_or_404, render

    selection = get_object_or_404(ParentSelection, id=uuid)

    # RÃ©cupÃ©rer tous les profs liÃ©s (sans filtrer par statut, car l'admin les a choisis manuellement)
    professeurs = selection.professeurs.all()

    # Appliquer les mÃªmes annotations que la page de recherche (moyenne_avis, nombre_avis, etc.)
    professeurs = annotate_teachers_with_ratings(professeurs)

    context = {
        "selection": selection,
        "professeurs": professeurs,
        "is_selection_page": True,
    }
    return render(request, 'core/selection_page.html', context)



def api_cron_check_essais(request):
    """
    Point d'entrÃ©e pour le service de Cron externe (ex: cron-job.org).
    SÃ©curisÃ© par un token statique.
    """
    from django.conf import settings
    from django.http import JsonResponse
    from django.core.management import call_command
    
    # Jeton de sÃ©curitÃ© basique (peut Ãªtre mis dans les variables d'environnement .env)
    EXPECTED_TOKEN = getattr(settings, 'CRON_SECRET_TOKEN', 'eCxnh2J54foTuWMoeQtRU7BURLa8B7vs4u1q_OkO5uw')
    
    token = request.GET.get('token')
    if token != EXPECTED_TOKEN:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    try:
        # ExÃ©cute la commande que nous avons crÃ©Ã©e prÃ©cÃ©demment
        call_command('check_essais')
        return JsonResponse({'success': True, 'message': 'Cron check_essais exÃ©cutÃ© avec succÃ¨s.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@login_required
@require_POST
def api_mark_visite_guidee_vue(request):
    try:
        profile = request.user.teacher_profile
        profile.a_vu_visite_guidee = True
        profile.save()
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
