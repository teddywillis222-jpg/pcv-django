import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
import json

User = get_user_model()
user, created = User.objects.get_or_create(username='testapprenant', defaults={'password': 'password123'})
if created:
    user.set_password('password123')
    user.save()

c = Client(HTTP_HOST='127.0.0.1')
c.login(username='testapprenant', password='password123')

try:
    response = c.post('/api/professeur/1/toggle-reaction/', data=json.dumps({'section': 'presentation'}), content_type='application/json')
    print('Status:', response.status_code)
    content = response.content.decode()
    print('Response:', content)
except Exception as e:
    import traceback
    traceback.print_exc()
