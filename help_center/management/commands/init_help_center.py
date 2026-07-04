from django.core.management.base import BaseCommand
from help_center.models import Category, Article


class Command(BaseCommand):
    help = "Crée les catégories et articles de démonstration pour le Centre d'aide."

    def handle(self, *args, **options):
        # ── Catégories ──
        categories_data = [
            {"name": "Parents", "slug": "parents", "description": "Tout ce qu'un parent doit savoir pour utiliser Prof Chez Vous.", "icon": "bi bi-people", "order": 1, "target_audience": "parents"},
            {"name": "Professeurs", "slug": "professeurs", "description": "Guides pour les professeurs inscrits sur la plateforme.", "icon": "bi bi-mortarboard", "order": 2, "target_audience": "teachers"},
            {"name": "Paiements", "slug": "paiements", "description": "Frais, moyens de paiement et remboursements.", "icon": "bi bi-wallet2", "order": 3, "target_audience": "all"},
            {"name": "Vérification", "slug": "verification", "description": "Processus de vérification et certification des professeurs.", "icon": "bi bi-patch-check", "order": 4, "target_audience": "all"},
            {"name": "Cours particuliers", "slug": "cours-particuliers", "description": "Réservation, déroulement et suivi des cours.", "icon": "bi bi-journal-text", "order": 5, "target_audience": "all"},
            {"name": "Compte", "slug": "compte", "description": "Création, modification et suppression de votre compte.", "icon": "bi bi-person-gear", "order": 6, "target_audience": "all"},
            {"name": "Sécurité", "slug": "securite", "description": "Conseils de sécurité et signalement.", "icon": "bi bi-shield-check", "order": 7, "target_audience": "all"},
            {"name": "Politique", "slug": "politique", "description": "Conditions d'utilisation, confidentialité et mentions légales.", "icon": "bi bi-file-earmark-text", "order": 8, "target_audience": "all"},
            {"name": "Application", "slug": "application", "description": "Fonctionnalités de la plateforme et mises à jour.", "icon": "bi bi-phone", "order": 9, "target_audience": "all"},
        ]

        created_cats = {}
        for cat_data in categories_data:
            cat, created = Category.objects.update_or_create(
                slug=cat_data["slug"],
                defaults=cat_data
            )
            created_cats[cat.slug] = cat
            status = "[+] Creee" if created else "[~] Mise a jour"
            self.stdout.write(f"  {status} : {cat.name}")

        # ── Articles de démonstration ──
        articles_data = [
            # Parents
            {
                "title": "Comment créer un compte parent ?",
                "slug": "comment-creer-un-compte-parent",
                "category": "parents",
                "keywords": "inscription, créer compte, s'inscrire, parent, nouveau",
                "content": "<h2>Créer votre compte parent en quelques minutes</h2><p>Pour créer votre compte parent sur Prof Chez Vous, rendez-vous sur la page d'inscription et choisissez le rôle <strong>Parent</strong>. Remplissez les informations demandées : nom, prénom, email et mot de passe.</p><h3>Étapes détaillées</h3><ol><li>Accédez à la page d'inscription</li><li>Choisissez le rôle « Parent »</li><li>Renseignez vos informations personnelles</li><li>Ajoutez le profil de votre enfant</li><li>Votre compte est prêt !</li></ol>"
            },
            {
                "title": "Comment réserver un cours ?",
                "slug": "comment-reserver-un-cours",
                "category": "parents",
                "keywords": "réserver, cours, engagement, prendre un cours, booking",
                "content": "<h2>Réserver un cours particulier</h2><p>Pour réserver un cours sur Prof Chez Vous, commencez par rechercher un professeur en utilisant la barre de recherche. Filtrez par matière, niveau et localisation pour trouver le profil idéal.</p><h3>Procédure de réservation</h3><ol><li>Recherchez un professeur</li><li>Consultez son profil et ses tarifs</li><li>Cliquez sur « Engager ce professeur »</li><li>Remplissez les détails du cours souhaité</li><li>Confirmez et procédez au paiement</li></ol>"
            },
            {
                "title": "Comment suivre la progression de mon enfant ?",
                "slug": "comment-suivre-progression-enfant",
                "category": "parents",
                "keywords": "suivi, progression, bilan, séances, résultats, notes",
                "content": "<h2>Le suivi pédagogique de votre enfant</h2><p>Prof Chez Vous propose un système de suivi pédagogique intégré. Après chaque séance, le professeur rédige un bilan détaillé visible depuis votre tableau de bord.</p><p>Vous pouvez suivre :</p><ul><li>Les bilans de chaque séance</li><li>Les objectifs atteints</li><li>Les prochaines étapes recommandées par le professeur</li></ul>"
            },
            # Professeurs
            {
                "title": "Comment créer mon profil professeur ?",
                "slug": "comment-creer-profil-professeur",
                "category": "professeurs",
                "keywords": "inscription professeur, profil, s'inscrire, devenir prof, enseigner",
                "content": "<h2>Devenir professeur sur Prof Chez Vous</h2><p>Pour rejoindre la communauté des professeurs, inscrivez-vous en choisissant le rôle <strong>Professeur</strong>. Complétez votre profil avec vos diplômes, expériences et tarifs.</p><h3>Les étapes</h3><ol><li>Inscrivez-vous avec le rôle Professeur</li><li>Complétez votre profil (matières, niveaux, tarifs)</li><li>Ajoutez vos diplômes et certifications</li><li>Soumettez votre profil pour vérification</li><li>Une fois approuvé, votre profil sera visible</li></ol>"
            },
            {
                "title": "Comment fonctionne la vérification des professeurs ?",
                "slug": "comment-fonctionne-verification-professeurs",
                "category": "verification",
                "keywords": "vérification, validation, certifié, approuvé, diplômes, badge",
                "content": "<h2>Le processus de vérification</h2><p>Chaque professeur inscrit sur Prof Chez Vous passe par un processus de vérification rigoureux. Nous vérifions les diplômes et l'identité de chaque candidat.</p><h3>Ce que nous vérifions</h3><ul><li>L'identité du professeur</li><li>Les diplômes et certifications</li><li>L'expérience d'enseignement</li></ul><p>Les professeurs vérifiés reçoivent un badge <strong>Certifié</strong> sur leur profil.</p>"
            },
            # Paiements
            {
                "title": "Quels sont les moyens de paiement acceptés ?",
                "slug": "moyens-de-paiement-acceptes",
                "category": "paiements",
                "keywords": "paiement, payer, mobile money, MTN, Moov, FedaPay, carte",
                "content": "<h2>Modes de paiement</h2><p>Prof Chez Vous accepte plusieurs moyens de paiement pour faciliter vos transactions :</p><ul><li><strong>Mobile Money</strong> : MTN Mobile Money, Moov Money</li><li><strong>Paiement en ligne</strong> via notre partenaire FedaPay</li></ul><p>Tous les paiements sont sécurisés et vous recevez une confirmation par email.</p>"
            },
            # Compte
            {
                "title": "Comment modifier mes informations personnelles ?",
                "slug": "comment-modifier-informations-personnelles",
                "category": "compte",
                "keywords": "modifier, profil, informations, email, mot de passe, photo",
                "content": "<h2>Modifier votre profil</h2><p>Vous pouvez modifier vos informations personnelles à tout moment depuis votre tableau de bord.</p><h3>Pour les parents</h3><p>Rendez-vous dans votre dashboard et cliquez sur « Modifier le profil ». Vous pouvez mettre à jour votre nom, email et les profils de vos enfants.</p><h3>Pour les professeurs</h3><p>Accédez à « Modifier mon profil » dans votre espace professeur pour mettre à jour vos tarifs, matières et disponibilités.</p>"
            },
            # Sécurité
            {
                "title": "Comment protéger mon compte ?",
                "slug": "comment-proteger-mon-compte",
                "category": "securite",
                "keywords": "sécurité, mot de passe, protection, compte, piratage",
                "content": "<h2>Conseils de sécurité</h2><p>La sécurité de votre compte est notre priorité. Voici quelques bonnes pratiques :</p><ul><li>Utilisez un mot de passe fort et unique</li><li>Ne partagez jamais vos identifiants</li><li>Changez votre mot de passe régulièrement</li><li>Vérifiez l'URL du site avant de vous connecter</li></ul><p>Si vous suspectez une activité suspecte, contactez immédiatement notre support.</p>"
            },
        ]

        for art_data in articles_data:
            cat_slug = art_data.pop("category")
            category = created_cats[cat_slug]
            article, created = Article.objects.update_or_create(
                slug=art_data["slug"],
                defaults={**art_data, "category": category}
            )
            status = "[+] Cree" if created else "[~] Mis a jour"
            self.stdout.write(f"  {status} : {article.title}")

        # ── Liens entre articles liés ──
        try:
            art_parent = Article.objects.get(slug="comment-creer-un-compte-parent")
            art_reserver = Article.objects.get(slug="comment-reserver-un-cours")
            art_suivi = Article.objects.get(slug="comment-suivre-progression-enfant")
            art_paiement = Article.objects.get(slug="moyens-de-paiement-acceptes")

            art_parent.related_articles.set([art_reserver, art_suivi])
            art_reserver.related_articles.set([art_parent, art_paiement])
            art_suivi.related_articles.set([art_parent, art_reserver])
            self.stdout.write("  [>] Liens entre articles crees")
        except Article.DoesNotExist:
            pass

        self.stdout.write(self.style.SUCCESS("\nCentre d'aide initialise avec succes !"))
