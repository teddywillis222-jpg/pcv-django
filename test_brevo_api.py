import os
import django
import sys

# Configure django
sys.path.append(r"c:\Users\JGA'TIC BENIN\Documents\ProfChezVous")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import send_mail
from anymail.exceptions import AnymailAPIError

try:
    print("Tentative d'envoi d'un email de test via Brevo API...")
    send_mail(
        "Test Brevo API",
        "Ceci est un test pour voir si l'API fonctionne.",
        "Prof Chez Vous <contact@profchezvousapp.com>",
        ["teddywillis222@gmail.com"],
        fail_silently=False,
    )
    print("Succès ! L'email est parti.")
except AnymailAPIError as e:
    print(f"Erreur API Anymail: {e}")
    if e.response:
        print(f"Status Code: {e.response.status_code}")
        print(f"Détails: {e.response.text}")
except Exception as e:
    print(f"Autre erreur: {e}")
