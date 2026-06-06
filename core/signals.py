import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from core.models import Profile, Abonnement, TypeAbonnement
from core.utils_emails import send_welcome_email

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_profile_and_abonnement(sender, instance, created, **kwargs):
    if created:
        # Create an Abonnement by default
        Abonnement.objects.create(
            user=instance,
            type_abonnement=TypeAbonnement.STANDARD,
            prix="2000f par engagement"
        )

import threading

@receiver(post_save, sender=Profile)
def send_welcome_email_on_profile_creation(sender, instance, created, **kwargs):
    if created:
        def send_email_async():
            try:
                send_welcome_email(instance.user, instance)
            except Exception as e:
                # Fail-safe : ne jamais bloquer la création du profil
                logger.error(
                    "Signal email bienvenue - échec critique pour user_id=%s : %s",
                    instance.user_id, e,
                    exc_info=True,
                )
        
        # Envoi de l'email en arrière-plan pour ne pas ralentir l'inscription
        # email_thread = threading.Thread(target=send_email_async)
        # email_thread.start()
        # NOTE: Désactivé temporairement pour éviter la redondance avec l'email de vérification obligatoire d'Allauth.

from django.contrib.auth.signals import user_logged_in

@receiver(user_logged_in)
def track_user_login(sender, request, user, **kwargs):
    if hasattr(user, 'profile'):
        user.profile.nb_connexions += 1
        user.profile.save(update_fields=['nb_connexions'])
