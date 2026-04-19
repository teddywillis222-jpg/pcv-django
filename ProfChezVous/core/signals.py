from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from core.models import Profile, Abonnement, TypeAbonnement

@receiver(post_save, sender=User)
def create_user_profile_and_abonnement(sender, instance, created, **kwargs):
    if created:
        # Create an Abonnement by default
        Abonnement.objects.create(
            user=instance,
            type_abonnement=TypeAbonnement.STANDARD,
            prix="2000f par engagement"
        )
