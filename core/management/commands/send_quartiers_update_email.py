from django.core.management.base import BaseCommand
from django.core.mail import send_mail, get_connection
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from core.models import TeacherProfile, ValidationStatus
import time

class Command(BaseCommand):
    help = 'Envoie un e-mail à tous les professeurs validés pour leur annoncer la fonctionnalité des quartiers multiples.'

    def handle(self, *args, **options):
        # Récupérer uniquement les professeurs approuvés
        professeurs = TeacherProfile.objects.filter(statut_de_validation=ValidationStatus.VALIDE).exclude(user__email='')
        
        total_profs = professeurs.count()
        self.stdout.write(self.style.SUCCESS(f'Préparation de l\'envoi à {total_profs} professeurs validés.'))
        
        if total_profs == 0:
            self.stdout.write(self.style.WARNING("Aucun professeur validé trouvé avec une adresse e-mail."))
            return

        subject = "🚀 Nouveauté : Étendez votre zone d'enseignement et recevez plus de demandes !"
        from_email = settings.DEFAULT_FROM_EMAIL
        
        # Ouvre une seule connexion pour envoyer tous les e-mails plus rapidement
        connection = get_connection()
        connection.open()
        
        success_count = 0
        error_count = 0

        for prof in professeurs:
            # Construction du message HTML (on utilise inline CSS pour une compatibilité max)
            html_message = f"""
            <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px;">
                <h2 style="color: #16a34a; text-align: center;">Nouveauté Prof Chez Vous</h2>
                <p>Bonjour <strong>{prof.prenom}</strong>,</p>
                
                <p>Bonne nouvelle ! Afin d'augmenter votre visibilité auprès des parents et de vous offrir plus d'opportunités de cours, nous avons mis à jour la plateforme Prof Chez Vous.</p>
                
                <p>Vous avez désormais la possibilité d'ajouter <strong>plusieurs quartiers couverts</strong> à votre profil !</p>
                
                <p>En complétant avec précision toutes les zones où vous êtes capable de vous rendre, vous aidez les parents de ces quartiers à vous trouver plus facilement.</p>
                
                <h3 style="color: #0f172a;">Comment faire ?</h3>
                <p style="background-color: #f1f5f9; padding: 15px; border-left: 4px solid #3b82f6; border-radius: 4px;">
                    Pour commencer, ouvrez le menu en appuyant sur l'icône à trois traits située en haut à droite de votre écran. Sélectionnez ensuite <strong><em>Modifier mon profil</em></strong> afin d'accéder à votre espace de modification et d'optimiser votre profil pour gagner en visibilité auprès des parents et des apprenants.
                </p>

                <h3 style="color: #dc2626;">⚠️ Un conseil important pour votre réussite :</h3>
                <p>L'objectif est d'optimiser vos déplacements, pas de vous épuiser. Avant d'ajouter un quartier, posez-vous ces 3 questions :</p>
                <ul style="padding-left: 20px;">
                    <li style="margin-bottom: 10px;"><strong>Le temps de trajet :</strong> La zone est-elle facilement accessible, même aux heures de pointe ?</li>
                    <li style="margin-bottom: 10px;"><strong>La rentabilité :</strong> Le coût de transport (Zemidjan, essence) pour s'y rendre est-il absorbé par votre tarif horaire ?</li>
                    <li style="margin-bottom: 10px;"><strong>La ponctualité :</strong> Pourrez-vous y être à l'heure à chaque séance pour maintenir votre excellente réputation (et éviter les avis négatifs) ?</li>
                </ul>

                <p>Mettez à jour vos zones d'intervention dès aujourd'hui et préparez-vous à recevoir de nouvelles demandes de cours !</p>

                <p style="margin-top: 30px;">À très bientôt,<br><strong>L'équipe Prof Chez Vous</strong></p>
            </div>
            """
            
            # Version texte pur pour les clients e-mails qui ne supportent pas le HTML
            plain_message = strip_tags(html_message).replace('⚠️', '[Attention]').strip()

            try:
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=from_email,
                    recipient_list=[prof.user.email],
                    html_message=html_message,
                    connection=connection,
                    fail_silently=False,
                )
                success_count += 1
                self.stdout.write(f"✅ E-mail envoyé avec succès à {prof.prenom} {prof.nom} ({prof.user.email})")
                
                # Petite pause pour éviter le throttle SMTP
                time.sleep(0.5)
                
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"❌ Erreur lors de l'envoi à {prof.user.email}: {str(e)}"))

        connection.close()
        
        self.stdout.write(self.style.SUCCESS(f"\nTerminé ! {success_count} e-mails envoyés avec succès. {error_count} erreurs."))
