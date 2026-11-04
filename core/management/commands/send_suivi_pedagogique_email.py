import time
import logging
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from core.models import TeacherProfile
from core.choices import ValidationStatus

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Envoie un e-mail de sensibilisation à l'espace de suivi pédagogique (et simulateur) aux professeurs validés."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Mode simulation : affiche la liste et le nombre de professeurs validés sans envoyer d'e-mails.",
        )
        parser.add_argument(
            '--test-email',
            type=str,
            help="Adresse e-mail de test pour envoyer un exemplaire unique de vérification sans toucher aux autres.",
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help="Limite le nombre d'e-mails envoyés (ex: --limit 10).",
        )
        parser.add_argument(
            '--yes',
            action='store_true',
            help="Confirme automatiquement l'envoi sans demander de confirmation interactive.",
        )

    def get_email_content(self, prenom):
        sujet = "Votre Espace de suivi pédagogique : un atout clé pour valoriser votre enseignement 📊"
        simulator_url = "https://profchezvousapp.com/prof/simulateur-suivi/"
        channel_url = "https://whatsapp.com/channel/0029VbD5Qni2Jl8KaiqS3k36"

        message_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 15px; color: #2D3748; line-height: 1.6; max-width: 600px; margin: 0 auto;">
            <p>Bonjour <strong>{prenom}</strong>,</p>
            
            <p>L’<strong>Espace de suivi pédagogique</strong> de Prof Chez Vous est bien plus qu'une simple fonctionnalité de la plateforme : c’est un outil qui renforce la qualité de votre accompagnement et valorise concrètement votre travail auprès des parents.</p>
            
            <p>Comme vous l'avez accepté lors de votre inscription à travers nos <em>Conditions Générales d’Utilisation</em>, vous avez l’obligation de renseigner et d'actualiser régulièrement cet espace après vos séances dans le cadre de vos collaborations officialisées sur la plateforme.</p>
            
            <p>Cette exigence n'est toutefois pas une simple formalité. Elle vous offre plusieurs avantages concrets :</p>
            
            <ul style="padding-left: 20px; margin: 15px 0;">
                <li style="margin-bottom: 8px;"><strong>Valoriser votre travail :</strong> permettre aux parents de mieux comprendre les notions abordées, les difficultés rencontrées et les progrès observés au fil de vos séances.</li>
                <li style="margin-bottom: 8px;"><strong>Garder une mémoire de vos séances :</strong> retrouver facilement les informations consignées et revenir sur un objectif ou une difficulté rencontrée précédemment.</li>
                <li style="margin-bottom: 8px;"><strong>Adapter votre accompagnement :</strong> repérer les difficultés récurrentes, observer les évolutions et ajuster votre démarche pédagogique à partir des informations recueillies.</li>
                <li style="margin-bottom: 8px;"><strong>Renforcer la confiance des parents :</strong> leur donner une meilleure visibilité sur votre implication et sur le travail réalisé avec leur enfant.</li>
            </ul>
            
            <p>Vous l'aurez compris, cet espace constitue une véritable mémoire pédagogique. Bien utilisé, il devient un atout pour votre pratique professionnelle autant qu'un gage de transparence pour les familles.</p>
            
            <!-- DÉCOUVERTE SIMULATEUR -->
            <p>Pour vous permettre de découvrir concrètement son fonctionnement dès aujourd'hui et sans stress, nous avons mis en place un <strong>espace de simulation interactif</strong> avec un élève fictif.</p>
            
            <div style="text-align: center; margin: 25px 0;">
                <a href="{simulator_url}" 
                   style="display: inline-block; padding: 13px 26px; background-color: #2563EB; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 15px; box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);">
                    📊 Découvrir et tester le simulateur de suivi
                </a>
            </div>
            
            <!-- CADRE CHAINE WHATSAPP (MINI-FORMATION) -->
            <div style="background-color: #F8FAFC; border-left: 4px solid #25D366; padding: 18px; border-radius: 6px; margin: 30px 0;">
                <p style="margin: 0 0 10px 0; font-weight: bold; color: #1E293B; font-size: 16px;">
                    🎓 Une mini-formation arrive dans les prochains jours !
                </p>
                <p style="margin: 0 0 15px 0; font-size: 14px; color: #475569;">
                    Nous lancerons très prochainement une série de publications pensée comme une mini-formation pour vous accompagner pas à pas dans la prise en main de l'espace et vous transmettre les bonnes pratiques.
                </p>
                <p style="margin: 0 0 15px 0; font-size: 14px; color: #475569;">
                    Ces partages auront lieu directement sur notre <strong>chaîne WhatsApp officielle</strong>. Si ce n'est pas encore fait, nous vous invitons vivement à la rejoindre dès maintenant :
                </p>
                <a href="{channel_url}" 
                   style="display: inline-block; padding: 10px 20px; background-color: #25D366; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 14px;">
                    📲 Intégrer la chaîne WhatsApp officielle
                </a>
            </div>
            
            <p>Cet outil mérite toute votre attention, et nous sommes convaincus qu'il fera la différence dans vos collaborations.</p>
            
            <p style="margin-top: 25px;">
                À très vite sur la plateforme,<br>
                <strong>L'équipe Prof Chez Vous</strong>
            </p>
        </div>
        """

        message_text = f"""Bonjour {prenom},

L’Espace de suivi pédagogique de Prof Chez Vous est bien plus qu'une simple fonctionnalité de la plateforme : c’est un outil qui renforce la qualité de votre accompagnement et valorise concrètement votre travail auprès des parents.

Comme vous l'avez accepté lors de votre inscription à travers nos Conditions Générales d’Utilisation, vous avez l’obligation de renseigner et d'actualiser régulièrement cet espace après vos séances dans le cadre de vos collaborations officialisées sur la plateforme.

Cette exigence n'est toutefois pas une simple formalité. Elle vous offre plusieurs avantages concrets :

- Valoriser votre travail : permettre aux parents de mieux comprendre les notions abordées, les difficultés rencontrées et les progrès observés au fil de vos séances.
- Garder une mémoire de vos séances : retrouver facilement les informations consignées et revenir sur un objectif ou une difficulté rencontrée précédemment.
- Adapter votre accompagnement : repérer les difficultés récurrentes, observer les évolutions et ajuster votre démarche pédagogique à partir des informations recueillies.
- Renforcer la confiance des parents : leur donner une meilleure visibilité sur votre implication et sur le travail réalisé avec leur enfant.

Vous l'aurez compris, cet espace constitue une véritable mémoire pédagogique de chaque collaboration. Bien utilisé, il devient un atout majeur pour votre pratique professionnelle autant qu'un gage de transparence pour les parents.

Pour vous permettre de découvrir concrètement son fonctionnement dès aujourd'hui et sans attendre votre première séance officielle, nous avons mis en place un espace de simulation interactif avec un élève fictif.

👉 Découvrir et tester le simulateur de suivi :
{simulator_url}

Dans les prochains jours, nous lancerons une série de publications conçue comme une mini-formation afin de vous guider pas à pas dans l'appréhension de cet outil et vous transmettre les meilleures pratiques.

Cette mini-formation sera diffusée directement sur notre chaîne WhatsApp officielle. Si ce n'est pas encore fait, nous vous invitons vivement à la rejoindre dès maintenant pour être prêt à suivre chaque étape :

📲 Intégrer la chaîne WhatsApp officielle :
{channel_url}

Cet outil mérite toute votre attention, et nous sommes convaincus qu'il fera la différence dans vos collaborations.

À très vite sur la plateforme,

L'équipe Prof Chez Vous"""

        return sujet, message_text, message_html

    def handle(self, *args, **options):
        dry_run = options.get('dry_run')
        test_email = options.get('test_email')
        limit = options.get('limit')
        auto_yes = options.get('yes')

        self.stdout.write(self.style.MIGRATE_HEADING("=== Envoi d'information Espace Suivi Pédagogique aux Professeurs Validés ==="))

        # Mode TEST
        if test_email:
            prenom = "Professeur"
            # Cherche si l'email correspond à un professeur existant
            prof_found = TeacherProfile.objects.filter(
                Q(user__email__iexact=test_email) | Q(email__iexact=test_email)
            ).first()
            if prof_found:
                prenom = (
                    getattr(prof_found, 'prenom', '')
                    or (prof_found.user.first_name if prof_found.user else '')
                    or "Professeur"
                ).strip().capitalize()

            self.stdout.write(self.style.WARNING(f"MODE TEST activé : envoi d'un exemplaire unique à {test_email} (Prénom utilisé : {prenom})"))
            sujet, message_text, message_html = self.get_email_content(prenom)

            try:
                send_mail(
                    subject=sujet,
                    message=message_text,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[test_email],
                    html_message=message_html,
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f"✅ E-mail de test envoyé avec succès à {test_email} !"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Échec de l'envoi test à {test_email} : {e}"))
            return

        # Sélection des professeurs validés uniquement
        queryset = TeacherProfile.objects.filter(
            statut_de_validation=ValidationStatus.VALIDE
        ).exclude(
            Q(user__email='') & Q(email='')
        ).select_related('user').order_by('-id')

        if limit:
            destinataires = list(queryset[:limit])
        else:
            destinataires = list(queryset)

        total = len(destinataires)
        self.stdout.write(f"Nombre de professeur(s) validé(s) ciblé(s) : {total}")

        if dry_run:
            self.stdout.write(self.style.NOTICE("\n[MODE SIMULATION] Aucun e-mail n'a été envoyé."))
            for idx, p in enumerate(destinataires, 1):
                email_addr = getattr(p, 'email', '') or (p.user.email if p.user else '')
                prenom = getattr(p, 'prenom', '') or (p.user.first_name if p.user else '') or "Professeur"
                nom = getattr(p, 'nom', '') or (p.user.last_name if p.user else '')
                self.stdout.write(f"  {idx}. {prenom} {nom} <{email_addr}> (ID: {p.id})")
            return

        if total == 0:
            self.stdout.write(self.style.WARNING("Aucun professeur validé trouvé."))
            return

        # Confirmation utilisateur avant envoi groupé réel
        if not auto_yes:
            self.stdout.write(self.style.WARNING(f"\n⚠️  Vous êtes sur le point d'envoyer {total} e-mails réels à tous les professeurs validés."))
            try:
                confirm = input("Confirmez-vous l'envoi ? (o/N) : ").strip().lower()
                if confirm not in ['o', 'oui', 'y', 'yes']:
                    self.stdout.write(self.style.NOTICE("Opération annulée."))
                    return
            except (KeyboardInterrupt, EOFError):
                self.stdout.write(self.style.NOTICE("\nOpération annulée."))
                return

        emails_sent = 0
        emails_failed = 0

        for idx, prof in enumerate(destinataires, 1):
            email_addr = getattr(prof, 'email', '') or (prof.user.email if prof.user else '')
            if not email_addr:
                continue

            prenom = (
                getattr(prof, 'prenom', '')
                or (prof.user.first_name if prof.user else '')
                or "Professeur"
            ).strip().capitalize()

            sujet, message_text, message_html = self.get_email_content(prenom)

            try:
                send_mail(
                    subject=sujet,
                    message=message_text,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email_addr],
                    html_message=message_html,
                    fail_silently=False,
                )
                emails_sent += 1
                self.stdout.write(f"[{idx}/{total}] Envoyé à {prenom} <{email_addr}>")
                time.sleep(0.1)  # Petite pause pour respecter le quota SMTP
            except Exception as e:
                emails_failed += 1
                logger.error(f"Échec de l'envoi à {email_addr} : {e}", exc_info=True)
                self.stdout.write(self.style.ERROR(f"[{idx}/{total}] Erreur pour {email_addr} : {e}"))

        self.stdout.write(self.style.SUCCESS(f"\nTerminé ! {emails_sent} e-mail(s) envoyé(s) avec succès ({emails_failed} échec(s))."))
