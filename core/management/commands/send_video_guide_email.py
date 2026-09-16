import time
import logging
from django.core.management.base import BaseCommand
from django.core.mail import send_mail, get_connection
from django.conf import settings
from django.db.models import Q
from core.models import TeacherProfile, ValidationStatus, RessourceProfesseur

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Envoie un e-mail aux professeurs pour leur présenter la vidéo de présentation et leur fournir le lien de téléchargement direct du guide."

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            type=str,
            help="Adresse e-mail réelle pour tester l'envoi en direct (ex: --test monemail@gmail.com)",
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Simule l'envoi et affiche la liste des destinataires sans envoyer d'e-mails.",
        )
        parser.add_argument(
            '--only-without-video',
            action='store_true',
            help="Cible uniquement les professeurs qui n'ont pas encore soumis de vidéo.",
        )
        parser.add_argument(
            '--all-profiles',
            action='store_true',
            help="Cible tous les professeurs (y compris en attente), au lieu de cibler uniquement les validés.",
        )

    def handle(self, *args, **options):
        test_email = options.get('test')
        dry_run = options.get('dry_run')
        only_without_video = options.get('only_without_video')
        all_profiles = options.get('all_profiles')

        # Récupération de la ressource Guide Vidéo
        guide = RessourceProfesseur.objects.filter(actif=True).filter(
            Q(titre__icontains="vidéo") | Q(titre__icontains="video")
        ).first()

        base_url = "https://profchezvousapp.com"

        if guide:
            guide_url = f"{base_url}/ressources-professeurs/{guide.id}/download/"
            self.stdout.write(self.style.SUCCESS(f"Guide vidéo identifié : '{guide.titre}' (ID: {guide.id})"))
            self.stdout.write(f"URL directe du guide : {guide_url}")
        else:
            self.stdout.write(self.style.WARNING("⚠️ Attention : Aucun guide vidéo trouvé dans RessourceProfesseur."))
            guide_url = f"{base_url}/prof/video-presentation/"

        video_page_url = f"{base_url}/prof/video-presentation/"

        # Construction de la liste des destinataires
        if test_email:
            self.stdout.write(self.style.WARNING(f"MODE TEST ACTIF : L'e-mail sera envoyé UNIQUEMENT à {test_email}"))
            prof_test = TeacherProfile.objects.filter(user__email__iexact=test_email).first()
            if not prof_test:
                class MockUser:
                    email = test_email
                    first_name = "Enseignant"
                    username = "Enseignant"
                class MockProf:
                    user = MockUser()
                    prenom = "Enseignant"
                    nom = ""
                destinataires = [MockProf()]
            else:
                destinataires = [prof_test]
        else:
            queryset = TeacherProfile.objects.exclude(user__email='')
            if not all_profiles:
                queryset = queryset.filter(statut_de_validation=ValidationStatus.VALIDE)
            
            if only_without_video:
                queryset = queryset.filter(videos__isnull=True).distinct()

            destinataires = list(queryset.select_related('user'))

        total = len(destinataires)
        self.stdout.write(f"Nombre de destinataire(s) : {total}")

        if dry_run:
            self.stdout.write(self.style.NOTICE("MODE SIMULATION (DRY-RUN) : Aucun e-mail ne sera envoyé."))
            for d in destinataires[:30]:
                self.stdout.write(f"- {getattr(d, 'prenom', '')} {getattr(d, 'nom', '')} <{d.user.email}>")
            if total > 30:
                self.stdout.write(f"... et {total - 30} autres.")
            return

        if total == 0:
            self.stdout.write(self.style.WARNING("Aucun destinataire à contacter."))
            return

        subject = "Votre vidéo de présentation sur Prof Chez Vous 🎬"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Prof Chez Vous <contact@profchezvous.com>')

        connection = get_connection()
        connection.open()

        success_count = 0
        error_count = 0

        for prof in destinataires:
            prenom = getattr(prof, 'prenom', '') or getattr(prof.user, 'first_name', '') or "Professeur"
            recipient_email = test_email if test_email else prof.user.email

            html_message = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b; line-height: 1.6;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f8fafc; padding: 25px 15px;">
        <tr>
            <td align="center">
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 580px; background-color: #ffffff; border-radius: 16px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
                    
                    <!-- En-tête -->
                    <tr>
                        <td style="padding: 28px 30px 20px; background: linear-gradient(135deg, #15803d 0%, #16a34a 100%); text-align: center;">
                            <div style="font-size: 24px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">
                                Prof Chez Vous
                            </div>
                            <div style="font-size: 13px; color: #dcfce7; margin-top: 4px; font-weight: 500;">
                                Rentrée 2026 — Valorisez votre savoir-faire
                            </div>
                        </td>
                    </tr>

                    <!-- Contenu principal -->
                    <tr>
                        <td style="padding: 30px;">
                            <h1 style="font-size: 19px; font-weight: 800; color: #0f172a; margin: 0 0 16px; line-height: 1.3;">
                                Donnez vie à votre profil avec votre vidéo de présentation 🎬
                            </h1>

                            <p style="margin: 0 0 14px; font-size: 15px; color: #334155;">
                                Bonjour <strong>{prenom}</strong>,
                            </p>

                            <p style="margin: 0 0 14px; font-size: 15px; color: #334155;">
                                À l’occasion de cette rentrée, Prof Chez Vous met en place une nouvelle opportunité pour vous démarquer auprès des familles : <strong>la vidéo de présentation</strong>.
                            </p>

                            <p style="margin: 0 0 14px; font-size: 15px; color: #334155;">
                                Votre profil ne se résume pas à vos diplômes. Une courte vidéo permet aux parents et apprenants de découvrir directement votre personnalité, votre écoute et votre approche pédagogique.
                            </p>

                            <!-- Encadré décomplexant -->
                            <div style="background-color: #f0fdf4; border-left: 4px solid #16a34a; border-radius: 6px; padding: 14px 16px; margin: 18px 0;">
                                <p style="margin: 0; font-size: 14px; color: #166534; line-height: 1.5;">
                                    💡 <strong>Pas besoin d’équipement professionnel !</strong> De quelques secondes à 2 minutes, l’essentiel est de rester naturel, clair et professionnel dans un endroit calme.
                                </p>
                            </div>

                            <p style="margin: 0 0 18px; font-size: 15px; color: #334155;">
                                Pour vous aider à réussir votre présentation pas à pas avec ce que vous avez, nous avons conçu un <strong>guide pratique spécialement adapté</strong> :
                            </p>

                            <!-- Bouton Téléchargement Guide -->
                            <div style="text-align: center; margin: 24px 0;">
                                <a href="{guide_url}" download style="display: inline-block; background-color: #16a34a; color: #ffffff; text-decoration: none; font-weight: 700; font-size: 15px; padding: 13px 26px; border-radius: 10px; box-shadow: 0 4px 10px rgba(22, 163, 74, 0.25);">
                                    📥 Télécharger le Guide Vidéo (PDF)
                                </a>
                            </div>

                            <p style="margin: 0 0 14px; font-size: 14.5px; color: #475569;">
                                Dès que votre vidéo est prête, vous pouvez la soumettre en un instant depuis votre espace personnel :
                            </p>

                            <!-- Bouton Espace Vidéo -->
                            <div style="text-align: center; margin: 16px 0 24px;">
                                <a href="{video_page_url}" style="display: inline-block; background-color: #ffffff; color: #15803d; border: 1.5px solid #16a34a; text-decoration: none; font-weight: 700; font-size: 14px; padding: 10px 22px; border-radius: 10px;">
                                    🎬 Accéder à mon espace vidéo
                                </a>
                            </div>

                            <p style="margin: 0 0 16px; font-size: 13.5px; color: #64748b; font-style: italic;">
                                Les vidéos validées seront mises en avant sur votre profil public et dans nos actions de communication pour vous apporter de nouveaux élèves.
                            </p>

                            <p style="margin: 24px 0 0; font-size: 15px; color: #334155; line-height: 1.5;">
                                Bonne rentrée et excellente préparation de votre vidéo !<br>
                                <strong>L’équipe Prof Chez Vous</strong>
                            </p>
                        </td>
                    </tr>

                    <!-- Pied de page -->
                    <tr>
                        <td style="padding: 18px 30px; background-color: #f8fafc; border-top: 1px solid #f1f5f9; text-align: center; font-size: 12px; color: #94a3b8;">
                            © 2026 Prof Chez Vous. Tous droits réservés.<br>
                            Cet e-mail vous est adressé en tant qu'enseignant inscrit sur Prof Chez Vous.
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

            plain_message = f"""Bonjour {prenom},

À l'occasion de cette rentrée, Prof Chez Vous met en place une nouvelle opportunité pour vous démarquer auprès des familles : la vidéo de présentation.

Votre profil ne se résume pas à vos diplômes. Une courte vidéo permet aux parents et apprenants de découvrir directement votre personnalité et votre pédagogie.

Pas besoin de matériel professionnel ! De quelques secondes à 2 minutes, l'essentiel est de rester naturel, clair et professionnel dans un endroit calme.

Pour vous aider à réussir votre enregistrement pas à pas avec vos moyens actuels, téléchargez notre guide pratique :
👉 Télécharger le guide (PDF) : {guide_url}

Une fois votre vidéo prête, vous pouvez la soumettre en un instant depuis votre espace personnel :
👉 Gérer ma vidéo : {video_page_url}

Les vidéos validées seront mises en avant sur votre profil et auprès des familles.

Bonne rentrée et excellente préparation !

L'équipe Prof Chez Vous
"""

            try:
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=from_email,
                    recipient_list=[recipient_email],
                    html_message=html_message,
                    connection=connection,
                    fail_silently=False,
                )
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f"✅ E-mail envoyé avec succès à {recipient_email}"))
                time.sleep(0.4)
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"❌ Erreur lors de l'envoi à {recipient_email}: {str(e)}"))

        connection.close()
        self.stdout.write(self.style.SUCCESS(f"\nOpération terminée ! {success_count} envoyé(s), {error_count} erreur(s)."))
