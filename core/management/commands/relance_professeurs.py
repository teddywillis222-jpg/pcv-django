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

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        only_unsent = options.get('only_unsent', False)
        
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
            sujet = "Presque prêt ! Votre vitrine de professeur vous attend sur Prof Chez Vous 🚀"
            
            message_html = f"""
            <div style="font-family: Arial, sans-serif; font-size: 15px; color: #333; line-height: 1.6;">
                <p>Bonjour {name},</p>
                
                <p>Nous avons remarqué que vous avez créé votre compte sur <strong>Prof Chez Vous</strong>, et nous tenons à vous féliciter pour cette première étape !</p>
                
                <p>Cependant, votre profil n'est pas encore tout à fait terminé. Pour commencer à être visible auprès des parents d'élèves et lancer votre essor sur la plateforme, il ne vous reste plus qu'à finaliser votre dossier (vos matières, votre diplôme et votre courte vidéo de présentation).</p>
                
                <p>Rassurez-vous, c'est simple et rapide ! Chaque document est une garantie de confiance pour les familles qui recherchent l'excellence pour leurs enfants.</p>
                
                <p><strong>Besoin d'un coup de main ? 🤝</strong><br>
                Si vous rencontrez la moindre difficulté technique, ou si vous préférez être guidé, notre équipe est là pour vous accompagner pas à pas !</p>
                
                <p style="margin: 20px 0;">
                    <a href="https://wa.me/2290147528839" style="display:inline-block; padding:12px 22px; background-color:#25D366; color:white; text-decoration:none; border-radius:6px; font-weight:bold; font-size:15px;">
                        Contacter le support WhatsApp
                    </a>
                </p>
                
                <p>Nous avons hâte de vous compter parmi nos professeurs officiels et de bâtir cette aventure ensemble.</p>
                
                <p>À très vite sur la plateforme,<br>
                <strong>L'équipe Prof Chez Vous</strong></p>
                
                <hr style="border:none; border-top:1px solid #e0e0e0; margin: 30px 0 15px 0;">
                
                <p style="font-size: 12px; color: #777; line-height: 1.5; margin: 0;">
                    <strong>Gestion de vos données personnelles :</strong><br>
                    Vous disposez à tout moment du droit de demander la suppression de vos données et de votre compte sur Prof Chez Vous. Si vous ne souhaitez plus poursuivre, il vous suffit de <strong>répondre directement à cet e-mail</strong> en mentionnant votre nom et l'adresse e-mail utilisée lors de la création de votre compte.
                </p>
            </div>
            """
            
            # Version texte brut (fallback pour les clients mail ne supportant pas HTML)
            message_text = f"""Bonjour {name},

Nous avons remarqué que vous avez créé votre compte sur Prof Chez Vous, et nous tenons à vous féliciter pour cette première étape !

Cependant, votre profil n'est pas encore tout à fait terminé. Pour commencer à être visible auprès des parents d'élèves et lancer votre essor sur la plateforme, il ne vous reste plus qu'à finaliser votre dossier (vos matières, votre diplôme et votre courte vidéo de présentation).

Rassurez-vous, c'est simple et rapide ! Chaque document est une garantie de confiance pour les familles qui recherchent l'excellence pour leurs enfants.

Besoin d'un coup de main ? 🤝 
Si vous rencontrez la moindre difficulté technique, ou si vous préférez être guidé, notre équipe est là pour vous accompagner pas à pas.

Cliquez ici pour échanger directement avec notre support sur WhatsApp : https://wa.me/2290147528839

Nous avons hâte de vous compter parmi nos professeurs officiels et de bâtir cette aventure ensemble.

À très vite sur la plateforme,

L'équipe Prof Chez Vous

--------------------------------------------------
Gestion de vos données personnelles :
Vous disposez à tout moment du droit de demander la suppression de vos données et de votre compte sur Prof Chez Vous. Si vous ne souhaitez plus poursuivre, il vous suffit de répondre directement à ce message en mentionnant votre nom et l'adresse e-mail utilisée lors de la création de votre compte."""

            try:
                # Utilisation du DEFAULT_FROM_EMAIL par défaut dans django, s'il n'est pas configuré il tombera sur webmaster@localhost ou autre
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
