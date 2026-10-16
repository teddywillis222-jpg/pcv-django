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
    Formate le numéro au format international sans le signe '+' pour SebPay.
    Gère tous les formats du Bénin (8 chiffres historiques, 10 chiffres ARCEP 01..., indicatif 229, +229).
    Retourne un tuple: (format_8_avec_229, format_10_avec_229)
    Exemples:
        '0144582541' -> ('22944582541', '2290144582541')
        '+2290144582541' -> ('22944582541', '2290144582541')
        '97000000' -> ('22997000000', '2290197000000')
    """
    if not phone_number:
        return "", ""
    digits = re.sub(r'\D', '', str(phone_number))
    
    # Nettoyer les répétitions accidentelles d'indicatifs (ex: 229229...)
    while digits.startswith("229") and len(digits) > 13:
        digits = digits[3:]
        
    if digits.startswith("00229"):
        digits = digits[2:]
        
    if digits.startswith("229"):
        local = digits[3:]
    else:
        local = digits
        
    if local.startswith("01") and len(local) == 10:
        local_8 = local[2:]
        local_10 = local
    elif len(local) == 8:
        local_8 = local
        local_10 = "01" + local
    elif local.startswith("0") and len(local) == 9:
        local_8 = local[1:]
        local_10 = "01" + local[1:]
    else:
        local_8 = local[-8:] if len(local) >= 8 else local
        local_10 = ("01" + local_8) if len(local_8) == 8 else local

    format_8 = f"229{local_8}" if len(local_8) == 8 else ""
    format_10 = f"229{local_10}" if len(local_10) == 10 else ""
    
    return format_8, format_10


def detect_benin_operator(phone_number):
    """
    Détecte l'opérateur Mobile Money béninois (mtn, moov, celtiis) selon le préfixe du numéro.
    """
    format_8, _ = clean_phone_for_sebpay(phone_number)
    if not format_8 or len(format_8) < 11:
        return 'mtn'
    num8 = format_8[3:]
    prefix2 = num8[:2]
    if prefix2 in ['40', '41', '47', '48', '49', '92', '93']:
        return 'celtiis'
    if prefix2 in ['43', '44', '45', '55', '58', '60', '63', '64', '65', '68', '94', '95', '98', '99']:
        return 'moov'
    return 'mtn'


def initier_collecte_sebpay(user, engagement, phone, operator=None, callback_url=None):
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

    format_8, format_10 = clean_phone_for_sebpay(phone)
    if not format_8 and not format_10:
        logger.error(f"Numéro Mobile Money invalide: '{phone}'")
        raise ValueError(f"Le numéro '{phone}' n'est pas un numéro valide du Bénin (ex: 01 97 00 00 00 ou 97 00 00 00).")

    detected_op = detect_benin_operator(phone)
    operator_clean = str(operator).lower().strip() if operator else detected_op
    if operator_clean not in ['mtn', 'moov', 'celtiis']:
        operator_clean = detected_op

    # Référence externe unique
    ext_ref = f"PCV-ACC-{engagement.id if engagement else user.id}-{int(time.time())}"

    headers = {
        "X-Public-Key": public_key,
        "X-Secret-Key": secret_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Le format documenté par SebPay est '229' + 8 chiffres (ex: 22997000000)
    phone_to_use = format_8 or format_10

    payload = {
        "amount": int(montant),
        "currency": "XOF",
        "phone": phone_to_use,
        "operator": operator_clean,
        "country": "BJ",
        "external_reference": ext_ref,
    }

    if callback_url:
        payload["callback_url"] = callback_url

    endpoint = f"{api_url.rstrip('/')}/collections"
    logger.info(f"Envoi requête SebPay Collections vers {endpoint} - Réf: {ext_ref}, Tel: {phone_to_use}, Op: {operator_clean}")

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=20)
        response_data = response.json() if response.content else {}

        # Stratégie de robustesse / auto-fallback :
        # Si SebPay rejette avec une erreur liée au format du numéro et qu'on a le format 10 chiffres (22901...):
        if response.status_code in [400, 422] and format_10 and format_10 != phone_to_use:
            err_text = str(response_data.get('message', '')).lower()
            if any(w in err_text for w in ['phone', 'numéro', 'numero', 'format', 'invalide', 'invalid']):
                logger.info(f"Fallback SebPay avec le format 10 chiffres : {format_10}")
                payload["phone"] = format_10
                phone_to_use = format_10
                response = requests.post(endpoint, json=payload, headers=headers, timeout=20)
                response_data = response.json() if response.content else {}

        # Si SebPay signale un opérateur incompatible avec le numéro :
        if response.status_code in [400, 422] and detected_op != operator_clean:
            err_text = str(response_data.get('message', '')).lower()
            if any(w in err_text for w in ['operator', 'opérateur', 'reseau', 'network']):
                logger.info(f"Fallback SebPay avec l'opérateur détecté : {detected_op}")
                payload["operator"] = detected_op
                operator_clean = detected_op
                response = requests.post(endpoint, json=payload, headers=headers, timeout=20)
                response_data = response.json() if response.content else {}

        if response.status_code not in [200, 201]:
            error_msg = response_data.get('message') or response_data.get('error') or f"Erreur code HTTP {response.status_code}"
            logger.error(f"Échec appel SebPay Collections: HTTP {response.status_code} - {response.text}")
            raise Exception(f"Erreur SebPay: {error_msg}")

        # SebPay retourne transaction_id ou data.transaction_id ou id
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
            telephone=phone_to_use,
            operateur=operator_clean,
            statut='pending',
            raw_response=json.dumps(response_data)
        )

        return txn_obj, response_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de communication avec SebPay: {str(e)}", exc_info=True)
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

