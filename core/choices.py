"""
Choix centralisés pour toute l'application.
Les mêmes option sets sont utilisés partout pour faciliter filtres et formulaires.
"""
from django.core.exceptions import ValidationError
import json
import os
from django.conf import settings


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
        (EXAMENS_NATIONAUX, "Préparation aux examens"),
        (COURS_VACANCES, "Cours de vacances"),
        (SOUTIEN_LANGUES, "Soutien en langues"),
        (METHODOLOGIE_ORGANISATION, "Soutien en méthodologie et organisation"),
        (SCIENTIFIQUE_TECHNIQUE, "Soutien scientifique et technique"),
        (LECTURE_ECRITURE, "Soutien en lecture et écriture"),
    ]
    VALUES = [c[0] for c in CHOICES]


class Matiere:
    """Liste de 100 matières standardisées pour les suggestions."""
    _liste = None

    @classmethod
    def load_liste(cls):
        if cls._liste is not None:
            return cls._liste
        
        filepath = getattr(settings, 'MATIERES_FILE', None)
        if filepath and os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    cls._liste = json.load(f)
                    return cls._liste
            except Exception:
                pass
        
        # Fallback minimal
        return ["Mathématiques", "Français", "Anglais", "Physique", "Chimie", "SVT"]

    @property
    def LISTE(self):
        return self.load_liste()
    
    @classmethod
    def get_choices(cls):
        """Retourne la liste triée par ordre alphabétique pour les Select, incluant les ajouts dynamiques."""
        base_list = set(cls.load_liste())
        try:
            from django.apps import apps
            CustomChoice = apps.get_model('core', 'CustomChoice')
            customs = CustomChoice.objects.filter(category='matiere').values_list('value', flat=True)
            for c in customs:
                base_list.add(c)
        except Exception:
            pass
        sorted_list = sorted(list(base_list))
        return [(m, m) for m in sorted_list]

Matiere.LISTE = Matiere.load_liste()


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

    @classmethod
    def get_choices(cls):
        base_choices = dict(cls.CHOICES)
        try:
            from django.apps import apps
            CustomChoice = apps.get_model('core', 'CustomChoice')
            customs = CustomChoice.objects.filter(category='classe').values_list('value', flat=True)
            for c in customs:
                if c not in base_choices:
                    base_choices[c] = c
        except Exception:
            pass
        return [(k, v) for k, v in base_choices.items()]


# --- Mode de cours (partout : TeacherProfile, Engagement) ---
class CourseMode:
    CHEZ_PARENT = "PARENT_HOME"
    CHEZ_APPRENANT = "APPRENANT_HOME"
    EN_LIGNE = "ONLINE"
    HYBRIDE = "HYBRID"
    LIEU_TIERS = "THIRD_PLACE"
    GROUPE_RESTREINT = "SMALL_GROUP"
    A_DISTANCE = "DISTANCE"

    CHOICES = [
        (CHEZ_PARENT, "Présentiel chez le parent"),
        (CHEZ_APPRENANT, "Présentiel chez l'apprenant"),
        (EN_LIGNE, "En ligne (visioconférence)"),
        (HYBRIDE, "Hybride (Présentiel + En ligne)"),
        (LIEU_TIERS, "Lieu tiers (bibliothèque, centre éducatif)"),
        (GROUPE_RESTREINT, "Cours en groupe restreint"),
        (A_DISTANCE, "À distance (téléphone, audio)"),
    ]
    VALUES = [c[0] for c in CHOICES]


class Localisation:
    _choices = None

    @classmethod
    def load_choices(cls):
        if cls._choices is not None:
            return cls._choices
        
        filepath = getattr(settings, 'LOCALISATIONS_FILE', None)
        if filepath and os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    cls._choices = json.load(f)
                    return cls._choices
            except Exception:
                pass
        
        # Fallback minimal si le fichier est absent
        return [("Cotonou", "Cotonou"), ("Porto-Novo", "Porto-Novo")]

    @property
    def CHOICES(self):
        # Pour compatibilité avec l'accès instance.CHOICES si besoin (rare en Django)
        return self.load_choices()
    
    @classmethod
    def get_choices(cls):
        base_choices = dict(cls.load_choices())
        try:
            from django.apps import apps
            CustomChoice = apps.get_model('core', 'CustomChoice')
            customs = CustomChoice.objects.filter(category='localisation').values_list('value', flat=True)
            for c in customs:
                if c not in base_choices:
                    base_choices[c] = c
        except Exception:
            pass
        return [(k, v) for k, v in base_choices.items()]
    
    # Pour l'accès statique Localisation.CHOICES utilisé dans les modèles/forms
    # On utilise une ruse : redéfinir CHOICES comme une property de classe ou juste appeler load_choices
    # Mais en Django, CHOICES est souvent attendu comme une liste simple à l'importation.
    # On va donc le charger une fois à l'importation du module.
    
Localisation.CHOICES = Localisation.load_choices()
Localisation.VALUES = [c[0] for c in Localisation.CHOICES]


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
    ENGAGEMENT_EN_COURS = "CONFIRME"
    ENGAGEMENT_TERMINE = "TERMINE"
    CONVERSATION_CLOSE = "CLOSE"
    CHOICES = [
        (DISCUSSION_LIBRE, "Discussion libre"),
        (ENGAGEMENT_NEGOCIATION, "Engagement en négociation"),
        (ENGAGEMENT_EN_COURS, "Engagement en cours"),
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
    # --- Anciens statuts (Maintenus pour rétrocompatibilité) ---
    EN_ATTENTE = "EN_ATTENTE"
    CONFIRME = "CONFIRME"
    EN_COURS = "EN_COURS"
    FINALISE = "FINALISE"
    
    # --- Nouveaux statuts ---
    ESSAI_PROGRAMME = "ESSAI_PROGRAMME"
    ESSAI_CONFIRME = "ESSAI_CONFIRME"
    ESSAI_REALISE = "ESSAI_REALISE"
    ENGAGEMENT_FINALISE = "ENGAGEMENT_FINALISE"
    
    # --- Statuts Communs ---
    REFUSE = "REFUSE"
    ANNULE = "ANNULE"
    TERMINE = "TERMINE"
    
    CHOICES = [
        # Anciens
        (EN_ATTENTE, "En attente"),
        (CONFIRME, "En cours"),
        (EN_COURS, "En cours"),
        (FINALISE, "Finalisé"),
        
        # Nouveaux
        (ESSAI_PROGRAMME, "Essai programmé"),
        (ESSAI_CONFIRME, "Essai confirmé"),
        (ESSAI_REALISE, "Essai réalisé"),
        (ENGAGEMENT_FINALISE, "Engagement finalisé"),
        
        # Communs
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
    REMISE_NIVEAU = "REMISE_NIVEAU"
    PREPARER_EXAMEN = "PREPARER_EXAMEN"
    AIDE_DEVOIRS = "AIDE_DEVOIRS"
    METHODOLOGIE = "METHODOLOGIE"
    RENFORCEMENT_MATIERE = "RENFORCEMENT_MATIERE"
    PREPA_CLASSE_SUP = "PREPA_CLASSE_SUP"
    TROUBLES_APPRENTISSAGE = "TROUBLES_APPRENTISSAGE"
    EVEIL_CURIOSITE = "EVEIL_CURIOSITE"
    SUIVI_ABSENCE = "SUIVI_ABSENCE"
    CONCOURS_EXCELLENCE = "CONCOURS_EXCELLENCE"
    AUTRE = "AUTRE"

    CHOICES = [
        (REMISE_NIVEAU, "Remise à niveau globale"),
        (PREPARER_EXAMEN, "Préparation à un examen (CEP, BEPC, etc.)"),
        (AIDE_DEVOIRS, "Aide aux devoirs quotidiens"),
        (METHODOLOGIE, "Amélioration de la méthodologie"),
        (RENFORCEMENT_MATIERE, "Renforcement dans une matière spécifique"),
        (PREPA_CLASSE_SUP, "Préparation à l'entrée dans une classe supérieure"),
        (TROUBLES_APPRENTISSAGE, "Accompagnement pour troubles d'apprentissage (Dys, attention)"),
        (EVEIL_CURIOSITE, "Éveil et curiosité intellectuelle"),
        (SUIVI_ABSENCE, "Suivi durant une absence prolongée"),
        (CONCOURS_EXCELLENCE, "Préparation à un concours d'excellence"),
        (AUTRE, "Autre..."),
    ]
    VALUES = [c[0] for c in CHOICES]


class ObjectifApprenant:
    REUSSITE_UNIV = "REUSSITE_UNIV"
    TEST_CERTIF = "TEST_CERTIF"
    COMPETENCES_PRO = "COMPETENCES_PRO"
    RECONVERSION = "RECONVERSION"
    PERFECTIONNEMENT_LING = "PERFECTIONNEMENT_LING"
    SOUTIEN_MEMOIRE = "SOUTIEN_MEMOIRE"
    OUTILS_NUMERIQUES = "OUTILS_NUMERIQUES"
    CULTURE_GENERALE = "CULTURE_GENERALE"
    CONCOURS_FONCTION_PUBLIQUE = "CONCOURS_FONCTION_PUBLIQUE"
    AUTO_FORMATION = "AUTO_FORMATION"
    AUTRE = "AUTRE"

    CHOICES = [
        (REUSSITE_UNIV, "Réussite aux examens universitaires"),
        (TEST_CERTIF, "Préparation à un test de certification (TOEIC, DELF, etc.)"),
        (COMPETENCES_PRO, "Acquisition de compétences professionnelles"),
        (RECONVERSION, "Reconversion vers un nouveau domaine"),
        (PERFECTIONNEMENT_LING, "Perfectionnement linguistique (Anglais, Français, etc.)"),
        (SOUTIEN_MEMOIRE, "Soutien pour la rédaction d'un mémoire ou thèse"),
        (OUTILS_NUMERIQUES, "Maîtrise d'outils numériques ou logiciels"),
        (CULTURE_GENERALE, "Développement de la culture générale"),
        (CONCOURS_FONCTION_PUBLIQUE, "Préparation aux concours de la fonction publique"),
        (AUTO_FORMATION, "Accompagnement pour une formation en autodidacte"),
        (AUTRE, "Autre..."),
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
    # On autorise désormais les valeurs personnalisées ajoutées par l'utilisateur (Choices.js)


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

class PriceRange:
    @classmethod
    def get_choices(cls):
        currency = getattr(settings, 'DEFAULT_CURRENCY', 'FCFA')
        thresholds = getattr(settings, 'PRICE_THRESHOLDS', ['2000', '5000', '10000'])
        
        return [
            (f"0-{thresholds[0]}", f"Moins de {thresholds[0]} {currency}"),
            (f"{thresholds[0]}-{thresholds[1]}", f"{thresholds[0]} - {thresholds[1]} {currency}"),
            (f"{thresholds[1]}-{thresholds[2]}", f"{thresholds[1]} - {thresholds[2]} {currency}"),
            (f"{thresholds[2]}+", f"Plus de {thresholds[2]} {currency}"),
        ]

PriceRange.CHOICES = PriceRange.get_choices()


# --- Validateurs pour champs liste (JSONField) ---
def validate_modes_cours(value):
    """Liste de valeurs CourseMode."""
    if not isinstance(value, list):
        raise ValidationError("Doit être une liste de modes de cours.")
    # On autorise désormais les valeurs personnalisées ajoutées par l'utilisateur (Choices.js / TomSelect)


def validate_classes_enseignees(value):
    """Liste de valeurs ClassLevel."""
    if not isinstance(value, list):
        raise ValidationError("Doit être une liste de classes.")
    # On autorise désormais les valeurs personnalisées ajoutées par l'utilisateur (Choices.js / TomSelect)
