import logging
from django.core.mail import send_mail
from django.conf import settings
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
