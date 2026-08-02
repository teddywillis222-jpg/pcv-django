import random
import string
from django.db import models
from django.conf import settings as django_settings
from django.utils import timezone

def generate_referral_code():
    length = 6
    chars = string.ascii_uppercase + string.digits
    while True:
        code = "PCV" + ''.join(random.choice(chars) for _ in range(length))
        if not Ambassador.objects.filter(code=code).exists():
            return code

class ReferralProgram(models.Model):
    current_reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=django_settings.REFERRAL_DEFAULT_REWARD_AMOUNT, help_text="Montant de la prime en FCFA")
    enabled = models.BooleanField(default=True)
    terms_version = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "Programme Ambassadeur"
        verbose_name_plural = "Programme Ambassadeurs"

    def __str__(self):
        return f"Programme Ambassadeur - {self.current_reward_amount} FCFA"

    @classmethod
    def get_current_amount(cls):
        program = cls.objects.first()
        if program:
            return program.current_reward_amount
        return django_settings.REFERRAL_DEFAULT_REWARD_AMOUNT

class Ambassador(models.Model):
    """Stocke le code personnel d'un parrain"""
    user = models.OneToOneField(django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ambassador_profile')
    code = models.CharField(max_length=20, unique=True, default=generate_referral_code)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Ambassadeur {self.user} - {self.code}"

class Referral(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('VISITED', 'Lien visité'),
        ('ACCOUNT_CREATED', 'Compte créé'),
        ('PROFILE_COMPLETED', 'Profil complété'),
        ('UNDER_REVIEW', 'En vérification'),
        ('VERIFIED', 'Vérifié'),
        ('REWARD_PENDING', 'Récompense en attente'),
        ('REWARD_PAID', 'Récompense payée'),
        ('REJECTED', 'Refusé'),
    ]

    referrer = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referrals_made')
    referred_teacher = models.OneToOneField(django_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='referral_received')
    referral_code = models.CharField(max_length=20)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='VISITED')
    
    # Historisation
    visited_at = models.DateTimeField(null=True, blank=True)
    account_created_at = models.DateTimeField(null=True, blank=True)
    profile_completed_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    reward_generated_at = models.DateTimeField(null=True, blank=True)
    reward_paid_at = models.DateTimeField(null=True, blank=True)
    
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Recommandation"
        verbose_name_plural = "Recommandations"

    def __str__(self):
        return f"Recommandation de {self.referrer} - Code {self.referral_code}"

class Reward(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('PAID', 'Payée'),
        ('CANCELLED', 'Annulée'),
    ]

    referral = models.OneToOneField(Referral, on_delete=models.CASCADE, related_name='reward')
    teacher = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rewards')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    payment_reference = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    admin = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='rewards_processed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Récompense"
        verbose_name_plural = "Récompenses"

    def __str__(self):
        return f"Récompense {self.amount} - {self.teacher}"
