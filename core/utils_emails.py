import logging
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse
from .models import Profile

logger = logging.getLogger(__name__)


def send_welcome_email(user, profile):
    """
    Envoie un email de bienvenue synchrone et protégé.
    Si l'envoi échoue, l'erreur est loguée proprement sans bloquer l'inscription.
    """
    # Garde : pas d'email = pas d'envoi
    if not user.email:
        logger.warning("Aucun email pour l'utilisateur %s (id=%s), email de bienvenue ignoré.", user.username, user.pk)
        return False

    name = user.first_name or user.username

    # Détermination du template en fonction du rôle
    if profile.role == Profile.ROLE_PARENT:
        sujet_parent = "Bienvenue chez Prof Chez Vous – L'excellence académique commence ici"
        message_parent = f"""Bonjour {name},

Nous sommes ravis de vous compter parmi les familles qui choisissent l’exigence pour la réussite de leurs enfants.

En rejoignant Prof Chez Vous, vous n’avez pas simplement accès à un catalogue de professeurs : vous accédez à un écosystème sécurisé conçu pour transformer le potentiel de votre enfant en résultats concrets.

Ce qui vous attend désormais :

La Certification : Tous les professeurs présents sur la plateforme passent par un processus de vérification rigoureux (diplômes et identité).
Espaces de Suivi Dédiés : Pour chaque matière (engagement) souscrite, vous disposez d'un espace de suivi exclusif.
Maîtrise du Niveau : Pilotez en temps réel la progression et le niveau de votre enfant dans chaque discipline spécifique grâce à votre tableau de bord.
Confidentialité Totale : Vos échanges et vos données sont protégés par notre infrastructure sur-mesure.

Votre première étape ? Complétez le profil de votre premier enfant pour nous aider à lui proposer les profils les plus adaptés à ses besoins.

Bienvenue dans l'élite,

L'équipe Prof Chez Vous."""
        sujet = sujet_parent
        message = message_parent

    elif profile.role == Profile.ROLE_PROF:
        sujet_prof = "Bienvenue chez Prof Chez Vous – Activez votre profil d'élite"
        message_prof = f"""Cher(e) {name},

Nous sommes honorés de votre inscription sur Prof Chez Vous. Vous rejoignez aujourd'hui une communauté qui place la pédagogie, l'expertise et la rigueur au sommet des priorités.

Comme vous l'avez constaté, vous avez été redirigé vers la création de votre profil professionnel. C’est l’étape la plus cruciale de votre parcours chez nous.

Pourquoi soigner votre profil dès maintenant ?

La Certification : Un profil complet est le préalable à l'obtention du badge "Certifié". Préparez vos justificatifs (CNI et Diplômes) pour notre équipe de modération.

La Visibilité : Plus votre profil est précis, plus vous inspirez confiance aux parents exigeants qui recherchent le meilleur pour leurs enfants.

L'Outil de Travail : Une fois votre profil validé, vous accéderez à votre espace pour gérer vos engagements et utiliser nos outils de suivi digitalisés.

Prenez le temps de bien remplir chaque section. Votre expertise mérite d'être mise en valeur avec précision.

Votre mission commence ici : Enseigner, Inspirer, Réussir.

Professionnellement,

La Direction, Prof Chez Vous."""
        sujet = sujet_prof
        message = message_prof

    elif profile.role == Profile.ROLE_APPRENANT:
        sujet_apprenant = "Prêt(e) pour le sommet ? Bienvenue sur Prof Chez Vous !"
        message_apprenant = f"""Salut {name},

Bienvenue sur la plateforme qui va changer ta manière d'apprendre. Ici, on ne fait pas que du "soutien scolaire", on te donne les clés pour maîtriser tes matières et viser l'excellence.

Avec ton compte Prof Chez Vous :

Trouve ton mentor : Accède à une sélection de professeurs passionnés et certifiés pour t'accompagner dans tes objectifs.

Suis ta progression : Pour chaque matière, visualise tes avancées et tes points d'amélioration grâce aux bilans de tes enseignants.

Le coaching PCV : Reste attentif à tes e-mails ! Chaque semaine, nous t'enverrons des conseils exclusifs et des méthodes éprouvées pour booster ta productivité et ton mental.

Le chemin vers tes résultats commence ici. Connecte-toi, choisis ton expert et prépare-toi à briller.

À très vite,

L'équipe Prof Chez Vous."""
        sujet = sujet_apprenant
        message = message_apprenant

    else:
        logger.info("Rôle inconnu '%s' pour %s, email de bienvenue ignoré.", profile.role, user.username)
        return False

    try:
        send_mail(
            subject=sujet,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        logger.info("Email de bienvenue envoyé avec succès à %s (%s).", user.email, profile.role)
        return True

    except Exception as e:
        logger.error(
            "Échec d'envoi de l'email de bienvenue à %s (user_id=%s, role=%s) : %s",
            user.email, user.pk, profile.role, e,
            exc_info=True,
        )
        return False

def get_full_url(path):
    try:
        domain = Site.objects.get_current().domain
    except Exception:
        domain = "profchezvousapp.com"
    protocol = "https" if not settings.DEBUG else "http"
    return f"{protocol}://{domain}{path}"

def send_teacher_approved_email(user, teacher_profile):
    if not user.email:
        return False
    
    name = teacher_profile.nom or user.first_name or user.username
    dashboard_url = get_full_url(reverse("prof_dashboard"))

    sujet = 'Félicitations ! Votre profil est désormais "Certifié"'
    message = f"""Cher(e) {name},

Après étude de votre dossier, notre équipe a le plaisir de vous annoncer que votre profil a été approuvé.

Votre expertise est désormais visible par les familles et apprenants sur la plateforme Prof Chez Vous. Vous bénéficiez dès à présent du badge "Certifié", gage de confiance et d'excellence.

Conseil de réussite : Veillez à répondre rapidement aux demandes d'engagement pour maintenir un excellent score de réactivité sur votre profil.

Accédez à votre tableau de bord dès maintenant :
{dashboard_url}

Bonne chance pour vos futures séances !

L'équipe Prof Chez Vous"""

    try:
        send_mail(
            subject=sujet,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info("Email de validation envoyé avec succès à %s.", user.email)
        return True
    except Exception as e:
        logger.error("Échec d'envoi de l'email de validation à %s : %s", user.email, e, exc_info=True)
        return False

def send_teacher_incomplete_email(user, teacher_profile, reason):
    if not user.email:
        return False
    
    name = teacher_profile.nom or user.first_name or user.username
    edit_url = get_full_url(reverse("prof_create_profile"))

    sujet = "Action requise : Optimisation de votre dossier Prof Chez Vous"
    message = f"""Cher(e) {name},

Nous avons bien reçu vos documents. Pour garantir le standard d'excellence de la plateforme, une mise à jour de votre profil est nécessaire avant sa publication.

Motif(s) de la mise en attente :

{reason}

Ce que vous devez faire :
1. Connectez-vous à votre espace.
2. Rectifiez les éléments mentionnés ci-dessus.
3. Soumettez à nouveau votre profil.

Vous pouvez mettre à jour votre profil via ce lien :
{edit_url}

Nous vous rappelons que vous pouvez resoumettre votre dossier à tout moment pour étude.

L'équipe Prof Chez Vous"""

    try:
        send_mail(
            subject=sujet,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info("Email de dossier incomplet envoyé avec succès à %s.", user.email)
        return True
    except Exception as e:
        logger.error("Échec d'envoi de l'email de dossier incomplet à %s : %s", user.email, e, exc_info=True)
        return False


def send_essai_scheduled_email(professor_user, engagement):
    """
    Email envoyé au professeur lorsqu'un parent ou apprenant programme un cours d'essai.
    """
    if not professor_user.email:
        logger.warning("Aucun email pour le professeur %s (id=%s), notification d'essai programmé ignorée.", professor_user.username, professor_user.pk)
        return False

    prof_email = professor_user.email
    prof_name = engagement.professeur.prenom or professor_user.first_name or "Professeur"
    parent_name = engagement.parent_apprenant.first_name or "Un parent"
    matiere = engagement.matiere or "Non précisée"
    classe = engagement.classe or "Non précisée"
    mode = engagement.get_mode_de_cours_display() if hasattr(engagement, 'get_mode_de_cours_display') else (engagement.mode_de_cours or "Non précisé")

    # Date et heure de l'essai
    date_str = ""
    if engagement.date_heure_essai:
        from django.utils import timezone as tz
        dt_local = tz.localtime(engagement.date_heure_essai)
        date_str = dt_local.strftime("%A %d %B %Y à %Hh%M")

    dashboard_url = get_full_url(reverse("prof_dashboard"))

    sujet = "Nouvelle demande de cours d'essai – Prof Chez Vous"
    message = f"""Bonjour Professeur {prof_name},

Excellente nouvelle ! {parent_name} vient de programmer un cours d'essai avec vous sur Prof Chez Vous.

Voici les détails de la demande :

    Matière : {matiere}
    Classe : {classe}
    Mode de cours : {mode}"""

    if date_str:
        message += f"""
    Date proposée : {date_str}"""

    message += f"""

L'étape suivante est entre vos mains : connectez-vous à votre espace professeur pour consulter la demande complète et confirmer (ou proposer un autre créneau).

Accéder à mon tableau de bord :
{dashboard_url}

Conseil : Les professeurs qui répondent rapidement obtiennent un meilleur score de réactivité et sont davantage mis en avant auprès des familles.

Professionnellement,

L'équipe Prof Chez Vous."""

    try:
        send_mail(
            subject=sujet,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[prof_email],
            fail_silently=False,
        )
        logger.info("Email de notification d'essai programmé envoyé avec succès à %s.", prof_email)
    except Exception as e:
        logger.error("Échec d'envoi de l'email d'essai programmé à %s : %s", prof_email, e, exc_info=True)
            
    return True


def send_essai_confirmed_email(parent_user, engagement):
    """
    Email envoyé au parent ou apprenant lorsque le professeur confirme le cours d'essai.
    """
    if not parent_user.email:
        logger.warning("Aucun email pour %s (id=%s), notification de confirmation d'essai ignorée.", parent_user.username, parent_user.pk)
        return False

    parent_email = parent_user.email
    parent_name = parent_user.first_name or "Cher(e) utilisateur"
    prof_name = f"{engagement.professeur.prenom} {engagement.professeur.nom}".strip() or "Votre professeur"
    matiere = engagement.matiere or "Non précisée"

    # Date et heure de l'essai
    date_str = ""
    if engagement.date_heure_essai:
        from django.utils import timezone as tz
        dt_local = tz.localtime(engagement.date_heure_essai)
        date_str = dt_local.strftime("%A %d %B %Y à %Hh%M")

    # Lien vers le bon espace selon le rôle
    if hasattr(parent_user, 'parent'):
        dashboard_url = get_full_url(reverse("parent_dashboard"))
    else:
        dashboard_url = get_full_url(reverse("apprenant_dashboard"))

    sujet = "Votre cours d'essai est confirmé ! – Prof Chez Vous"
    message = f"""Bonjour {parent_name},

Bonne nouvelle ! Le Professeur {prof_name} vient de confirmer votre cours d'essai.

Récapitulatif :

    Professeur : {prof_name}
    Matière : {matiere}"""

    if date_str:
        message += f"""
    Date et heure : {date_str}"""

    message += f"""

Que faire maintenant ?

1. Connectez-vous à votre espace pour consulter tous les détails de la séance.
2. Préparez vos questions ou les points que vous souhaitez aborder durant ce premier cours.
3. Profitez de cette séance pour évaluer la pédagogie du professeur et voir si le courant passe.

Accéder à mon espace :
{dashboard_url}

Nous vous souhaitons une excellente première séance !

Cordialement,

L'équipe Prof Chez Vous."""

    try:
        send_mail(
            subject=sujet,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[parent_email],
            fail_silently=False,
        )
        logger.info("Email de confirmation d'essai envoyé avec succès à %s.", parent_email)
    except Exception as e:
        logger.error("Échec d'envoi de l'email de confirmation d'essai à %s : %s", parent_email, e, exc_info=True)
            
    return True

