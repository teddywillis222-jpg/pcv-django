import os
import requests
from django.conf import settings
from .models import TransactionFedaPay

def initier_paiement_engagement(engagement, user, callback_url):
    """
    Initialise une transaction FedaPay pour payer les frais d'engagement de 2000 FCFA
    en utilisant l'API REST directe (car la librairie python 'fedapay' de PyPI est incomplète).
    """
    api_key = os.environ.get('FEDAPAY_SECRET_KEY', '')
    env = os.environ.get('FEDAPAY_ENVIRONMENT', 'sandbox')

    if not api_key:
        raise ValueError("La clé API FedaPay (FEDAPAY_SECRET_KEY) n'est pas configurée dans l'environnement.")

    base_url = "https://sandbox-api.fedapay.com/v1" if env == 'sandbox' else "https://api.fedapay.com/v1"
    montant = 2000

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "description": f"Frais d'engagement Prof Chez Vous (#{engagement.id})",
        "amount": montant,
        "currency": {"iso": "XOF"},
        "callback_url": callback_url,
        "customer": {
            "firstname": user.first_name or "Parent",
            "lastname": user.last_name or "PCV",
            "email": user.email or f"user_{user.id}@profchezvous.com"
        }
    }

    try:
        # 1. Créer la transaction
        response = requests.post(f"{base_url}/transactions", json=payload, headers=headers)
        response_data = response.json()

        if response.status_code not in [200, 201]:
            error_msg = response_data.get('message', 'Erreur inconnue')
            raise Exception(f"Erreur API FedaPay: {error_msg}")

        transaction_data = response_data.get('v1/transaction', response_data.get('transaction', {}))
        transaction_id = transaction_data.get('id')

        # 2. Générer le token de paiement
        token_response = requests.post(f"{base_url}/transactions/{transaction_id}/token", headers=headers)
        token_data = token_response.json()

        if token_response.status_code not in [200, 201]:
            raise Exception("Impossible de générer le token de paiement FedaPay.")

        payment_url = token_data.get('url', token_data.get('v1/token', {}).get('url'))
        if not payment_url:
            payment_url = token_data.get('token', {}).get('url')

        if not payment_url:
            raise Exception("L'URL de paiement n'a pas été retournée par FedaPay.")

        # 3. Enregistrement en base de données locale
        TransactionFedaPay.objects.create(
            engagement=engagement,
            transaction_id=str(transaction_id),
            montant=montant,
            statut='pending'
        )

        return payment_url

    except requests.exceptions.RequestException as e:
        raise Exception(f"Erreur de connexion à FedaPay : {str(e)}")

def initier_paiement_abonnement(user, callback_url):
    """
    Initialise une transaction FedaPay pour souscrire à l'abonnement Access+ Premium.
    """
    api_key = os.environ.get('FEDAPAY_SECRET_KEY', '')
    env = os.environ.get('FEDAPAY_ENVIRONMENT', 'sandbox')

    if not api_key:
        raise ValueError("La clé API FedaPay (FEDAPAY_SECRET_KEY) n'est pas configurée dans l'environnement.")

    base_url = "https://sandbox-api.fedapay.com/v1" if env == 'sandbox' else "https://api.fedapay.com/v1"
    
    # Prix depuis les settings, conversion en entier
    montant = int(settings.PREMIUM_MONTHLY_PRICE)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "description": f"Abonnement Access+ Premium pour {user.first_name or user.username}",
        "amount": montant,
        "currency": {"iso": "XOF"},
        "callback_url": callback_url,
        "customer": {
            "firstname": user.first_name or "Utilisateur",
            "lastname": user.last_name or "PCV",
            "email": user.email or f"user_{user.id}@profchezvous.com"
        }
    }

    try:
        # 1. Créer la transaction
        response = requests.post(f"{base_url}/transactions", json=payload, headers=headers)
        response_data = response.json()

        if response.status_code not in [200, 201]:
            error_msg = response_data.get('message', 'Erreur inconnue')
            raise Exception(f"Erreur API FedaPay: {error_msg}")

        transaction_data = response_data.get('v1/transaction', response_data.get('transaction', {}))
        transaction_id = transaction_data.get('id')

        # 2. Générer le token de paiement
        token_response = requests.post(f"{base_url}/transactions/{transaction_id}/token", headers=headers)
        token_data = token_response.json()

        if token_response.status_code not in [200, 201]:
            raise Exception("Impossible de générer le token de paiement FedaPay.")

        payment_url = token_data.get('url', token_data.get('v1/token', {}).get('url'))
        if not payment_url:
            payment_url = token_data.get('token', {}).get('url')

        if not payment_url:
            raise Exception("L'URL de paiement n'a pas été retournée par FedaPay.")

        # 3. Enregistrement en base de données locale
        TransactionFedaPay.objects.create(
            user=user,
            type_transaction='ABONNEMENT',
            transaction_id=str(transaction_id),
            montant=montant,
            statut='pending'
        )

        return payment_url

    except requests.exceptions.RequestException as e:
        raise Exception(f"Erreur de connexion à FedaPay : {str(e)}")
