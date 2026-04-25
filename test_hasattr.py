import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
from core.models import Parent

u = User.objects.create(username="test_no_parent")
try:
    has_parent = hasattr(u, "parent")
    print("hasattr worked:", has_parent)
except Exception as e:
    print("hasattr crashed with:", type(e).__name__)
    
u.delete()
