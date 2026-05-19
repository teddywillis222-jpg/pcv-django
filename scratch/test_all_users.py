import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import TeacherProfile, Apprenant, Profile
from core.views import apprenant_dashboard
from django.test import RequestFactory

# Find all users, check if any user triggers the issue
for user in User.objects.all():
    # Make them learner
    profile, _ = Profile.objects.get_or_create(user=user, defaults={'role': 'apprenant'})
    profile.role = 'apprenant'
    profile.save()
    
    apprenant, _ = Apprenant.objects.get_or_create(
        user=user,
        defaults={'nom': user.username, 'classe': '6EME'}
    )
    
    factory = RequestFactory()
    request = factory.get('/apprenant/dashboard/')
    request.user = user
    
    try:
        response = apprenant_dashboard(request)
        print(f"User {user.username} success!")
    except Exception as e:
        print(f"User {user.username} FAILED:")
        import traceback
        traceback.print_exc()
