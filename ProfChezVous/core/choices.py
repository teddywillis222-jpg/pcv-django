"""
Choix centralisés pour toute l'application.
Les mêmes option sets sont utilisés partout pour faciliter filtres et formulaires.
"""
from django.core.exceptions import ValidationError


# --- Profil & compte ---
class TypeAbonnement:
    STANDARD = "STANDARD"
    ACCESS_PREMIUM = "ACCESS_PREMIUM"
    CHOICES = [
        (STANDARD, "Standard"),
        (ACCESS_PREMIUM, "Access+Premium"),
    ]


class ParentAccountStatus:
    ACTIF = "ACTIF"
    SUSPENDU = "SUSPENDU"
    INACTIF = "INACTIF"
    CHOICES = [
        (ACTIF, "Actif"),
        (SUSPENDU, "Suspendu"),
        (INACTIF, "Inactif"),
    ]


# --- Soutien & matière ---
class SupportCategory:
    SOUTIEN_SCOLAIRE = "ACADEMIC"
    EXAMENS_NATIONAUX = "EXAMS"
    COURS_VACANCES = "HOLIDAYS"
    SOUTIEN_LANGUES = "LANGUAGES"
    METHODOLOGIE_ORGANISATION = "METHODO"
    SCIENTIFIQUE_TECHNIQUE = "SCI_TECH"
    LECTURE_ECRITURE = "LITERACY"
    CHOICES = [
        (SOUTIEN_SCOLAIRE, "Soutien scolaire académique"),
        (EXAMENS_NATIONAUX, "Préparation aux examens nationaux"),
        (COURS_VACANCES, "Cours de vacances"),
        (SOUTIEN_LANGUES, "Soutien en langues"),
        (METHODOLOGIE_ORGANISATION, "Soutien en méthodologie et organisation"),
        (SCIENTIFIQUE_TECHNIQUE, "Soutien scientifique et technique"),
        (LECTURE_ECRITURE, "Soutien en lecture et écriture"),
    ]


# --- Classe / niveau (partout : Enfant, Engagement, TeacherProfile) ---
class ClassLevel:
    CI = "CI"
    CP = "CP"
    CE1 = "CE1"
    CE2 = "CE2"
    CM1 = "CM1"
    CM2 = "CM2"
    SIXIEME = "6EME"
    CINQUIEME = "5EME"
    QUATRIEME = "4EME"
    TROISIEME = "3EME"
    SECONDE = "2NDE"
    PREMIERE = "1ERE"
    TERMINALE = "TLE"
    CAP1 = "CAP1"
    CAP2 = "CAP2"
    BEP1 = "BEP1"
    BEP2 = "BEP2"
    BACPRO1 = "BACPRO1"
    BACPRO_TLE = "BACPRO_TLE"
    BTS1 = "BTS1"
    BTS2 = "BTS2"
    LICENCE1 = "L1"
    LICENCE2 = "L2"
    LICENCE3 = "L3"
    MASTER = "MASTER"
    DOCTORAT = "PHD"
    CHOICES = [
        (CI, "CI"),
        (CP, "CP"),
        (CE1, "CE1"),
        (CE2, "CE2"),
        (CM1, "CM1"),
        (CM2, "CM2"),
        (SIXIEME, "6ème"),
        (CINQUIEME, "5ème"),
        (QUATRIEME, "4ème"),
        (TROISIEME, "3ème"),
        (SECONDE, "2nde"),
        (PREMIERE, "1ère"),
        (TERMINALE, "Tle"),
        (CAP1, "1ère année CAP"),
        (CAP2, "2ème année CAP"),
        (BEP1, "1ère année BEP"),
        (BEP2, "2ème année BEP"),
        (BACPRO1, "1ère année BAC Pro"),
        (BACPRO_TLE, "Tle BAC Pro"),
        (BTS1, "1ère année BTS"),
        (BTS2, "2ème année BTS"),
        (LICENCE1, "Licence 1"),
        (LICENCE2, "Licence 2"),
        (LICENCE3, "Licence 3"),
        (MASTER, "Master"),
        (DOCTORAT, "Doctorat"),
    ]
    VALUES = [c[0] for c in CHOICES]


# --- Mode de cours (partout : TeacherProfile, Engagement) ---
class CourseMode:
    CHEZ_PARENT = "PARENT_HOME"
    CHEZ_APPRENANT = "APPRENANT_HOME"
    EN_LIGNE = "ONLINE"
    HYBRIDE = "HYBRID"
    CHOICES = [
        (CHEZ_PARENT, "Présentiel chez le parent"),
        (CHEZ_APPRENANT, "Présentiel chez l'apprenant"),
        (EN_LIGNE, "En ligne"),
        (HYBRIDE, "Hybride (presentiel + en ligne par visioconférence)"),
    ]
    VALUES = [c[0] for c in CHOICES]


# --- Validation prof ---
class ValidationStatus:
    EN_ATTENTE = "PENDING"
    VALIDE = "APPROVED"
    REFUSE = "REJECTED"
    SUSPENDU = "SUSPENDED"
    INCOMPLET = "INCOMPLETE"
    CHOICES = [
        (EN_ATTENTE, "En attente"),
        (VALIDE, "Validé"),
        (REFUSE, "Refusé"),
        (SUSPENDU, "Suspendu"),
        (INCOMPLET, "Incomplet"),
    ]


# --- Conversation ---
class ConversationStatus:
    DISCUSSION_LIBRE = "DISCUSSION_LIBRE"
    ENGAGEMENT_NEGOCIATION = "NEGOCIATION"
    ENGAGEMENT_CONFIRME = "CONFIRME"
    ENGAGEMENT_TERMINE = "TERMINE"
    CONVERSATION_CLOSE = "CLOSE"
    CHOICES = [
        (DISCUSSION_LIBRE, "Discussion libre"),
        (ENGAGEMENT_NEGOCIATION, "Engagement en négociation"),
        (ENGAGEMENT_CONFIRME, "Engagement confirmé"),
        (ENGAGEMENT_TERMINE, "Engagement terminé"),
        (CONVERSATION_CLOSE, "Conversation close"),
    ]


# --- Engagement ---
class EngagementType:
    ESSAI = "ESSAI"
    NORMAL = "NORMAL"
    CHOICES = [(ESSAI, "Essai"), (NORMAL, "Normal")]


class StatutEssai:
    PROGRAMME = "PROGRAMME"
    CONFIRME = "CONFIRME"
    COMPLETE = "COMPLETE"
    CHOICES = [
        (PROGRAMME, "Programmé"),
        (CONFIRME, "Confirmé"),
        (COMPLETE, "Complété"),
    ]


class StatutGeneral:
    EN_ATTENTE = "EN_ATTENTE"
    CONFIRME = "CONFIRME"
    EN_COURS = "EN_COURS"
    FINALISE = "FINALISE"
    REFUSE = "REFUSE"
    ANNULE = "ANNULE"
    TERMINE = "TERMINE"
    CHOICES = [
        (EN_ATTENTE, "En attente"),
        (CONFIRME, "Confirmé"),
        (EN_COURS, "En cours"),
        (FINALISE, "Finalisé"),
        (REFUSE, "Refusé"),
        (ANNULE, "Annulé"),
        (TERMINE, "Terminé"),
    ]


class DureeSeance:
    UNE_HEURE = "1H"
    HEURE_30 = "1H30"
    DEUX_HEURES = "2H"
    DEUX_HEURES_30 = "2H30"
    TROIS_HEURES = "3H"
    CHOICES = [
        (UNE_HEURE, "1h"),
        (HEURE_30, "1h30"),
        (DEUX_HEURES, "2h"),
        (DEUX_HEURES_30, "2h30"),
        (TROIS_HEURES, "3h"),
    ]


class FrequenceHebdomadaire:
    UNE = "1"
    DEUX = "2"
    TROIS = "3"
    QUATRE = "4"
    CINQ = "5"
    CHOICES = [
        (UNE, "1 séance/semaine"),
        (DEUX, "2 séances/semaine"),
        (TROIS, "3 séances/semaine"),
        (QUATRE, "4 séances/semaine"),
        (CINQ, "5 séances/semaine"),
    ]


class PeriodeEngagement:
    UN_MOIS = "1_MOIS"
    TROIS_MOIS = "3_MOIS"
    SIX_MOIS = "6_MOIS"
    UN_AN = "1_AN"
    PONCTUEL = "PONCTUEL"
    CHOICES = [
        (UN_MOIS, "1 mois"),
        (TROIS_MOIS, "3 mois"),
        (SIX_MOIS, "6 mois"),
        (UN_AN, "1 an"),
        (PONCTUEL, "Ponctuel"),
    ]


# --- Enfant ---
class Sexe:
    MASCULIN = "M"
    FEMININ = "F"
    CHOICES = [
        (MASCULIN, "Masculin"),
        (FEMININ, "Féminin"),
    ]


class NiveauScolaire:
    PRIMAIRE = "PRIMAIRE"
    COLLEGE = "COLLEGE"
    LYCEE = "LYCEE"
    TECHNIQUE = "TECHNIQUE"
    SUPERIEUR = "SUPERIEUR"
    AUTRE = "AUTRE"
    CHOICES = [
        (PRIMAIRE, "Primaire"),
        (COLLEGE, "Collège"),
        (LYCEE, "Lycée"),
        (TECHNIQUE, "Technique"),
        (SUPERIEUR, "Supérieur"),
        (AUTRE, "Autre"),
    ]


class NiveauPercu:
    FAIBLE = "FAIBLE"
    MOYEN = "MOYEN"
    BON_IRREGULIER = "BON_IRREGULIER"
    EXCELLENT = "EXCELLENT"
    CHOICES = [
        (FAIBLE, "Faible"),
        (MOYEN, "Moyen"),
        (BON_IRREGULIER, "Bon mais irrégulier"),
        (EXCELLENT, "Excellent"),
    ]


class BesoinPrioritaire:
    REMISE_NIVEAU = "REMISE_NIVEAU"
    PERFECTIONNEMENT = "PERFECTIONNEMENT"
    PREPARATION_EXAMENS = "PREPARATION_EXAMENS"
    SOUTIEN_REGULIER = "SOUTIEN_REGULIER"
    METHODO_ORGANISATION = "METHODO"
    CHOICES = [
        (REMISE_NIVEAU, "Remise à niveau"),
        (PERFECTIONNEMENT, "Perfectionnement"),
        (PREPARATION_EXAMENS, "Préparation aux examens"),
        (SOUTIEN_REGULIER, "Soutien régulier"),
        (METHODO_ORGANISATION, "Méthodologie et organisation"),
    ]


def validate_matieres_max_5(value):
    """Liste de matières, maximum 5."""
    if not isinstance(value, list):
        raise ValidationError("Doit être une liste de matières.")
    if len(value) > 5:
        raise ValidationError("Maximum 5 matières autorisées.")


# --- Apprenant ---
class ObjectifMotivation:
    PREPARER_EXAMEN = "PREPARER_EXAMEN"
    AMELIORER_NOTES = "AMELIORER_NOTES"
    REMISE_NIVEAU = "REMISE_NIVEAU"
    PERFECTIONNEMENT = "PERFECTIONNEMENT"
    METHODO_ORGANISATION = "METHODO"
    CHOICES = [
        (PREPARER_EXAMEN, "Préparer un examen"),
        (AMELIORER_NOTES, "Améliorer mes notes"),
        (REMISE_NIVEAU, "Remise à niveau"),
        (PERFECTIONNEMENT, "Perfectionnement"),
        (METHODO_ORGANISATION, "Méthodologie et organisation"),
    ]
    VALUES = [c[0] for c in CHOICES]


class CreneauDisponibilite:
    LUNDI_VENDREDI_MATIN = "LUN_VEN_MATIN"
    LUNDI_VENDREDI_APRES_MIDI = "LUN_VEN_APRES_MIDI"
    LUNDI_VENDREDI_SOIR = "LUN_VEN_SOIR"
    MERCREDI_APRES_MIDI = "MER_APRES_MIDI"
    SAMEDI_MATIN = "SAM_MATIN"
    SAMEDI_APRES_MIDI = "SAM_APRES_MIDI"
    DIMANCHE = "DIMANCHE"
    CHOICES = [
        (LUNDI_VENDREDI_MATIN, "Lundi – Vendredi (Matin)"),
        (LUNDI_VENDREDI_APRES_MIDI, "Lundi – Vendredi (Après-midi)"),
        (LUNDI_VENDREDI_SOIR, "Lundi – Vendredi (Soir)"),
        (MERCREDI_APRES_MIDI, "Mercredi après-midi"),
        (SAMEDI_MATIN, "Samedi (Matin)"),
        (SAMEDI_APRES_MIDI, "Samedi (Après-midi)"),
        (DIMANCHE, "Dimanche"),
    ]
    VALUES = [c[0] for c in CHOICES]


def validate_objectifs_motivations(value):
    """Liste de valeurs ObjectifMotivation."""
    if not isinstance(value, list):
        raise ValidationError("Doit être une liste.")
    valid = set(ObjectifMotivation.VALUES)
    for v in value:
        if v not in valid:
            raise ValidationError(f"Objectif invalide : {v}")


def validate_creneaux_disponibilites(value):
    """Liste de valeurs CreneauDisponibilite."""
    if not isinstance(value, list):
        raise ValidationError("Doit être une liste de créneaux.")
    valid = set(CreneauDisponibilite.VALUES)
    for v in value:
        if v not in valid:
            raise ValidationError(f"Creneau invalide : {v}")


def validate_matieres_recherchees_max_5(value):
    """Liste de matières recherchées, maximum 5."""
    if not isinstance(value, list):
        raise ValidationError("Doit être une liste de matières.")
    if len(value) > 5:
        raise ValidationError("Maximum 5 matières autorisées.")


# --- Message ---
class MessageType:
    TEXTE = "TEXTE"
    IMAGE = "IMAGE"
    DOCUMENT = "DOCUMENT"
    SYSTEME = "SYSTEME"
    CHOICES = [
        (TEXTE, "Texte"),
        (IMAGE, "Image"),
        (DOCUMENT, "Document"),
        (SYSTEME, "Système"),
    ]


# --- Validateurs pour champs liste (JSONField) ---
def validate_modes_cours(value):
    """Liste de valeurs CourseMode."""
    if not isinstance(value, list):
        raise ValidationError("Doit être une liste de modes de cours.")
    valid = set(CourseMode.VALUES)
    for v in value:
        if v not in valid:
            raise ValidationError(f"Mode de cours invalide : {v}. Valeurs autorisées : {list(valid)}")


def validate_classes_enseignees(value):
    """Liste de valeurs ClassLevel."""
    if not isinstance(value, list):
        raise ValidationError("Doit être une liste de classes.")
    valid = set(ClassLevel.VALUES)
    for v in value:
        if v not in valid:
            raise ValidationError(f"Classe invalide : {v}. Valeurs autorisées : {list(valid)}")
