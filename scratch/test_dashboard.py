import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import TeacherProfile, Apprenant, Profile
from core.views import apprenant_dashboard
from django.test import RequestFactory

# Find any user with learner profile, or create one if none exists
apprenant_user = User.objects.filter(profile__role='apprenant').first()
if not apprenant_user:
    print("No learner user found, looking for any user...")
    apprenant_user = User.objects.first()

if apprenant_user:
    print(f"Testing with user: {apprenant_user.username}")
    # Ensure profile and apprenant profile exist
    profile, _ = Profile.objects.get_or_create(user=apprenant_user, defaults={'role': 'apprenant'})
    profile.role = 'apprenant'
    profile.save()
    
    apprenant, _ = Apprenant.objects.get_or_create(
        user=apprenant_user,
        defaults={'nom': 'Test Learner', 'classe': '6EME'}
    )
    
    factory = RequestFactory()
    request = factory.get('/apprenant/dashboard/')
    request.user = apprenant_user
    
    try:
        response = apprenant_dashboard(request)
        print("Success! Dashboard rendered without FieldError.")
    except Exception as e:
        import traceback
        print("Error encountered:")
        traceback.print_exc()
else:
    print("No users exist in the database.")
