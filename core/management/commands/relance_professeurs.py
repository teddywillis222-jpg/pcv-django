import logging
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from core.models import Profile, TeacherProfile
from core.choices import ValidationStatus

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Envoie un e-mail de relance aux professeurs dont le profil est vide ou incomplet."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Ne pas envoyer les e-mails, juste afficher les cibles",
        )
        parser.add_argument(
            '--only-unsent',
            action='store_true',
            help="Filtrer uniquement ceux n'ayant jamais reçu la relance",
        )
        parser.add_argument(
            '--test-email',
            type=str,
            help="Envoyer un e-mail de test uniquement à cette adresse (aucun autre e-mail ne sera envoyé)",
        )

    def get_email_content(self, name):
        sujet = "Presque prêt ! Votre vitrine de professeur vous attend sur Prof Chez Vous 🚀"
        profile_url = "https://profchezvousapp.com/prof/create-profile/"
        whatsapp_url = "https://wa.me/2290147528839"

        message_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 15px; color: #2D3748; line-height: 1.6; max-width: 600px; margin: 0 auto;">
            <p>Bonjour <strong>{name}</strong>,</p>
            
            <p>Nous avons remarqué que vous avez créé votre compte sur <strong>Prof Chez Vous</strong>, et nous tenons à vous féliciter pour cette première étape !</p>
            
            <p>Cependant, votre profil n'est pas encore tout à fait terminé. Pour commencer à être visible auprès des parents d'élèves et recevoir vos premières demandes, il ne vous reste plus qu'à finaliser votre dossier (vos matières, votre diplôme et votre courte vidéo de présentation).</p>
            
            <p>Rassurez-vous, c'est simple et rapide ! Chaque document est un gage de confiance essentiel pour les familles qui recherchent l'excellence pour leurs enfants.</p>
            
            <!-- BOUTON D'ACTION PRINCIPAL -->
            <div style="text-align: center; margin: 30px 0;">
                <a href="{profile_url}" 
                   style="display: inline-block; padding: 14px 28px; background-color: #2563EB; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 16px; box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);">
                    🚀 Finaliser mon profil professeur
                </a>
            </div>
            
            <!-- BLOC ASSISTANCE WHATSAPP -->
            <div style="background-color: #F8FAFC; border-left: 4px solid #25D366; padding: 15px; border-radius: 4px; margin: 25px 0;">
                <p style="margin: 0 0 10px 0; font-weight: bold; color: #1E293B;">Besoin d'un coup de main ? 🤝</p>
                <p style="margin: 0 0 10px 0; font-size: 14px; color: #475569;">
                    Si vous rencontrez la moindre difficulté technique ou si vous préférez être guidé, notre équipe est là pour vous accompagner pas à pas.
                </p>
                <a href="{whatsapp_url}" 
                   style="display: inline-block; padding: 8px 16px; background-color: #25D366; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 13px;">
                    Contacter le support WhatsApp
                </a>
            </div>
            
            <p>Nous avons hâte de vous compter parmi nos professeurs officiels et de bâtir cette aventure ensemble.</p>
            
            <p style="margin-top: 25px;">
                À très vite sur la plateforme,<br>
                <strong>L'équipe Prof Chez Vous</strong>
            </p>
            
            <!-- PIED DE PAGE / RGPD -->
            <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 35px 0 15px 0;">
            <p style="font-size: 12px; color: #718096; line-height: 1.5; margin: 0;">
                <strong>Gestion de vos données personnelles :</strong><br>
                Vous disposez à tout moment du droit de demander la suppression de vos données et de votre compte sur Prof Chez Vous. Si vous ne souhaitez pas poursuivre, il vous suffit de <strong>répondre directement à cet e-mail</strong> en mentionnant votre nom et l'adresse e-mail associée à votre compte.
            </p>
        </div>
        """

        message_text = f"""Bonjour {name},

Nous avons remarqué que vous avez créé votre compte sur Prof Chez Vous, et nous tenons à vous féliciter pour cette première étape !

Cependant, votre profil n'est pas encore tout à fait terminé. Pour commencer à être visible auprès des parents d'élèves et recevoir vos premières demandes, il ne vous reste plus qu'à finaliser votre dossier (vos matières, votre diplôme et votre courte vidéo de présentation).

Rassurez-vous, c'est simple et rapide ! Chaque élément est un gage de confiance essentiel pour les familles qui recherchent l'excellence pour leurs enfants.

👉 Cliquez sur le lien ci-dessous pour compléter votre profil dès maintenant :
{profile_url}

Besoin d'un coup de main ? 🤝
Si vous rencontrez la moindre difficulté technique ou si vous préférez être guidé, notre équipe est là pour vous accompagner pas à pas sur WhatsApp :
{whatsapp_url}

Nous avons hâte de vous compter parmi nos professeurs officiels et de bâtir cette aventure ensemble.

À très vite sur la plateforme,

L'équipe Prof Chez Vous

--------------------------------------------------
Gestion de vos données personnelles :
Vous disposez à tout moment du droit de demander la suppression de vos données et de votre compte sur Prof Chez Vous. Si vous ne souhaitez plus poursuivre, il vous suffit de répondre directement à ce message en mentionnant votre nom et l'adresse e-mail utilisée lors de la création de votre compte."""

        return sujet, message_text, message_html

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        only_unsent = options.get('only_unsent', False)
        test_email = options.get('test_email')
        
        # Mode test avec une adresse spécifique
        if test_email:
            name = "Professeur Test"
            user_found = User.objects.filter(email__iexact=test_email).first()
            if user_found:
                name = user_found.first_name or user_found.username
                
            self.stdout.write(f"Mode TEST activé : envoi d'un e-mail unique à {test_email} (Nom affiché : {name})")
            sujet, message_text, message_html = self.get_email_content(name)

            try:
                send_mail(
                    subject=sujet,
                    message=message_text,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[test_email],
                    html_message=message_html,
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f"E-mail de test envoyé avec succès à {test_email} !"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Échec d'envoi du test à {test_email} : {e}"))
            return
        
        # Sélectionne les utilisateurs ayant le rôle PROF (insensible à la casse pour compatibilité)
        users_profs = User.objects.filter(profile__role__iexact=Profile.ROLE_PROF).select_related('profile')
        
        cibles = []
        for user in users_profs:
            if only_unsent and getattr(user.profile, 'relance_incomplet_envoyee', False):
                continue
                
            # Vérifie l'état du profil lié
            needs_relance = False
            try:
                teacher_profile = user.teacher_profile
                if teacher_profile.statut_de_validation == ValidationStatus.INCOMPLET:
                    needs_relance = True
            except TeacherProfile.DoesNotExist:
                # Profil inexistant ou vide
                needs_relance = True
                
            if needs_relance:
                cibles.append(user)

        self.stdout.write(f"Trouvé {len(cibles)} professeur(s) nécessitant une relance.")

        if dry_run:
            for user in cibles:
                self.stdout.write(f"- {user.email} (ID: {user.id})")
            return

        emails_sent = 0
        for user in cibles:
            if not user.email:
                continue

            name = user.first_name or user.username
            sujet, message_text, message_html = self.get_email_content(name)

            try:
                # Utilisation du DEFAULT_FROM_EMAIL par défaut dans django
                send_mail(
                    subject=sujet,
                    message=message_text,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=message_html,
                    fail_silently=False,
                )
                
                # Marquer comme envoyé
                user.profile.relance_incomplet_envoyee = True
                user.profile.save(update_fields=['relance_incomplet_envoyee'])
                
                emails_sent += 1
                logger.info(f"Relance profil incomplet envoyée avec succès à {user.email}.")
            except Exception as e:
                logger.error(f"Échec d'envoi de l'email de relance à {user.email} : {e}", exc_info=True)

        self.stdout.write(self.style.SUCCESS(f"{emails_sent} e-mails de relance envoyés avec succès."))
