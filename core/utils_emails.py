import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
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

    # Détermination du template en fonction du rôle
    if profile.role == Profile.ROLE_PARENT:
        template_name = "emails/welcome_parent.html"
        subject = "Bienvenue sur Prof Chez Vous !"
    elif profile.role == Profile.ROLE_APPRENANT:
        template_name = "emails/welcome_apprenant.html"
        subject = "Bienvenue sur Prof Chez Vous !"
    elif profile.role == Profile.ROLE_PROF:
        template_name = "emails/welcome_teacher.html"
        subject = "Bienvenue sur Prof Chez Vous - Complétez votre profil"
    else:
        logger.info("Rôle inconnu '%s' pour %s, email de bienvenue ignoré.", profile.role, user.username)
        return False

    try:
        context = {
            'user': user,
            'profile': profile,
        }
        html_content = render_to_string(template_name, context)

        msg = EmailMultiAlternatives(
            subject=subject,
            body="Bonjour,\n\nVotre client de messagerie ne supporte pas le HTML.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        logger.info("Email de bienvenue envoyé avec succès à %s (%s).", user.email, profile.role)
        return True

    except Exception as e:
        logger.error(
            "Échec d'envoi de l'email de bienvenue à %s (user_id=%s, role=%s) : %s",
            user.email, user.pk, profile.role, e,
            exc_info=True,
        )
        return False
