from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.db import models
from django.utils import timezone
from django.conf import settings

from .choices import (
    BesoinPrioritaire,
    TypeAbonnement,
    ClassLevel,
    ConversationStatus,
    CourseMode,
    CreneauDisponibilite,
    DureeSeance,
    EngagementType,
    FrequenceHebdomadaire,
    MessageType,
    Matiere,
    Localisation,
    NiveauPercu,
    NiveauScolaire,
    ObjectifMotivation,
    ParentAccountStatus,
    PeriodeEngagement,
    Sexe,
    StatutEssai,
    StatutGeneral,
    SupportCategory,
    ValidationStatus,
    validate_classes_enseignees,
    validate_creneaux_disponibilites,
    validate_matieres_max_5,
    validate_matieres_recherchees_max_5,
    validate_modes_cours,
    validate_objectifs_motivations,
)


def clean_subjects(subjects):
    """
    Nettoie une liste de matiÃ¨res ou une chaÃ®ne de caractÃ¨res.
    Applique .strip() et garantit l'unicitÃ© (insensible Ã  la casse).
    """
    if not subjects:
        return subjects

    if isinstance(subjects, str):
        # Pour les chaÃ®nes (ex: "Maths, Physique")
        parts = [s.strip() for s in subjects.split(',')]
        cleaned = []
        seen = set()
        for p in parts:
            if p and p.lower() not in seen:
                cleaned.append(p)
                seen.add(p.lower())
        return ", ".join(cleaned)

    if isinstance(subjects, list):
        cleaned = []
        seen = set()
        for s in subjects:
            if not isinstance(s, str):
                cleaned.append(s)
                continue
            s_strip = s.strip()
            if s_strip and s_strip.lower() not in seen:
                cleaned.append(s_strip)
                seen.add(s_strip.lower())
        return cleaned

    return subjects


class Profile(models.Model):
    ROLE_PARENT = "PARENT"
    ROLE_PROF = "PROF"
    ROLE_APPRENANT = "APPRENANT"

    ROLE_CHOICES = [
        (ROLE_PARENT, "Parent"),
        (ROLE_PROF, "Professeur"),
        (ROLE_APPRENANT, "Apprenant"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
    )
    telephone = models.CharField(max_length=50, blank=True)
    a_vu_popup_bienvenue = models.BooleanField(
        default=False,
        help_text="DÃ©termine si le popup de bienvenue (Apprenant/Parent) a dÃ©jÃ  Ã©tÃ© fermÃ©."
    )
    
    # Statistiques avancÃ©es (Lancement)
    nb_vues_page_plan = models.IntegerField(default=0, help_text="Intention d'achat : Vues de la page GÃ©rer mon plan")
    nb_vues_suivi = models.IntegerField(default=0, help_text="IntÃ©rÃªt suivi : Vues de la page de suivi pÃ©dagogique")
    nb_connexions = models.IntegerField(default=0, help_text="RÃ©currence d'utilisation")

    @property
    def current_plan(self):
        """Retourne le code du plan d'abonnement actuel."""
        from django.utils import timezone
        latest = self.user.abonnements.order_by('-id').first()
        if latest:
            if latest.type_abonnement == 'ACCESS_PREMIUM' and latest.date_fin and latest.date_fin < timezone.now().date():
                from .choices import TypeAbonnement
                from .models import Abonnement
                # CrÃ©er un abonnement standard suite Ã  l'expiration
                Abonnement.objects.create(
                    user=self.user,
                    type_abonnement=TypeAbonnement.STANDARD,
                    date_debut=timezone.now().date()
                )
                return TypeAbonnement.STANDARD
            return latest.type_abonnement
        return "STANDARD"

    @property
    def current_plan_label(self):
        """Retourne le label lisible du plan d'abonnement actuel."""
        from .choices import TypeAbonnement
        plan = self.current_plan
        for code, label in TypeAbonnement.CHOICES:
            if code == plan:
                return label
        return "Standard"

    def __str__(self):
        return f"{self.user.username} ({self.role})"


import random

def generate_otp():
    """GÃ©nÃ¨re un code OTP alÃ©atoire Ã  6 chiffres."""
    return str(random.randint(100000, 999999))


class PhoneVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='phone_verification')
    phone_number = models.CharField(max_length=50)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        """Renvoie True si le code a plus de 10 minutes ou a expirÃ©."""
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"OTP pour {self.phone_number} (VÃ©rifiÃ©: {self.is_verified})"


class ParentDetails(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="parent_details",
    )
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"DÃ©tails parent {self.user.username}"


class Parent(models.Model):
    # C. Lien avec lâ€™utilisateur (obligatoire)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="parent",
    )

    # A. Identification & contact
    nom = models.CharField(max_length=150)
    numero_whatsapp = models.CharField(max_length=50)
    profession = models.CharField(max_length=150, blank=True)
    quartier_ville = models.CharField(
        max_length=150,
        choices=Localisation.CHOICES,
        blank=True
    )
    photo_profil = models.ImageField(
        upload_to="parents/photos/",
        blank=True,
        null=True,
    )

    # D. Statut du compte
    statut_compte = models.CharField(
        max_length=20,
        choices=ParentAccountStatus.CHOICES,
        default=ParentAccountStatus.ACTIF,
    )

    # E. Champs optionnels
    email = models.EmailField(blank=True)
    est_verifie = models.BooleanField(default=False)
    
    # F. Statistiques de lancement
    nb_recherches = models.PositiveIntegerField(default=0)
    nb_profils_consultes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Parent {self.nom}"


class Enfant(models.Model):
    # 1. IdentitÃ© et liens systÃ¨me
    parent = models.ForeignKey(
        Parent,
        on_delete=models.CASCADE,
        related_name="enfants",
    )
    prenom = models.CharField(max_length=150)
    sexe = models.CharField(
        max_length=5,
        choices=Sexe.CHOICES,
        blank=True,
    )
    date_de_naissance = models.DateField(null=True, blank=True)
    etablissement_scolaire = models.CharField(max_length=200, blank=True)

    # 2. Profil acadÃ©mique et besoins
    niveau_scolaire = models.CharField(
        max_length=20,
        choices=NiveauScolaire.CHOICES,
        blank=True,
    )
    classe = models.CharField(
        max_length=30,
        choices=ClassLevel.CHOICES,
        blank=True,
    )
    matieres = models.JSONField(
        default=list,
        blank=True,
        validators=[validate_matieres_max_5],
        help_text="MatiÃ¨res nÃ©cessitant un accompagnement (max 5)",
    )
    niveau_percu = models.CharField(
        max_length=20,
        choices=NiveauPercu.CHOICES,
        blank=True,
    )
    besoin_prioritaire = models.CharField(
        max_length=20,
        choices=BesoinPrioritaire.CHOICES,
        blank=True,
    )
    objectif_principal = models.TextField(blank=True)

    # 3. Logistique et localisation
    quartier_ville = models.CharField(
        max_length=150,
        choices=Localisation.CHOICES,
        blank=True,
        help_text="Format Â« Quartier - Ville Â» pour matching avec professeurs",
    )
    mode_de_cours = models.CharField(
        max_length=30,
        choices=CourseMode.CHOICES,
        blank=True,
    )

    def save(self, *args, **kwargs):
        self.matieres = clean_subjects(self.matieres)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prenom} ({self.parent.nom})"

    @property
    def age(self):
        """Ã‚ge calculÃ© Ã  partir de date_de_naissance."""
        if not self.date_de_naissance:
            return None
        from datetime import date

        today = date.today()
        return (
            today.year
            - self.date_de_naissance.year
            - ((today.month, today.day) < (self.date_de_naissance.month, self.date_de_naissance.day))
        )




def get_default_abonnement_price():
    return f"{settings.DEFAULT_ENGAGEMENT_PRICE}{settings.DEFAULT_CURRENCY} par engagement"

class Abonnement(models.Model):
    """Contrat d'abonnement, crÃ©Ã© automatiquement Ã  l'inscription."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="abonnements",
        null=True,
        blank=True,
    )
    type_abonnement = models.CharField(
        max_length=30,
        choices=TypeAbonnement.CHOICES,
        default=TypeAbonnement.STANDARD,
    )
    prix = models.CharField(
        max_length=100,
        default=get_default_abonnement_price,
    )
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Abonnement {self.type_abonnement} â€” {self.user.username}"


class Apprenant(models.Model):
    # 1. IdentitÃ© et liens systÃ¨me
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="apprenant",
    )
    nom = models.CharField(max_length=200, help_text="Nom et prÃ©nom")
    email_apprenant = models.EmailField(blank=True)
    telephone = models.CharField(max_length=50, blank=True, help_text="NumÃ©ro WhatsApp")
    photo_de_profil = models.ImageField(
        upload_to="apprenants/photos/",
        blank=True,
        null=True,
    )
    abonnement_lie = models.ForeignKey(
        "Abonnement",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="apprenants",
    )
    derniere_mise_a_jour = models.DateTimeField(auto_now=True)
    
    # Statistiques avancÃ©es (Lancement)
    nb_recherches = models.IntegerField(default=0, help_text="Nombre de recherches effectuÃ©es")
    nb_profils_consultes = models.IntegerField(default=0, help_text="Nombre de profils professeurs consultÃ©s")

    # 2. Parcours et besoins acadÃ©miques
    niveau = models.CharField(
        max_length=20,
        choices=NiveauScolaire.CHOICES,
        blank=True,
    )
    classe = models.CharField(
        max_length=30,
        choices=ClassLevel.CHOICES,
        blank=True,
    )
    matieres_recherchees = models.JSONField(
        default=list,
        blank=True,
        validators=[validate_matieres_recherchees_max_5],
        help_text="MatiÃ¨res prioritaires (max 5)",
    )
    objectifs_motivations = models.JSONField(
        default=list,
        blank=True,
        validators=[validate_objectifs_motivations],
        help_text="Liste de codes ObjectifMotivation (ex: ['PREPARER_EXAMEN'])",
    )
    description_difficultes = models.TextField(blank=True)
    habitudes_de_travail = models.TextField(blank=True)

    # 3. Logistique et localisation
    quartier_ville = models.CharField(
        max_length=150,
        choices=Localisation.CHOICES,
        blank=True,
        help_text="Format Â« Quartier - Ville Â» pour matching",
    )
    preference_de_cours = models.CharField(
        max_length=30,
        choices=CourseMode.CHOICES,
        blank=True,
    )
    disponibilites = models.JSONField(
        default=list,
        blank=True,
        validators=[validate_creneaux_disponibilites],
        help_text="Liste de codes CreneauDisponibilite (ex: ['LUN_VEN_MATIN'])",
    )

    def save(self, *args, **kwargs):
        self.matieres_recherchees = clean_subjects(self.matieres_recherchees)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Apprenant {self.nom}"


class Disponibilite(models.Model):
    jour = models.CharField(max_length=20)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

    def __str__(self):
        return f"{self.jour} {self.heure_debut}-{self.heure_fin}"


class Diplome(models.Model):
    teacher = models.ForeignKey("TeacherProfile", on_delete=models.CASCADE, related_name="diplomes", null=True, blank=True)
    nom_diplome = models.CharField(max_length=255, default="Inconnu")
    fichier_preuve = models.FileField(upload_to="diplomes/", blank=True, null=True)
    date_upload = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.nom_diplome


class VueProfil(models.Model):
    professeur_vise = models.ForeignKey(
        "TeacherProfile",
        on_delete=models.CASCADE,
        related_name="vues",
        null=True,
        blank=True,
    )
    visiteur_utilisateur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vues_profils",
    )
    visiteur_id_technique = models.CharField(max_length=255, blank=True)
    date_consultation = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Vue de profil"
        verbose_name_plural = "Vues de profil"

    def __str__(self):
        return f"Vue de {self.professeur_vise} le {self.date_consultation}"


class Evaluation(models.Model):
    """Une seule Ã©valuation par (parent_Ã©valuateur, professeur_Ã©valuÃ©). UPSERT en cas de mise Ã  jour."""

    professeur_evalue = models.ForeignKey(
        "TeacherProfile",
        on_delete=models.CASCADE,
        related_name="evaluations_recues",
        null=True,
        blank=True,
    )
    parent_evaluateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="evaluations_donnees",
        null=True,
        blank=True,
    )
    engagement_lie = models.OneToOneField(
        "Engagement",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evaluation_liee",
    )
    note = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Note sur 5",
    )
    commentaire = models.TextField(blank=True)
    date_evaluation = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["parent_evaluateur", "professeur_evalue"],
                name="unique_eval_parent_prof",
            )
        ]
        verbose_name = "Ã‰valuation"
        verbose_name_plural = "Ã‰valuations"

    def __str__(self):
        return f"Ã‰valuation {self.note}/5 â€” {self.professeur_evalue}"


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
    )

    # 1. Informations de base
    email = models.EmailField()
    prenom = models.CharField(max_length=150)
    nom = models.CharField(max_length=150)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    telephone_whatsapp = models.CharField(max_length=50)

    # 2. PrÃ©sentation et mÃ©thodologie
    photo_de_profil = models.ImageField(
        upload_to="teachers/profile_photos/",
        blank=True,
        null=True,
    )
    presentation = models.TextField(blank=True)
    methodologie = models.TextField(blank=True)
    video_presentation = models.URLField(blank=True, null=True, help_text="Lien YouTube ou TikTok de prÃ©sentation")
    annees_d_experience = models.PositiveIntegerField(default=0)
    categories_de_soutien = models.JSONField(
        default=list,
        blank=True,
        help_text="Liste de codes SupportCategory",
    )

    # 3. CompÃ©tences et modalitÃ©s
    matiere_enseignee = models.CharField(max_length=150)
    classes_enseignees = models.JSONField(
        default=list,
        blank=True,
        validators=[validate_classes_enseignees],
        help_text="Liste de codes ClassLevel (ex: ['6EME','5EME'])",
    )
    modes_de_cours = models.JSONField(
        default=list,
        blank=True,
        validators=[validate_modes_cours],
        help_text="Liste de codes CourseMode (ex: ['ONLINE','HYBRID'])",
    )
    ville_quartier = models.CharField(
        max_length=150,
        choices=Localisation.CHOICES,
        help_text="Format Â« Quartier - Ville Â»"
    )
    disponibilites = models.ManyToManyField(
        Disponibilite,
        blank=True,
        related_name="teachers",
    )
    grille_disponibilites = models.JSONField(default=list, blank=True)
    message_admin = models.TextField(blank=True)

    # 4. Documents et vÃ©rification
    fichier_cni = models.FileField(
        upload_to="teachers/cni/",
        blank=True,
        null=True,
    )
    liste_certifications_texte = models.TextField(blank=True)
    
    # 5. Statistiques de lancement
    nb_vues_profil = models.PositiveIntegerField(default=0)
    statut_de_validation = models.CharField(
        max_length=20,
        choices=ValidationStatus.CHOICES,
        default=ValidationStatus.EN_ATTENTE,
    )
    est_certifie = models.BooleanField(default=False)
    profil_complet = models.BooleanField(default=False, help_text="Vrai si le profil est complÃ©tÃ© Ã  100%")

    # 5. Tarification et offres
    tarif_horaire = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    essai_gratuit_actif = models.BooleanField(default=False)

    # 6. Statistiques et visibilitÃ©
    nb_vues_jour = models.PositiveIntegerField(default=0)
    nb_vues_semaine = models.PositiveIntegerField(default=0)
    nb_vues_mois = models.PositiveIntegerField(default=0)
    nb_vues_total = models.PositiveIntegerField(default=0)
    nombre_apparitions_recherche = models.PositiveIntegerField(default=0)
    nombre_apparitions_mois = models.PositiveIntegerField(default=0)
    # evaluations_recues : relation inverse depuis Evaluation.professeur_evalue
    nb_engagements_confirmes = models.PositiveIntegerField(default=0)
    nb_engagements_finalises = models.PositiveIntegerField(default=0)
    nb_engagements_termines = models.PositiveIntegerField(default=0)
    nb_engagements_total = models.PositiveIntegerField(default=0)
    note_initiale_equipe = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=settings.RATING_DEFAULT_STANDARD, 
        help_text="Note attribuÃ©e par l'Ã©quipe Ã  la validation"
    )
    temps_moyen_reponse = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Temps de rÃ©ponse moyen en minutes"
    )

    parents_favoris = models.ManyToManyField(
        User,
        blank=True,
        related_name="professeurs_favoris",
        help_text="Liste des parents marquÃ©s comme favoris par ce professeur"
    )

    @property
    def video_embed_url(self):
        """Retourne l'URL d'intÃ©gration (embed) pour la vidÃ©o de prÃ©sentation (YouTube ou TikTok)."""
        import re
        if not self.video_presentation:
            return None
        url = self.video_presentation
        # YouTube
        if 'youtube.com' in url or 'youtu.be' in url:
            match = re.search(r'(?:v=|/v/|/embed/|youtu\.be/)([^&?/]+)', url)
            if match:
                video_id = match.group(1)
                return f"https://www.youtube.com/embed/{video_id}"
        # TikTok
        elif 'tiktok.com' in url:
            match = re.search(r'/video/(\d+)', url)
            if match:
                video_id = match.group(1)
                return f"https://www.tiktok.com/embed/v2/{video_id}"
        return None

    @property
    def completion_percentage(self):
        """Calcule le pourcentage de complÃ©tion du profil professeur."""
        fields_to_check = [
            'photo_de_profil', 'presentation', 'methodologie', 
            'annees_d_experience', 'classes_enseignees', 'modes_de_cours',
            'ville_quartier', 'tarif_horaire', 'telephone_whatsapp'
        ]
        filled = 0
        for field in fields_to_check:
            val = getattr(self, field)
            if val:
                if isinstance(val, (list, dict)) and not val:
                    continue
                filled += 1
        
        # On ajoute des points pour les diplÃ´mes
        if self.diplomes.exists():
            filled += 1
            
        return int((filled / (len(fields_to_check) + 1)) * 100)

    @property
    def classes_labels(self):
        """Retourne les labels des classes enseignÃ©es sous forme de chaÃ®ne."""
        if not self.classes_enseignees:
            return ""
        from .choices import ClassLevel
        choices_dict = dict(ClassLevel.CHOICES)
        return ", ".join([choices_dict.get(c, c) for c in self.classes_enseignees])

    @property
    def categories_labels(self):
        """Retourne les labels des catÃ©gories de soutien sous forme de chaÃ®ne."""
        if not self.categories_de_soutien:
            return ""
        from .choices import SupportCategory
        choices_dict = dict(SupportCategory.CHOICES)
        return ", ".join([choices_dict.get(c, c) for c in self.categories_de_soutien])

    # 7. ParamÃ¨tres et consentement
    autorisation_publicitaire = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(f"{self.prenom} {self.nom} {self.matiere_enseignee} {self.ville_quartier}")
            if not base_slug:
                base_slug = "professeur"
            slug = base_slug
            counter = 1
            while TeacherProfile.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        self.matiere_enseignee = clean_subjects(self.matiere_enseignee)
        super().save(*args, **kwargs)
        
        # Mise Ã  jour du boolÃ©en profil_complet (post-save pour autoriser l'accÃ¨s aux relations ManyToMany si existantes)
        try:
            is_complete = (self.completion_percentage == 100)
            if self.profil_complet != is_complete:
                TeacherProfile.objects.filter(pk=self.pk).update(profil_complet=is_complete)
        except ValueError:
            pass

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('professeur_detail', kwargs={'teacher_slug': self.slug})

    def __str__(self):
        return f"Professeur {self.prenom} {self.nom}"


class Conversation(models.Model):
    # 1. IdentitÃ© et participants
    participants = models.ManyToManyField(
        User,
        related_name="conversations",
    )
    professeur = models.ForeignKey(
        "TeacherProfile",
        on_delete=models.CASCADE,
        related_name="conversations",
        null=True,
        blank=True,
    )
    parent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="conversations_parent",
        null=True,
        blank=True,
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    dernier_message_date = models.DateTimeField(null=True, blank=True)

    # 2. Contenu et lien avec les messages
    dernier_message_texte = models.TextField(blank=True)
    dernier_message_auteur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dernier_messages",
    )

    # 3. Engagement
    engagement_actif = models.OneToOneField(
        "Engagement",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversation_active",
    )
    statut_conversation = models.CharField(
        max_length=30,
        choices=ConversationStatus.CHOICES,
        default=ConversationStatus.DISCUSSION_LIBRE,
    )

    # 4. MÃ©tadonnÃ©es & UX
    conversation_lue_par_parent = models.BooleanField(default=False)
    conversation_lue_par_prof = models.BooleanField(default=False)
    conversation_archivee = models.BooleanField(default=False) # Legacy field
    archivee_par = models.ManyToManyField(User, related_name='conversations_archivees', blank=True)
    masquee_par = models.ManyToManyField(User, related_name='conversations_masquees', blank=True)

    def __str__(self):
        return f"Conversation #{self.id}"


class Engagement(models.Model):
    # 1. Acteurs et liens de base
    conversation = models.ForeignKey(
        "Conversation",
        on_delete=models.CASCADE,
        related_name="engagements",
        null=True,
        blank=True,
    )
    type_engagement = models.CharField(
        max_length=20,
        choices=EngagementType.CHOICES,
        default=EngagementType.NORMAL,
    )
    professeur = models.ForeignKey(
        "TeacherProfile",
        on_delete=models.CASCADE,
        related_name="engagements",
        null=True,
        blank=True,
    )
    parent_apprenant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="engagements_client",
        null=True,
        blank=True,
    )
    enfants_concernes = models.ManyToManyField(
        "Enfant",
        related_name="engagements",
        blank=True,
    )
    matiere = models.CharField(max_length=150, blank=True)
    classe = models.CharField(
        max_length=30,
        choices=ClassLevel.CHOICES,
        blank=True,
    )
    duree_mois = models.IntegerField(
        null=True,
        blank=True,
        help_text="DurÃ©e souhaitÃ©e en mois"
    )

    # 2. Logistique et localisation
    mode_de_cours = models.CharField(
        max_length=30,
        choices=CourseMode.CHOICES,
        blank=True,
    )
    localisation_option = models.CharField(
        max_length=150,
        blank=True,
        help_text="Format Â« Quartier-Ville Â»",
    )
    indications_geographiques = models.TextField(
        blank=True,
        help_text="Indications pour trouver la maison (pour les cours Ã  domicile)",
    )
    plateforme_visio_preferee = models.CharField(max_length=100, blank=True)
    duree_seance = models.CharField(
        max_length=10,
        choices=DureeSeance.CHOICES,
        blank=True,
    )
    frequence_hebdomadaire = models.CharField(
        max_length=5,
        choices=FrequenceHebdomadaire.CHOICES,
        blank=True,
    )
    budget_convenu = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    periode_engagement = models.CharField(
        max_length=20,
        choices=PeriodeEngagement.CHOICES,
        blank=True,
    )

    # 3. Gestion du cours d'essai
    date_heure_essai = models.DateTimeField(null=True, blank=True)
    lien_cours_essai = models.URLField(max_length=500, blank=True)
    statut_essai = models.CharField(
        max_length=20,
        choices=StatutEssai.CHOICES,
        null=True,
        blank=True,
    )
    description_essai = models.TextField(blank=True)
    date_heure_fin_essai = models.DateTimeField(null=True, blank=True)

    masque_par_parent = models.BooleanField(
        default=False,
        help_text="Si vrai, l'engagement n'est plus visible dans l'espace parent."
    )

    # 4. Ã‰tats et flux de contrÃ´le
    statut_general = models.CharField(
        max_length=20,
        choices=StatutGeneral.CHOICES,
        default=StatutGeneral.ESSAI_PROGRAMME,
    )

    # NÃ©gociation / Budget
    tarif_horaire_propose = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    paiement_effectue = models.BooleanField(default=False)
    vu_par_professeur = models.BooleanField(default=False)

    # 5. Horodatages
    date_creation = models.DateTimeField(auto_now_add=True)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    date_confirmation = models.DateTimeField(null=True, blank=True)
    date_finalisation = models.DateTimeField(null=True, blank=True)
    date_refus = models.DateTimeField(null=True, blank=True)
    date_cloture = models.DateTimeField(null=True, blank=True)
    temps_reponse_prof = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Temps (en minutes) mis par le prof pour confirmer",
    )
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    # 6. SÃ©curitÃ© et actions bilatÃ©rales
    annulation_initiee_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="annulations_initiees",
    )
    annulation_confirmee = models.BooleanField(default=False)
    cloture_initiee_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clotures_initiees",
    )
    cloture_confirmee = models.BooleanField(default=False)
    masque_pour_professeur = models.BooleanField(default=False)
    masque_pour_parent = models.BooleanField(default=False)

    # 7. Suivi et qualitÃ© (journal_sÃ©ance_liÃ© = Liste_SÃ©ances via engagement.seances)
    # evaluation_liee : relation inverse depuis Evaluation.engagement_lie

    # 8. Suivi global matiÃ¨re (ajouts)
    total_points_obtenus_matiere = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    total_points_max_matiere = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    taux_global_matiere = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    @property
    def essai_status_label(self):
        from .choices import EngagementType, StatutGeneral
        from django.utils import timezone
        # Retrait de la restriction type_engagement pour s'adapter au nouveau flux
            
        if self.statut_general in [StatutGeneral.REFUSE, StatutGeneral.ANNULE]:
            return self.get_statut_general_display()
            
        if self.statut_general in [StatutGeneral.EN_ATTENTE, StatutGeneral.ESSAI_PROGRAMME]:
            return "ProgrammÃ©"
            
        if self.statut_general in [StatutGeneral.CONFIRME, StatutGeneral.EN_COURS, StatutGeneral.FINALISE, StatutGeneral.TERMINE, StatutGeneral.ESSAI_CONFIRME, StatutGeneral.ESSAI_REALISE, StatutGeneral.ENGAGEMENT_FINALISE]:
            if (self.date_heure_fin_essai and self.date_heure_fin_essai < timezone.now()) or self.statut_general in [StatutGeneral.ESSAI_REALISE, StatutGeneral.ENGAGEMENT_FINALISE]:
                return "ComplÃ©tÃ©e"
            return "ConfirmÃ©"
            
        return "ProgrammÃ©"

    def save(self, *args, **kwargs):
        self.matiere = clean_subjects(self.matiere)
        
        # SÃ©curitÃ© anti-contournement: Masquer les numÃ©ros de tÃ©lÃ©phone dans les indications
        if self.indications_geographiques:
            import re
            # Regex agressive : dÃ©tecte toute suite d'au moins 8 chiffres sÃ©parÃ©s Ã©ventuellement par des espaces, points ou tirets,
            # avec ou sans indicatif (+229, 00229).
            phone_regex = r'(?:(?:\+|00)?229[\s\.\-]*)?(?:\d[\s\.\-]*){8,}'
            self.indications_geographiques = re.sub(phone_regex, '[NumÃ©ro masquÃ© par sÃ©curitÃ©]', self.indications_geographiques)
            
        super().save(*args, **kwargs)

    def check_and_update_essai_status(self):
        """Met Ã  jour le statut de l'essai Ã  ESSAI_REALISE si la date de dÃ©but + 45 min est dÃ©passÃ©e."""
        from django.utils import timezone
        import datetime
        from core.choices import StatutGeneral, EngagementType
        
        if self.type_engagement == EngagementType.ESSAI and self.statut_general == StatutGeneral.ESSAI_CONFIRME:
            if self.date_heure_essai:
                dt_fin = self.date_heure_essai + datetime.timedelta(minutes=45)
                if timezone.now() >= dt_fin:
                    self.statut_general = StatutGeneral.ESSAI_REALISE
                    self.save(update_fields=['statut_general'])
                    return True
        return False

    def __str__(self):
        return f"Engagement #{self.id} - {self.professeur} / {self.parent_apprenant} - {self.statut_general}"


class Seance(models.Model):
    engagement = models.ForeignKey(
        "Engagement",
        on_delete=models.CASCADE,
        related_name="seances",
    )
    date_seance = models.DateField()
    objectifs = models.TextField()
    difficultes_presentes = models.BooleanField()
    difficultes_rencontrees = models.TextField(blank=True)
    taches_domicile = models.TextField(blank=True)
    total_points_obtenus = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )
    total_points_max = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )
    taux_maitrise_seance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    mois_index = models.DateField(
        null=True,
        blank=True,
        help_text="Premier jour du mois (pour filtrage)",
    )
    creee_le = models.DateTimeField(auto_now_add=True)
    validee = models.BooleanField(default=False)

    def __str__(self):
        return f"SÃ©ance #{self.id} (eng. {self.engagement_id})"


class NotionSeance(models.Model):
    seance = models.ForeignKey(
        "Seance",
        on_delete=models.CASCADE,
        related_name="notions",
    )
    nom_notion = models.CharField(max_length=255)
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="Score de 0 Ã  3",
    )

    def __str__(self):
        return f"{self.nom_notion} ({self.seance})"


class Message(models.Model):
    # 1. RÃ©fÃ©rences
    conversation = models.ForeignKey(
        "Conversation",
        on_delete=models.CASCADE,
        related_name="messages",
    )
    auteur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="messages_envoyes",
    )
    destinataire = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="messages_recus",
    )

    # 2. Contenu avec validation
    contenu_texte = models.TextField(
        validators=[MinLengthValidator(1, message="Le message ne peut pas Ãªtre vide")],
        blank=True  # Permet le vide si un fichier est joint
    )
    contenu_media = models.FileField(
        upload_to="messages/media/",
        blank=True,
        null=True,
    )
    type_message = models.CharField(
        max_length=20,
        choices=MessageType.CHOICES,
        default=MessageType.TEXTE,
    )

    # 3. Statut & suivi
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)
    date_lecture = models.DateTimeField(null=True, blank=True)

    # 4. Lien avec les engagements
    message_declencheur_engagement = models.BooleanField(default=False)
    engagement_associe = models.ForeignKey(
        "Engagement",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages_lies",
    )

    def __str__(self):
        return f"Message #{self.id} (conv {self.conversation_id})"


class ProfessorAnnouncement(models.Model):
    TARGET_CHOICES = [
        ('ALL', 'Tous les utilisateurs'),
        ('PROF', 'Professeurs uniquement'),
        ('PARENT_APPRENANT', 'Parents et Apprenants uniquement'),
    ]
    title = models.CharField(max_length=255)
    message = models.TextField()
    target_audience = models.CharField(max_length=20, choices=TARGET_CHOICES, default='ALL')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    dismissed_by = models.ManyToManyField(User, related_name='dismissed_announcements', blank=True)

    def __str__(self):
        return f"{self.title} ({'Active' if self.is_active else 'Inactive'})"


class TransactionFedaPay(models.Model):
    """
    Trace comptable d'une tentative de paiement des frais d'engagement (2000 FCFA)
    ou de souscription Ã  un abonnement Premium.
    """
    TYPE_TRANSACTION_CHOICES = [
        ('ENGAGEMENT', 'Engagement'),
        ('ABONNEMENT', 'Abonnement'),
    ]
    type_transaction = models.CharField(
        max_length=20,
        choices=TYPE_TRANSACTION_CHOICES,
        default='ENGAGEMENT',
        help_text="Type de la transaction"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="transactions_fedapay",
        null=True,
        blank=True,
        help_text="L'utilisateur qui effectue le paiement (requis pour les abonnements)"
    )
    engagement = models.ForeignKey(
        "Engagement",
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True,
        blank=True,
        help_text="L'engagement liÃ© Ã  ce paiement (pour type ENGAGEMENT)"
    )
    transaction_id = models.CharField(
        max_length=100, 
        unique=True,
        help_text="L'ID de transaction gÃ©nÃ©rÃ© par FedaPay"
    )
    montant = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=2000.00,
        help_text="Montant en FCFA"
    )
    statut = models.CharField(
        max_length=50,
        default="pending",
        help_text="Statut renvoyÃ© par FedaPay (ex: pending, approved, declined)"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.statut}"

class RessourceProfesseur(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    fichier_pdf = models.FileField(upload_to='ressources_profs/', blank=True, null=True)
    lien_externe = models.URLField(max_length=500, blank=True, null=True, help_text="Lien Google Drive ou autre")
    est_guide_officiel = models.BooleanField(
        default=False, 
        help_text="Cochez ceci si ce document est le Guide Officiel téléchargeable depuis le bouton principal."
    )
    ordre_affichage = models.IntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordre_affichage', '-date_creation']
        verbose_name = "Ressource Professeur"
        verbose_name_plural = "Ressources Professeurs"

    def __str__(self):
        return self.titre

class FAQProfesseur(models.Model):
    question = models.CharField(max_length=255)
    reponse = models.TextField()
    ordre_affichage = models.IntegerField(default=0)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['ordre_affichage']
        verbose_name = "FAQ Professeur"
        verbose_name_plural = "FAQs Professeurs"

    def __str__(self):
        return self.question

