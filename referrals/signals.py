from django.dispatch import receiver
from django.db.models.signals import post_save
from allauth.account.signals import user_signed_up
from django.utils import timezone
from core.models import TeacherProfile
from .models import Referral, ReferralProgram, Reward

@receiver(user_signed_up)
def handle_user_signed_up(sender, request, user, **kwargs):
    """
    Lorsque l'utilisateur s'inscrit via allauth, on vérifie s'il y a un referral_id
    dans la session. Si oui, on associe l'utilisateur au referral.
    """
    referral_id = request.session.get('referral_id')
    if referral_id:
        try:
            referral = Referral.objects.get(id=referral_id)
            if not referral.referred_teacher:
                referral.referred_teacher = user
                referral.status = 'ACCOUNT_CREATED'
                referral.account_created_at = timezone.now()
                referral.save()
            
            # On nettoie la session
            del request.session['referral_id']
        except Referral.DoesNotExist:
            pass

@receiver(post_save, sender=TeacherProfile)
def handle_teacher_profile_update(sender, instance, created, **kwargs):
    """
    Gère la mise à jour des statuts du parrainage en fonction de l'évolution
    du profil du professeur (créé, en révision, validé).
    """
    if not instance.user:
        return
        
    try:
        referral = Referral.objects.get(referred_teacher=instance.user)
        
        status_changed = False
        now = timezone.now()
        
        # 1. Profil complété
        if referral.status == 'ACCOUNT_CREATED' and instance.statut_de_validation == 'PENDING':
            referral.status = 'PROFILE_COMPLETED'
            referral.profile_completed_at = now
            status_changed = True
            
        # 2. Profil vérifié
        elif referral.status in ['ACCOUNT_CREATED', 'PROFILE_COMPLETED', 'UNDER_REVIEW'] and instance.statut_de_validation == 'APPROVED':
            referral.status = 'VERIFIED'
            referral.verified_at = now
            status_changed = True
            
        if status_changed:
            referral.save()
            
        # 3. Génération de la récompense si vérifié et pas encore récompensé
        if referral.status == 'VERIFIED':
            # On vérifie si une récompense existe déjà pour ce referral (pour éviter les doublons)
            if not Reward.objects.filter(teacher=referral.referrer, payment_reference=f"REF-{referral.id}").exists():
                reward_amount = ReferralProgram.get_current_amount()
                
                Reward.objects.create(
                    teacher=referral.referrer,
                    amount=reward_amount,
                    status='PENDING',
                    payment_reference=f"REF-{referral.id}"
                )
                
                referral.status = 'REWARD_PENDING'
                referral.reward_generated_at = now
                referral.save()
                
    except Referral.DoesNotExist:
        pass
