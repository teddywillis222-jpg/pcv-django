from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

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

    def __str__(self):
        return f"{self.user.username} ({self.role})"


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
        return f"Détails parent {self.user.username}"


class Parent(models.Model):
    # C. Lien avec l’utilisateur (obligatoire)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="parent",
    )

    # A. Identification & contact
    nom = models.CharField(max_length=150)
    numero_whatsapp = models.CharField(max_length=50)
    profession = models.CharField(max_length=150, blank=True)
    quartier_ville = models.CharField(max_length=150, blank=True)
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

    def __str__(self):
        return f"Parent {self.nom}"


class Enfant(models.Model):
    # 1. Identité et liens système
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

    # 2. Profil académique et besoins
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
        help_text="Matières nécessitant un accompagnement (max 5)",
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
        blank=True,
        help_text="Format « Quartier-Ville » pour matching avec professeurs",
    )
    mode_de_cours = models.CharField(
        max_length=30,
        choices=CourseMode.CHOICES,
        blank=True,
    )

    def __str__(self):
        return f"{self.prenom} ({self.parent.nom})"

    @property
    def age(self):
        """Âge calculé à partir de date_de_naissance."""
        if not self.date_de_naissance:
            return None
        from datetime import date

        today = date.today()
        return (
            today.year
            - self.date_de_naissance.year
            - ((today.month, today.day) < (self.date_de_naissance.month, self.date_de_naissance.day))
        )




class Abonnement(models.Model):
    """Contrat d'abonnement, créé automatiquement à l'inscription."""

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
        default="2000f par engagement",
    )
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Abonnement {self.type_abonnement} — {self.user.username}"


class Apprenant(models.Model):
    # 1. Identité et liens système
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="apprenant",
    )
    nom = models.CharField(max_length=200, help_text="Nom et prénom")
    email_apprenant = models.EmailField(blank=True)
    telephone = models.CharField(max_length=50, blank=True, help_text="Numéro WhatsApp")
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

    # 2. Parcours et besoins académiques
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
        help_text="Matières prioritaires (max 5)",
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
        blank=True,
        help_text="Format « Quartier-Ville » pour matching",
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
    """Une seule évaluation par (parent_évaluateur, professeur_évalué). UPSERT en cas de mise à jour."""

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
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"

    def __str__(self):
        return f"Évaluation {self.note}/5 — {self.professeur_evalue}"


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

    # 2. Présentation et méthodologie
    photo_de_profil = models.ImageField(
        upload_to="teachers/profile_photos/",
        blank=True,
        null=True,
    )
    presentation = models.TextField(blank=True)
    methodologie = models.TextField(blank=True)
    annees_d_experience = models.PositiveIntegerField(default=0)
    categorie_de_soutien = models.CharField(
        max_length=20,
        choices=SupportCategory.CHOICES,
    )

    # 3. Compétences et modalités
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
    ville_quartier = models.CharField(max_length=150)
    disponibilites = models.ManyToManyField(
        Disponibilite,
        blank=True,
        related_name="teachers",
    )
    grille_disponibilites = models.JSONField(default=list, blank=True)
    message_admin = models.TextField(blank=True)

    # 4. Documents et vérification
    fichier_cni = models.FileField(
        upload_to="teachers/cni/",
        blank=True,
        null=True,
    )
    liste_certifications_texte = models.TextField(blank=True)
    statut_de_validation = models.CharField(
        max_length=20,
        choices=ValidationStatus.CHOICES,
        default=ValidationStatus.EN_ATTENTE,
    )
    est_certifie = models.BooleanField(default=False)

    # 5. Tarification et offres
    tarif_horaire = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    essai_gratuit_actif = models.BooleanField(default=False)

    # 6. Statistiques et visibilité
    nb_vues_jour = models.PositiveIntegerField(default=0)
    nb_vues_semaine = models.PositiveIntegerField(default=0)
    nb_vues_mois = models.PositiveIntegerField(default=0)
    # evaluations_recues : relation inverse depuis Evaluation.professeur_evalue
    nb_engagements_confirmes = models.PositiveIntegerField(default=0)
    nb_engagements_finalises = models.PositiveIntegerField(default=0)
    nb_engagements_termines = models.PositiveIntegerField(default=0)
    nb_engagements_total = models.PositiveIntegerField(default=0)

    # 7. Paramètres et consentement
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
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Professeur {self.prenom} {self.nom}"


class Conversation(models.Model):
    # 1. Identité et participants
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

    # 4. Métadonnées & UX
    conversation_lue_par_parent = models.BooleanField(default=False)
    conversation_lue_par_prof = models.BooleanField(default=False)
    conversation_archivee = models.BooleanField(default=False)

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

    # 2. Logistique et localisation
    mode_de_cours = models.CharField(
        max_length=30,
        choices=CourseMode.CHOICES,
        blank=True,
    )
    localisation_option = models.CharField(
        max_length=150,
        blank=True,
        help_text="Format « Quartier-Ville »",
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
        blank=True,
    )

    # 4. États et flux de contrôle
    statut_general = models.CharField(
        max_length=20,
        choices=StatutGeneral.CHOICES,
        default=StatutGeneral.EN_ATTENTE,
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

    # 6. Sécurité et actions bilatérales
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

    # 7. Suivi et qualité (journal_séance_lié = Liste_Séances via engagement.seances)
    # evaluation_liee : relation inverse depuis Evaluation.engagement_lie

    # 8. Suivi global matière (ajouts)
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

    def __str__(self):
        return f"Engagement #{self.id} (conv {self.conversation_id})"


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
        return f"Séance #{self.id} (eng. {self.engagement_id})"


class NotionSeance(models.Model):
    seance = models.ForeignKey(
        "Seance",
        on_delete=models.CASCADE,
        related_name="notions",
    )
    nom_notion = models.CharField(max_length=255)
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="Score de 0 à 3",
    )

    def __str__(self):
        return f"{self.nom_notion} ({self.seance})"


class Message(models.Model):
    # 1. Références
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

    # 2. Contenu
    contenu_texte = models.TextField(blank=True)
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