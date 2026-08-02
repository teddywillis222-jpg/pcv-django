from abc import ABC, abstractmethod

class PaymentProvider(ABC):
    """
    Interface pour les fournisseurs de paiement de récompenses ambassadeur.
    Permet d'ajouter ultérieurement FedaPay, Kkiapay, etc.
    """
    
    @abstractmethod
    def pay(self, reward):
        """
        Effectue le paiement pour la récompense donnée.
        Doit retourner True si succès, False sinon.
        """
        pass

class ManualPaymentProvider(PaymentProvider):
    """
    Fournisseur de paiement manuel par défaut.
    Nécessite une validation manuelle par l'administrateur.
    """
    
    def pay(self, reward):
        # Dans ce cas, le paiement manuel est validé via l'interface admin.
        # Cette méthode pourrait envoyer un email de rappel à l'admin.
        return True
