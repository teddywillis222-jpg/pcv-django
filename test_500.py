import os
import django
import sys
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# We need a teacher user. We'll pick one that has a TeacherProfile.
from core.models import TeacherProfile, Conversation

# Get conversation 3
conv = Conversation.objects.filter(id=3).first()
if not conv:
    print("Conversation 3 not found.")
    sys.exit(0)

prof_user = conv.professeur.user if conv.professeur else None

if not prof_user:
    print("Conversation 3 has no professor user.")
    sys.exit(0)

# Create a client and force login
c = Client()
c.force_login(prof_user)

try:
    response = c.get('/messagerie/3/')
    print("Status Code:", response.status_code)
    if response.status_code == 500:
        print("500 Error encountered. Traceback might be hidden by test client.")
except Exception as e:
    import traceback
    traceback.print_exc()

