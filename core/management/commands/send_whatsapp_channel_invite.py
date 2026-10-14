import time
import logging
from django.core.management.base import BaseCommand
from django.core.mail import send_mail, get_connection
from django.conf import settings
from core.models import TeacherProfile, ValidationStatus

logger = logging.getLogger(__name__)

DEFAULT_CHANNEL_URL = "https://whatsapp.com/channel/0029VbD5Qni2Jl8KaiqS3k36"
DEFAULT_SUBJECT = "Ne ratez pas les prochaines nouveautés sur Prof Chez Vous 📲"


class Command(BaseCommand):
    help = "Envoie un e-mail d'invitation à rejoindre la chaîne WhatsApp officielle aux professeurs validés de Prof Chez Vous."

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            type=str,
            help="Adresse e-mail de test pour envoyer un seul exemplaire de vérification (ex: --test monemail@gmail.com).",
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Mode simulation : affiche la liste et le nombre de professeurs ciblés sans envoyer d'e-mails.",
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help="Limite le nombre d'e-mails envoyés (ex: --limit 50).",
        )
        parser.add_argument(
            '--all-profiles',
            action='store_true',
            help="Cible tous les profils de professeurs (même non validés), au lieu de cibler uniquement les validés.",
        )
        parser.add_argument(
            '--subject',
            type=str,
            default=DEFAULT_SUBJECT,
            help="Personnalise l'objet de l'e-mail.",
        )
        parser.add_argument(
            '--channel-url',
            type=str,
            default=DEFAULT_CHANNEL_URL,
            help="Lien URL de la chaîne WhatsApp (défaut : https://whatsapp.com/channel/0029VbD5Qni2Jl8KaiqS3k36).",
        )

    def handle(self, *args, **options):
        test_email = options.get('test')
        dry_run = options.get('dry_run')
        limit = options.get('limit')
        all_profiles = options.get('all_profiles')
        subject = options.get('subject') or DEFAULT_SUBJECT
        channel_url = options.get('channel_url') or DEFAULT_CHANNEL_URL
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Prof Chez Vous <contact@profchezvous.com>')

        self.stdout.write(self.style.MIGRATE_HEADING("=== Envoi d'invitation à la chaîne WhatsApp Prof Chez Vous ==="))

        # Sélection des destinataires
        if test_email:
            self.stdout.write(self.style.WARNING(f"MODE TEST : L'e-mail sera envoyé UNIQUEMENT à {test_email}"))
            prof_test = TeacherProfile.objects.filter(
                statut_de_validation=ValidationStatus.VALIDE
            ).first() or TeacherProfile.objects.first()

            if not prof_test:
                class MockUser:
                    email = test_email
                    first_name = "Professeur"
                    last_name = "Test"
                    def get_full_name(self):
                        return "Professeur Test"
                class MockProf:
                    user = MockUser()
                    prenom = "Professeur"
                    nom = "Test"
                    email = test_email
                destinataires = [MockProf()]
            else:
                destinataires = [prof_test]
        else:
            from django.db.models import Q
            queryset = TeacherProfile.objects.exclude(Q(user__email='') & Q(email=''))
            if not all_profiles:
                queryset = queryset.filter(statut_de_validation=ValidationStatus.VALIDE)

            queryset = queryset.select_related('user').order_by('-id')

            if limit:
                destinataires = list(queryset[:limit])
            else:
                destinataires = list(queryset)

        total = len(destinataires)
        self.stdout.write(f"Nombre de professeur(s) validé(s) sélectionné(s) : {total}")
        self.stdout.write(f"Lien de la chaîne WhatsApp : {channel_url}")

        if dry_run:
            self.stdout.write(self.style.NOTICE("\nMODE SIMULATION (DRY-RUN) : Aucun e-mail n'a été envoyé."))
            for idx, p in enumerate(destinataires[:25], 1):
                nom_affiche = f"{getattr(p, 'prenom', '')} {getattr(p, 'nom', '')}".strip() or p.user.get_full_name() or "Professeur"
                email_addr = getattr(p, 'email', '') or p.user.email
                self.stdout.write(f"  {idx}. {nom_affiche} <{email_addr}>")
            if total > 25:
                self.stdout.write(f"  ... et {total - 25} autres professeurs.")
            return

        if total == 0:
            self.stdout.write(self.style.WARNING("Aucun professeur validé trouvé avec une adresse e-mail."))
            return

        # Confirmation si lancement global
        if not test_email and not dry_run:
            self.stdout.write(self.style.WARNING(f"\n⚠️  Vous êtes sur le point d'envoyer {total} e-mails réels."))
            try:
                confirm = input("Confirmez-vous l'envoi ? (o/N) : ").strip().lower()
                if confirm not in ['o', 'oui', 'y', 'yes']:
                    self.stdout.write(self.style.ERROR("Envoi annulé par l'utilisateur."))
                    return
            except EOFError:
                # Dans le cas d'une exécution non-interactive
                pass

        # Connexion SMTP
        connection = get_connection()
        connection.open()

        success_count = 0
        error_count = 0

        for idx, prof in enumerate(destinataires, 1):
            prenom = getattr(prof, 'prenom', '').strip()
            nom = getattr(prof, 'nom', '').strip()
            if prenom and nom:
                nom_prof = f"{prenom} {nom}"
            elif prenom:
                nom_prof = prenom
            elif hasattr(prof, 'user') and prof.user.get_full_name():
                nom_prof = prof.user.get_full_name()
            else:
                nom_prof = "Professeur"

            recipient_email = test_email if test_email else (getattr(prof, 'email', '') or prof.user.email)

            # Version Texte brut
            plain_message = f"""Bonjour {nom_prof},

Votre profil a été validé sur Prof Chez Vous. Nous sommes heureux de vous compter parmi les professeurs de notre plateforme.

Pour vous permettre de profiter pleinement de votre présence sur Prof Chez Vous, nous vous invitons à rejoindre notre chaîne WhatsApp officielle.

Pourquoi rejoindre la chaîne ?

En vous abonnant, vous pourrez notamment :
- Rester informé des nouveautés et des évolutions de la plateforme.
- Recevoir nos mises à jour et les informations importantes concernant votre espace professeur.
- Découvrir des conseils et astuces pratiques pour mieux valoriser votre profil et développer votre activité de professeur particulier.
- Accéder à des ressources utiles pour améliorer votre utilisation de la plateforme et votre accompagnement des apprenants.

Notre objectif est de vous donner les informations et les outils qui vous aideront à tirer le meilleur parti de Prof Chez Vous et à faire évoluer votre activité.

Ne passez pas à côté des prochaines nouveautés !

👉 Rejoindre la chaîne WhatsApp de Prof Chez Vous :
{channel_url}

L'abonnement à la chaîne est gratuit. Vous pourrez ainsi retrouver nos actualités et nos conseils directement sur WhatsApp.

Au plaisir de vous accompagner dans votre parcours avec Prof Chez Vous.

L'équipe Prof Chez Vous
Le bon professeur. Au bon moment.
"""

            # Version HTML
            html_message = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b; line-height: 1.6;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f8fafc; padding: 20px 8px;">
        <tr>
            <td align="center">
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 660px; background-color: #ffffff; border-radius: 18px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.03);">
                    
                    <!-- En-tête -->
                    <tr>
                        <td style="padding: 26px 28px 20px; background: linear-gradient(135deg, #15803d 0%, #16a34a 100%); text-align: center;">
                            <div style="font-size: 24px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">
                                Prof Chez Vous
                            </div>
                            <div style="font-size: 13.5px; color: #dcfce7; margin-top: 4px; font-weight: 600; letter-spacing: 0.3px;">
                                Communauté Officielle des Professeurs
                            </div>
                        </td>
                    </tr>

                    <!-- Contenu principal -->
                    <tr>
                        <td style="padding: 30px 26px 24px;">
                            <p style="margin: 0 0 16px; font-size: 16px; color: #1e293b;">
                                Bonjour <strong>{nom_prof}</strong>,
                            </p>

                            <p style="margin: 0 0 16px; font-size: 15.5px; color: #334155; line-height: 1.65;">
                                Votre profil a été validé sur <strong>Prof Chez Vous</strong>. Nous sommes heureux de vous compter parmi les professeurs de notre plateforme.
                            </p>

                            <p style="margin: 0 0 22px; font-size: 15.5px; color: #334155; line-height: 1.65;">
                                Pour vous permettre de profiter pleinement de votre présence sur Prof Chez Vous, nous vous invitons à rejoindre notre <strong>chaîne WhatsApp officielle</strong>.
                            </p>

                            <!-- Bloc Pourquoi rejoindre -->
                            <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px 22px; margin: 22px 0 24px;">
                                <h3 style="margin: 0 0 14px; font-size: 16px; font-weight: 800; color: #0f172a;">
                                    Pourquoi rejoindre la chaîne ?
                                </h3>
                                <p style="margin: 0 0 14px; font-size: 15px; color: #475569;">
                                    En vous abonnant, vous pourrez notamment :
                                </p>
                                
                                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                    <tr>
                                        <td valign="top" style="padding-bottom: 10px; width: 22px; font-size: 16px; color: #16a34a;">•</td>
                                        <td style="padding-bottom: 10px; font-size: 15px; color: #334155; line-height: 1.55;">
                                            <strong>Rester informé des nouveautés</strong> et des évolutions de la plateforme.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td valign="top" style="padding-bottom: 10px; width: 22px; font-size: 16px; color: #16a34a;">•</td>
                                        <td style="padding-bottom: 10px; font-size: 15px; color: #334155; line-height: 1.55;">
                                            <strong>Recevoir nos mises à jour</strong> et les informations importantes concernant votre espace professeur.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td valign="top" style="padding-bottom: 10px; width: 22px; font-size: 16px; color: #16a34a;">•</td>
                                        <td style="padding-bottom: 10px; font-size: 15px; color: #334155; line-height: 1.55;">
                                            <strong>Découvrir des conseils et astuces pratiques</strong> pour mieux valoriser votre profil et développer votre activité de professeur particulier.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td valign="top" style="width: 22px; font-size: 16px; color: #16a34a;">•</td>
                                        <td style="font-size: 15px; color: #334155; line-height: 1.55;">
                                            <strong>Accéder à des ressources utiles</strong> pour améliorer votre utilisation de la plateforme et votre accompagnement des apprenants.
                                        </td>
                                    </tr>
                                </table>
                            </div>

                            <p style="margin: 0 0 20px; font-size: 15.5px; color: #334155; line-height: 1.65;">
                                Notre objectif est de vous donner les informations et les outils qui vous aideront à tirer le meilleur parti de Prof Chez Vous et à faire évoluer votre activité.
                            </p>

                            <p style="margin: 0 0 20px; font-size: 15.5px; font-weight: 700; color: #0f172a;">
                                Ne passez pas à côté des prochaines nouveautés !
                            </p>

                            <!-- Bouton CTA WhatsApp -->
                            <div style="text-align: center; margin: 28px 0 24px;">
                                <a href="{channel_url}" target="_blank" rel="noopener noreferrer" style="display: inline-block; background-color: #25D366; color: #ffffff; text-decoration: none; font-weight: 800; font-size: 16px; padding: 15px 32px; border-radius: 12px; box-shadow: 0 4px 14px rgba(37, 211, 102, 0.35); letter-spacing: -0.2px;">
                                    👉 Rejoindre la chaîne WhatsApp de Prof Chez Vous
                                </a>
                            </div>

                            <p style="margin: 0 0 22px; font-size: 14.5px; color: #64748b; line-height: 1.55;">
                                L’abonnement à la chaîne est gratuit. Vous pourrez ainsi retrouver nos actualités et nos conseils directement sur WhatsApp.
                            </p>

                            <p style="margin: 20px 0 20px; font-size: 15.5px; color: #334155; line-height: 1.65;">
                                Au plaisir de vous accompagner dans votre parcours avec Prof Chez Vous.
                            </p>

                            <div style="margin-top: 26px; padding-top: 18px; border-top: 1px solid #f1f5f9;">
                                <div style="font-size: 15px; font-weight: 800; color: #1e293b;">
                                    L’équipe Prof Chez Vous
                                </div>
                                <div style="font-size: 13.5px; color: #64748b; font-style: italic; margin-top: 2px;">
                                    Le bon professeur. Au bon moment.
                                </div>
                            </div>
                        </td>
                    </tr>

                    <!-- Pied de page -->
                    <tr>
                        <td style="padding: 18px 26px; background-color: #f8fafc; border-top: 1px solid #f1f5f9; text-align: center; font-size: 12px; color: #94a3b8; line-height: 1.5;">
                            © 2026 Prof Chez Vous. Tous droits réservés.<br>
                            Cet e-mail est destiné aux professeurs certifiés et validés de la plateforme.
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
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
                self.stdout.write(self.style.SUCCESS(f"[{idx}/{total}] Envoyé avec succès à {nom_prof} <{recipient_email}>"))
            except Exception as e:
                error_count += 1
                logger.error(f"Erreur d'envoi à {recipient_email} : {e}")
                self.stdout.write(self.style.ERROR(f"[{idx}/{total}] Échec pour {nom_prof} <{recipient_email}> : {e}"))

            # Courte pause pour respecter les quotas / limites SMTP
            time.sleep(0.25)

        connection.close()

        self.stdout.write(self.style.MIGRATE_LABEL("\n=== Résumé de l'opération ==="))
        self.stdout.write(self.style.SUCCESS(f"✔ E-mails envoyés avec succès : {success_count}"))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"✖ Échecs : {error_count}"))
        self.stdout.write(self.style.SUCCESS("Opération terminée."))
