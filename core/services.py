import os
import requests
import logging
from django.conf import settings
from .models import TransactionFedaPay, TransactionSebPay
import time
import hmac
import hashlib
import json

logger = logging.getLogger(__name__)

def send_whatsapp_notification(to_number, message_body):
    """
    Envoie un message WhatsApp via l'API Twilio (en utilisant requests pour éviter d'ajouter des dépendances).
    """
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_WHATSAPP_NUMBER')

    if not all([account_sid, auth_token, from_number]):
        logger.error("Configuration Twilio manquante dans l'environnement. (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN ou TWILIO_WHATSAPP_NUMBER)")
        return False

    # Formatage du numéro d'expédition
    if not from_number.startswith('whatsapp:'):
        from_number = f"whatsapp:{from_number}"

    # Nettoyage et formatage du numéro de destination
    raw_number = str(to_number).strip().replace(" ", "").replace("-", "")
    
    # Enlever 'whatsapp:' s'il est déjà là pour faciliter le traitement
    if raw_number.startswith('whatsapp:'):
        raw_number = raw_number[9:]
        
    # S'il ne commence pas par '+' on force le format international
    if not raw_number.startswith('+'):
        # Si ça commence par 0, on le retire
        if raw_number.startswith('0') and not raw_number.startswith('00'):
            raw_number = raw_number[1:]
        
        # Si ça ne commence pas par 229 (l'indicatif du Bénin), on l'ajoute
        if not raw_number.startswith('229'):
            raw_number = f"+229{raw_number}"
        else:
            raw_number = f"+{raw_number}"

    to_number_final = f"whatsapp:{raw_number}"

    logger.info(f"Tentative d'envoi WhatsApp Twilio. Numéro original: {to_number} -> Format final: {to_number_final}")
    print(f"--- TWILIO WHATSAPP : Préparation de l'envoi vers {to_number_final} ---")

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    auth = (account_sid, auth_token)
    
    # Configuration stricte pour Twilio Sandbox (Templates via Content API)
    data = {
        'From': 'whatsapp:+14155238886',  # Numéro Sandbox officiel
        'To': to_number_final,
        'ContentSid': 'HXb5b62575e6e4ff6129ad7c8efe1f983e',
        'ContentVariables': '{"1":"Demande","2":"ProfChezVous"}'
    }

    try:
        response = requests.post(url, data=data, auth=auth, timeout=10)
        if response.status_code not in [200, 201]:
            logger.error(f"Échec de l'envoi WhatsApp Twilio. Code: {response.status_code}, Erreur complète: {response.text}")
            print(f"--- TWILIO ERROR : Code {response.status_code} | Msg: {response.text} ---")
            return False
            
        print(f"--- TWILIO SUCCESS : Message envoyé à {to_number_final} ---")
        return True
    except Exception as e:
        logger.error(f"Exception lors de l'envoi WhatsApp Twilio: {str(e)}")
        print(f"--- TWILIO EXCEPTION : {str(e)} ---")
        return False

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


# ==========================================
# --- INTÉGRATION OFFICIELLE SEBPAY API ---
# ==========================================

def clean_phone_for_sebpay(phone_number):
    """
    Formate le numéro au format international sans le signe '+' pour SebPay (ex: 22901XXXXXXXX).
    """
    if not phone_number:
        return ""
    cleaned = str(phone_number).strip().replace(" ", "").replace("-", "").replace(".", "")
    if cleaned.startswith("+"):
        cleaned = cleaned[1:]
    # Si le numéro commence par 0, on le retire
    if cleaned.startswith("0") and not cleaned.startswith("00"):
        cleaned = cleaned[1:]
    # Si le numéro ne contient pas l'indicatif du Bénin (229), on le préfixe
    if not cleaned.startswith("229") and len(cleaned) in [8, 10]:
        cleaned = f"229{cleaned}"
    return cleaned


def initier_collecte_sebpay(user, engagement, phone, operator, callback_url=None):
    """
    Initie une demande de paiement direct Mobile Money via l'API SebPay Collections.
    Envoie un Push USSD direct sur le téléphone de l'utilisateur.
    """
    public_key = getattr(settings, 'SEBPAY_PUBLIC_KEY', '') or os.environ.get('SEBPAY_PUBLIC_KEY', '')
    secret_key = getattr(settings, 'SEBPAY_SECRET_KEY', '') or os.environ.get('SEBPAY_SECRET_KEY', '')
    api_url = getattr(settings, 'SEBPAY_API_URL', 'https://newapi.sebpay.bj/api/v1')
    montant = getattr(settings, 'SEBPAY_AMOUNT', 30)

    if not public_key or not secret_key:
        logger.error("Clés d'API SebPay manquantes (SEBPAY_PUBLIC_KEY ou SEBPAY_SECRET_KEY).")
        raise ValueError("Les clés d'API SebPay ne sont pas encore configurées sur le serveur.")

    phone_cleaned = clean_phone_for_sebpay(phone)
    if not phone_cleaned or len(phone_cleaned) < 10:
        raise ValueError("Numéro de téléphone Mobile Money invalide.")

    # Opérateur standardisé : mtn, moov, celtiis
    operator_clean = str(operator).lower().strip()
    if operator_clean not in ['mtn', 'moov', 'celtiis']:
        operator_clean = 'mtn'

    # Référence externe unique
    ext_ref = f"PCV-ACC-{engagement.id if engagement else user.id}-{int(time.time())}"

    headers = {
        "X-Public-Key": public_key,
        "X-Secret-Key": secret_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "amount": int(montant),
        "currency": "XOF",
        "phone": phone_cleaned,
        "operator": operator_clean,
        "country": "BJ",
        "external_reference": ext_ref,
    }

    if callback_url:
        payload["callback_url"] = callback_url

    endpoint = f"{api_url.rstrip('/')}/collections"
    logger.info(f"Envoi requête SebPay Collections vers {endpoint} - Réf: {ext_ref}, Tel: {phone_cleaned}, Op: {operator_clean}")

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=20)
        response_data = response.json() if response.content else {}

        if response.status_code not in [200, 201]:
            error_msg = response_data.get('message') or response_data.get('error') or f"Erreur code HTTP {response.status_code}"
            logger.error(f"Échec appel SebPay Collections: {response.status_code} - {response.text}")
            raise Exception(f"Erreur SebPay: {error_msg}")

        # SebPay retourne généralement transaction_id ou data.transaction_id
        txn_id = response_data.get('transaction_id') or response_data.get('data', {}).get('transaction_id')
        if not txn_id:
            txn_id = response_data.get('id')

        # Création de la trace locale en base de données
        txn_obj = TransactionSebPay.objects.create(
            user=user,
            engagement=engagement,
            transaction_id=str(txn_id) if txn_id else None,
            external_reference=ext_ref,
            montant=montant,
            telephone=phone_cleaned,
            operateur=operator_clean,
            statut='pending',
            raw_response=json.dumps(response_data)
        )

        return txn_obj, response_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de communication avec SebPay: {str(e)}")
        raise Exception(f"Impossible de joindre le serveur de paiement SebPay: {str(e)}")


def verifier_statut_sebpay(transaction_id):
    """
    Interroge l'API SebPay pour vérifier le statut actuel d'une transaction.
    """
    public_key = getattr(settings, 'SEBPAY_PUBLIC_KEY', '') or os.environ.get('SEBPAY_PUBLIC_KEY', '')
    secret_key = getattr(settings, 'SEBPAY_SECRET_KEY', '') or os.environ.get('SEBPAY_SECRET_KEY', '')
    api_url = getattr(settings, 'SEBPAY_API_URL', 'https://newapi.sebpay.bj/api/v1')

    if not public_key or not secret_key:
        return None

    headers = {
        "X-Public-Key": public_key,
        "X-Secret-Key": secret_key,
        "Accept": "application/json"
    }

    endpoint = f"{api_url.rstrip('/')}/collections/{transaction_id}"
    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('status') or data.get('data', {}).get('status')
    except Exception as e:
        logger.warning(f"Erreur lors de la vérification de statut SebPay: {e}")
    return None


def verifier_signature_webhook_sebpay(request_body, received_signature):
    """
    Vérifie l'authenticité d'un webhook SebPay via HMAC-SHA256.
    """
    secret_key = getattr(settings, 'SEBPAY_SECRET_KEY', '') or os.environ.get('SEBPAY_SECRET_KEY', '')
    if not secret_key or not received_signature:
        return False

    computed = hmac.new(secret_key.encode('utf-8'), request_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed.lower(), received_signature.lower())

