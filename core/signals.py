from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from core.models import Profile, Abonnement, TypeAbonnement
from core.utils_emails import send_welcome_email_async

@receiver(post_save, sender=User)
def create_user_profile_and_abonnement(sender, instance, created, **kwargs):
    if created:
        # Create an Abonnement by default
        Abonnement.objects.create(
            user=instance,
            type_abonnement=TypeAbonnement.STANDARD,
            prix="2000f par engagement"
        )

@receiver(post_save, sender=Profile)
def send_welcome_email_on_profile_creation(sender, instance, created, **kwargs):
    if created:
        # Envoi de l'email asynchrone selon le rôle défini dans le profil
        send_welcome_email_async(instance.user, instance)
