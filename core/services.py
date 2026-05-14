import os
import fedapay
from django.conf import settings
from .models import TransactionFedaPay

# Configuration de l'environnement (sandbox par défaut)
fedapay.environment = os.environ.get('FEDAPAY_ENVIRONMENT', 'sandbox')
fedapay.api_key = os.environ.get('FEDAPAY_SECRET_KEY', '') # Par sécurité, mettez une valeur par défaut vide

def initier_paiement_engagement(engagement, user, callback_url):
    """
    Initialise une transaction FedaPay pour payer les frais d'engagement de 2000 FCFA.
    Retourne l'URL de paiement générée par FedaPay.
    """
    if not fedapay.api_key:
        raise ValueError("La clé API FedaPay (FEDAPAY_SECRET_KEY) n'est pas configurée dans l'environnement.")

    montant = 2000

    try:
        # Création de la transaction chez FedaPay
        transaction = fedapay.Transaction.create(
            amount=montant,
            currency={'iso': 'XOF'},
            callback_url=callback_url,
            description=f"Frais d'engagement Prof Chez Vous (#{engagement.id})",
            customer={
                'firstname': user.first_name or "Parent",
                'lastname': user.last_name or "PCV",
                'email': user.email or f"user_{user.id}@profchezvous.com",
            }
        )
        
        # Génération du token pour obtenir l'URL de paiement
        token = transaction.generate_token()
        payment_url = token.url

        # Enregistrement de la trace comptable dans la base de données
        TransactionFedaPay.objects.create(
            engagement=engagement,
            transaction_id=str(transaction.id),
            montant=montant,
            statut='pending'
        )

        return payment_url

    except Exception as e:
        raise Exception(f"Erreur lors de l'initialisation de la transaction FedaPay : {str(e)}")
