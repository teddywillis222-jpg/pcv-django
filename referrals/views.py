from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q
from .models import Ambassador, Referral, Reward, ReferralProgram
from core.models import TeacherProfile

def ambassador_landing_page(request, referral_code):
    ambassador = get_object_or_404(Ambassador, code=referral_code)
    
    # Éviter de créer des multiples Referral si l'utilisateur rafraîchit la page
    referral_id = request.session.get('referral_id')
    referral = None
    
    if referral_id:
        try:
            referral = Referral.objects.get(id=referral_id, referral_code=referral_code)
            referral.visited_at = timezone.now()
            referral.save()
        except Referral.DoesNotExist:
            referral = None

    if not referral:
        referral = Referral.objects.create(
            referrer=ambassador.user,
            referral_code=referral_code,
            status='VISITED',
            visited_at=timezone.now()
        )
        request.session['referral_id'] = referral.id
    
    referrer = ambassador.user
    referrer_profile = None
    try:
        referrer_profile = referrer.teacher_profile
    except TeacherProfile.DoesNotExist:
        pass
        
    context = {
        'referrer': referrer,
        'referrer_profile': referrer_profile,
    }
    
    response = render(request, 'referrals/landing.html', context)
    response.set_cookie('pcv_referral_id', referral.id, max_age=30*24*60*60)
    return response

def cgu_ambassadeurs(request):
    return render(request, 'referrals/cgu_ambassadeur.html')
