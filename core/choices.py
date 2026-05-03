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
    VALUES = [c[0] for c in CHOICES]


class Matiere:
    """Liste de 100 matières standardisées pour les suggestions."""
    LISTE = [
        "Allemand", "Anglais", "Arts Plastiques", "Biologie", "Chimie",
        "Communication Écrite", "Communication Orale", "Dessin",
        "Éducation Civique (ECM)", "Éducation Musicale",
        "Éducation Physique et Sportive (EPS)", "Espagnol", "Français",
        "Géographie", "Histoire", "Informatique", "Initiation à la Technologie",
        "Italien", "Lecture", "Mathématiques", "Philosophie", "Physique",
        "Rédaction", "Sciences de la Vie et de la Terre (SVT)",
        "Agronomie", "Anatomie", "Architecture", "Bureautique",
        "Comptabilité Analytique", "Comptabilité Générale",
        "Construction Mécanique", "Coupe-Couture", "Dessin Technique",
        "Droit Civil", "Droit Constitutionnel", "Droit des Affaires",
        "Économie Générale", "Électricité", "Électronique", "Entrepreneuriat",
        "Fiscalité", "Génie Civil", "Gestion de Projets",
        "Gestion des Ressources Humaines", "Hôtellerie et Restauration",
        "Hydraulique", "Maçonnerie", "Maintenance Informatique",
        "Marketing et Communication", "Mécanique Automobile", "Menuiserie",
        "Organisation du Travail Administratif (OTA)", "Santé et Nutrition",
        "Secrétariat", "Statistiques", "Topographie", "Tourisme",
        "Algèbre", "Analyse Mathématique", "Biochimie", "Biotechnologie",
        "Cryptographie", "Économétrie", "Électromagnétisme", "Épistémologie",
        "Finances Publiques", "Géologie", "Intelligence Artificielle",
        "Linguistique", "Macroéconomie", "Mécanique des Fluides",
        "Microéconomie", "Neurosciences", "Pétrochimie",
        "Psychologie de l'Éducation", "Réseaux et Télécoms",
        "Sciences de l'Éducation", "Sociologie", "Thermodynamique",
        "Alphabétisation (Langues Nationales)", "Art Oratoire",
        "Chinois (Mandarin)", "Coiffure et Esthétique", "Cuisine et Pâtisserie",
        "Développement Mobile (Flutter/React Native)",
        "Développement Web (HTML/CSS/JS)", "Échecs", "Éducation Financière",
        "Entrepreneuriat Agricole", "Infographie (Photoshop/Illustrator)",
        "Leadership et Soft Skills", "Maintenance de Panneaux Solaires",
        "Montage Vidéo", "Musique (Guitare)", "Musique (Piano)",
        "No-Code (Bubble/Adalo)", "Photographie", "Programmation Python",
        "Rédaction Web / SEO", "Yoga et Bien-être"
    ]
    
    @classmethod
    def get_choices(cls):
        """Retourne la liste triée par ordre alphabétique pour les Select."""
        sorted_list = sorted(cls.LISTE)
        return [(m, m) for m in sorted_list]


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
    CHOICES = [
        ("Abokicodji - Cotonou", "Abokicodji - Cotonou"),
        ("Adidogomé - Abomey-Calavi", "Adidogomé - Abomey-Calavi"),
        ("Adjagbo - Abomey-Calavi", "Adjagbo - Abomey-Calavi"),
        ("Adjamé - Cotonou", "Adjamé - Cotonou"),
        ("Adjégounlè - Porto-Novo", "Adjégounlè - Porto-Novo"),
        ("Adogéta - Porto-Novo", "Adogéta - Porto-Novo"),
        ("Agblangandan - Sèmè-Kpodji", "Agblangandan - Sèmè-Kpodji"),
        ("Agla - Cotonou", "Agla - Cotonou"),
        ("Agontikon - Cotonou", "Agontikon - Cotonou"),
        ("Agori - Abomey-Calavi", "Agori - Abomey-Calavi"),
        ("Agouako - Abomey-Calavi", "Agouako - Abomey-Calavi"),
        ("Ahogbohouè - Cotonou", "Ahogbohouè - Cotonou"),
        ("Aidjèdo - Cotonou", "Aidjèdo - Cotonou"),
        ("Akassato - Abomey-Calavi", "Akassato - Abomey-Calavi"),
        ("Akpakpa - Cotonou", "Akpakpa - Cotonou"),
        ("Akron - Porto-Novo", "Akron - Porto-Novo"),
        ("Alaga - Parakou", "Alaga - Parakou"),
        ("Albarika - Parakou", "Albarika - Parakou"),
        ("Amanwignon - Parakou", "Amanwignon - Parakou"),
        ("Atchakpa - Porto-Novo", "Atchakpa - Porto-Novo"),
        ("Atrokpocodji - Abomey-Calavi", "Atrokpocodji - Abomey-Calavi"),
        ("Avakpa - Porto-Novo", "Avakpa - Porto-Novo"),
        ("Avotrou - Cotonou", "Avotrou - Cotonou"),
        ("Awansouri - Cotonou", "Awansouri - Cotonou"),
        ("Ayélawadjè - Cotonou", "Ayélawadjè - Cotonou"),
        ("Bakinkoura - Parakou", "Bakinkoura - Parakou"),
        ("Banikanni - Parakou", "Banikanni - Parakou"),
        ("Bidossessi - Abomey-Calavi", "Bidossessi - Abomey-Calavi"),
        ("Cadjèhoun - Cotonou", "Cadjèhoun - Cotonou"),
        ("Camp Adagbé - Porto-Novo", "Camp Adagbé - Porto-Novo"),
        ("Cocotomey - Abomey-Calavi", "Cocotomey - Abomey-Calavi"),
        ("Dandji - Cotonou", "Dandji - Cotonou"),
        ("Davatin - Porto-Novo", "Davatin - Porto-Novo"),
        ("Dépôt - Parakou", "Dépôt - Parakou"),
        ("Djassin - Porto-Novo", "Djassin - Porto-Novo"),
        ("Djidjè - Cotonou", "Djidjè - Cotonou"),
        ("Djifa-Prix - Cotonou", "Djifa-Prix - Cotonou"),
        ("Djougou-Kpota - Djougou", "Djougou-Kpota - Djougou"),
        ("Dokparou - Parakou", "Dokparou - Parakou"),
        ("Donaten - Cotonou", "Donaten - Cotonou"),
        ("Dowa - Porto-Novo", "Dowa - Porto-Novo"),
        ("Enagnon - Cotonou", "Enagnon - Cotonou"),
        ("Fidjrossè - Cotonou", "Fidjrossè - Cotonou"),
        ("Fonkpame - Porto-Novo", "Fonkpame - Porto-Novo"),
        ("Ganhoto - Porto-Novo", "Ganhoto - Porto-Novo"),
        ("Ganhi - Cotonou", "Ganhi - Cotonou"),
        ("Gbèdjromèdé - Cotonou", "Gbèdjromèdé - Cotonou"),
        ("Gbégamey - Cotonou", "Gbégamey - Cotonou"),
        ("Gbégnigan - Cotonou", "Gbégnigan - Cotonou"),
        ("Gbodjé - Abomey-Calavi", "Gbodjé - Abomey-Calavi"),
        ("Glo-Djigbé - Abomey-Calavi", "Glo-Djigbé - Abomey-Calavi"),
        ("Godomey - Abomey-Calavi", "Godomey - Abomey-Calavi"),
        ("Gorobani - Parakou", "Gorobani - Parakou"),
        ("Guéma - Parakou", "Guéma - Parakou"),
        ("Haie Vive - Cotonou", "Haie Vive - Cotonou"),
        ("Hindé - Cotonou", "Hindé - Cotonou"),
        ("Hogbonou - Porto-Novo", "Hogbonou - Porto-Novo"),
        ("Houéyiho - Cotonou", "Houéyiho - Cotonou"),
        ("Houézoumè - Cotonou", "Houézoumè - Cotonou"),
        ("Houinmè - Porto-Novo", "Houinmè - Porto-Novo"),
        ("Hounsa - Porto-Novo", "Hounsa - Porto-Novo"),
        ("Jéricho - Cotonou", "Jéricho - Cotonou"),
        ("Kadébou - Parakou", "Kadébou - Parakou"),
        ("Kindonou - Cotonou", "Kindonou - Cotonou"),
        ("Komè - Porto-Novo", "Komè - Porto-Novo"),
        ("Kouhounou - Cotonou", "Kouhounou - Cotonou"),
        ("Kpébié - Parakou", "Kpébié - Parakou"),
        ("Kpékpédji - Abomey-Calavi", "Kpékpédji - Abomey-Calavi"),
        ("Kpondehou - Cotonou", "Kpondehou - Cotonou"),
        ("Ladji - Cotonou", "Ladji - Cotonou"),
        ("Ladjifarani - Parakou", "Ladjifarani - Parakou"),
        ("Les Cocotiers - Cotonou", "Les Cocotiers - Cotonou"),
        ("Lobozounkpa - Abomey-Calavi", "Lobozounkpa - Abomey-Calavi"),
        ("Madina - Parakou", "Madina - Parakou"),
        ("Maria-Gléta - Abomey-Calavi", "Maria-Gléta - Abomey-Calavi"),
        ("Maro-Militaire - Cotonou", "Maro-Militaire - Cotonou"),
        ("Menontin - Cotonou", "Menontin - Cotonou"),
        ("Missébo - Cotonou", "Missébo - Cotonou"),
        ("Missessin - Cotonou", "Missessin - Cotonou"),
        ("Missité - Cotonou", "Missité - Cotonou"),
        ("Moumouni - Parakou", "Moumouni - Parakou"),
        ("Nato - Cotonou", "Nato - Cotonou"),
        ("Okpè-Oyouré - Porto-Novo", "Okpè-Oyouré - Porto-Novo"),
        ("Ouando - Porto-Novo", "Ouando - Porto-Novo"),
        ("Ouinmeko - Porto-Novo", "Ouinmeko - Porto-Novo"),
        ("Padonou - Abomey-Calavi", "Padonou - Abomey-Calavi"),
        ("Parana - Parakou", "Parana - Parakou"),
        ("Placodji - Cotonou", "Placodji - Cotonou"),
        ("Saint Hubert - Cotonou", "Saint Hubert - Cotonou"),
        ("Sainte Rita - Cotonou", "Sainte Rita - Cotonou"),
        ("Segbeya - Cotonou", "Segbeya - Cotonou"),
        ("Sodohomè - Bohicon", "Sodohomè - Bohicon"),
        ("Somankpon - Abomey-Calavi", "Somankpon - Abomey-Calavi"),
        ("Tankpè - Abomey-Calavi", "Tankpè - Abomey-Calavi"),
        ("Titirou - Parakou", "Titirou - Parakou"),
        ("Togoudo - Abomey-Calavi", "Togoudo - Abomey-Calavi"),
        ("Tokpa-Hoho - Cotonou", "Tokpa-Hoho - Cotonou"),
        ("Vedoko - Cotonou", "Vedoko - Cotonou"),
        ("Wonkoro - Parakou", "Wonkoro - Parakou"),
        ("Zogbo - Cotonou", "Zogbo - Cotonou"),
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
    EN_ATTENTE = "EN_ATTENTE"
    CONFIRME = "CONFIRME"
    EN_COURS = "EN_COURS"
    FINALISE = "FINALISE"
    REFUSE = "REFUSE"
    ANNULE = "ANNULE"
    TERMINE = "TERMINE"
    CHOICES = [
        (EN_ATTENTE, "En attente"),
        (CONFIRME, "En cours"),
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
