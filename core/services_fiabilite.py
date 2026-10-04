from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from .models import OperationScoreFiabilite, TeacherProfile
import logging

logger = logging.getLogger(__name__)

def _attribuer_points(professeur, type_operation, points, reference_type, reference_id, description=""):
    """
    Fonction générique pour attribuer des points de fiabilité de manière sécurisée et atomique.
    """
    reference_id_str = str(reference_id)
    
    with transaction.atomic():
        # Vérifier si l'opération existe déjà
        existe = OperationScoreFiabilite.objects.filter(
            professeur=professeur,
            type_operation=type_operation,
            reference_type=reference_type,
            reference_id=reference_id_str
        ).exists()
        
        if existe:
            logger.info(f"Opération {type_operation} pour {reference_type} {reference_id} déjà enregistrée pour {professeur.id}.")
            return False
            
        # Créer l'opération
        OperationScoreFiabilite.objects.create(
            professeur=professeur,
            type_operation=type_operation,
            points=points,
            reference_type=reference_type,
            reference_id=reference_id_str,
            description=description,
            statut='VALIDE'
        )
        
        # Mettre à jour le compteur global du professeur (safe update)
        professeur.score_fiabilite = OperationScoreFiabilite.objects.filter(
            professeur=professeur, 
            statut='VALIDE'
        ).aggregate(
            total=Sum('points')
        )['total'] or 0
        
        professeur.date_dernier_calcul_score = timezone.now()
        professeur.save(update_fields=['score_fiabilite', 'date_dernier_calcul_score'])
        
        return True

def attribuer_points_journal(seance):
    """ +5 points par journal valide """
    professeur = seance.engagement.professeur
    return _attribuer_points(
        professeur=professeur,
        type_operation='JOURNAL',
        points=5,
        reference_type='Seance',
        reference_id=seance.id,
        description=f"Journal de séance renseigné pour l'engagement {seance.engagement.id}"
    )

def attribuer_points_reactivite(engagement, date_reponse):
    """ 0 à +5 points selon la réactivité """
    delai = date_reponse - engagement.date_creation
    minutes = delai.total_seconds() / 60
    
    if minutes <= 30:
        points = 5
    elif minutes <= 60:
        points = 2
    elif minutes <= 120:
        points = 1
    else:
        points = 0
        
    return _attribuer_points(
        professeur=engagement.professeur,
        type_operation='REACTIVITE',
        points=points,
        reference_type='Engagement',
        reference_id=engagement.id,
        description=f"Réponse en {int(minutes)} minutes"
    )

def attribuer_points_engagement_termine(engagement):
    """ +20 points par engagement achevé """
    return _attribuer_points(
        professeur=engagement.professeur,
        type_operation='ENGAGEMENT_TERMINE',
        points=20,
        reference_type='Engagement',
        reference_id=engagement.id,
        description="Collaboration menée à terme"
    )

def attribuer_points_avis(avis):
    """ 0 à +15 points selon la note """
    if avis.note == 5:
        points = 15
    elif avis.note == 4:
        points = 10
    elif avis.note == 3:
        points = 5
    else:
        points = 0
        
    return _attribuer_points(
        professeur=avis.professeur,
        type_operation='AVIS',
        points=points,
        reference_type='Avis',
        reference_id=avis.id,
        description=f"Avis {avis.note} étoiles reçu"
    )
