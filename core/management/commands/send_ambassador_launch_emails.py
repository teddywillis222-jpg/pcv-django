import time
from django.core.management.base import BaseCommand
from django.core.mail import send_mail, get_connection
from django.conf import settings
from django.utils.html import strip_tags
from core.models import TeacherProfile, ValidationStatus
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Envoie l\'e-mail de lancement du Programme Ambassadeurs.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--target',
            type=str,
            choices=['valides', 'incomplets'],
            required=True,
            help='Cible de l\'e-mail : "valides" ou "incomplets".'
        )
        parser.add_argument(
            '--test',
            type=str,
            help='Adresse e-mail de test pour envoyer un seul exemplaire de vérification.'
        )

    def handle(self, *args, **options):
        target = options['target']
        test_email = options.get('test')

        # 1. Sélection de la cible
        if target == 'valides':
            professeurs = TeacherProfile.objects.filter(statut_de_validation=ValidationStatus.VALIDE).exclude(user__email='')
            subject = "🚀 Lancement officiel : Le Programme Ambassadeurs Prof Chez Vous est là !"
        elif target == 'incomplets':
            professeurs = TeacherProfile.objects.exclude(statut_de_validation=ValidationStatus.VALIDE).exclude(user__email='')
            subject = "🎉 Le Programme Ambassadeurs est lancé ! (Finalisez votre profil pour y participer)"
        
        # Mode Test
        if test_email:
            professeurs = professeurs[:1]
            self.stdout.write(self.style.WARNING(f"MODE TEST ACTIF : L'e-mail sera envoyé uniquement à {test_email}"))
        
        total_profs = professeurs.count()
        self.stdout.write(self.style.SUCCESS(f"Préparation de l'envoi à {total_profs} professeurs ({target})."))
        
        if total_profs == 0:
            self.stdout.write(self.style.WARNING("Aucun professeur trouvé pour cette cible."))
            return

        from_email = settings.DEFAULT_FROM_EMAIL
        
        connection = get_connection()
        connection.open()
        
        success_count = 0
        error_count = 0

        for prof in professeurs:
            # Récupération sécurisée du prénom (fallback sur email si vide)
            prenom = prof.prenom if prof.prenom else prof.user.first_name
            if not prenom:
                prenom = "Professeur"

            # 2. Construction du message HTML en fonction de la cible
            if target == 'valides':
                html_message = f"""
                <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px;">
                    <h2 style="color: #16a34a; text-align: center;">Le moment est arrivé.</h2>
                    <p>Bonjour <strong>{prenom}</strong>,</p>
                    <p>Le Programme Ambassadeurs Prof Chez Vous est officiellement lancé. 🎉</p>
                    <p>En tant que professeur vérifié sur la plateforme, vous pouvez désormais devenir Ambassadeur et recommander à Prof Chez Vous des collègues enseignants sérieux et compétents de votre entourage.</p>
                    
                    <h3 style="color: #0f172a;">Le principe est simple :</h3>
                    <p>Vous recommandez → votre collègue s’inscrit via votre lien personnel → il complète son profil et passe notre processus de vérification → votre recommandation est validée → vous recevez votre récompense.</p>
                    
                    <p>L'objectif n'est pas de multiplier les inscriptions à tout prix. Nous voulons construire une communauté d'enseignants de qualité, suffisamment large pour permettre à chaque parent ou apprenant de trouver le professeur adapté à ses besoins.</p>
                    <p>Votre rôle est donc simple : identifier des enseignants que vous seriez vous-même prêt à recommander.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://profchezvousapp.com/dashboard/#section-ambassadeur" style="background-color: #16a34a; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">👉 Accéder au Programme Ambassadeurs</a>
                    </div>
                    
                    <p style="background-color: #f1f5f9; padding: 15px; border-radius: 4px; font-size: 0.9em;">
                        📄 Avant de participer, nous vous invitons à consulter les conditions générales du programme :<br>
                        <a href="https://profchezvousapp.com/cgu-ambassadeurs/" style="color: #2563eb;">https://profchezvousapp.com/cgu-ambassadeurs/</a>
                    </p>
                    
                    <p>Merci de contribuer, à votre manière, à la construction d'une communauté enseignante plus professionnelle et plus accessible au Bénin.</p>
                    <p style="margin-top: 30px;">L'équipe Prof Chez Vous 💚</p>
                </div>
                """
            else: # incomplets
                html_message = f"""
                <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px;">
                    <h2 style="color: #16a34a; text-align: center;">Le Programme Ambassadeurs est lancé !</h2>
                    <p>Bonjour <strong>{prenom}</strong>,</p>
                    <p>Le Programme Ambassadeurs Prof Chez Vous est désormais officiellement lancé. 🎉</p>
                    <p>Vous avez déjà fait le premier pas en rejoignant Prof Chez Vous. Il vous reste toutefois une étape importante avant de pouvoir participer au programme.</p>
                    <p>Pour devenir Ambassadeur, votre compte doit disposer d'un profil entièrement complété et être officiellement vérifié par notre équipe.</p>
                    
                    <h3 style="color: #0f172a;">Le parcours est simple :</h3>
                    <ol style="padding-left: 20px; line-height: 1.8;">
                        <li>Complétez votre profil</li>
                        <li>Soumettez les informations et justificatifs nécessaires à la vérification</li>
                        <li>Une fois votre profil validé, accédez au Programme Ambassadeurs</li>
                        <li>Recommandez des collègues enseignants via votre lien personnel</li>
                        <li>Recevez votre récompense lorsque les conditions du programme sont réunies</li>
                    </ol>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://profchezvousapp.com/professeur/creer-profil/" style="background-color: #16a34a; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">👉 Compléter mon profil / Finaliser mon inscription</a>
                    </div>
                    
                    <p>Une fois votre profil complété et votre vérification terminée, vous pourrez pleinement profiter des fonctionnalités réservées aux professeurs vérifiés, dont le Programme Ambassadeurs.</p>
                    
                    <p style="background-color: #f1f5f9; padding: 15px; border-radius: 4px; font-size: 0.9em;">
                        📄 Les conditions générales du programme sont disponibles ici :<br>
                        <a href="https://profchezvousapp.com/cgu-ambassadeurs/" style="color: #2563eb;">https://profchezvousapp.com/cgu-ambassadeurs/</a>
                    </p>
                    
                    <p style="margin-top: 30px;">L'équipe Prof Chez Vous 💚</p>
                </div>
                """

            plain_message = strip_tags(html_message).replace('👉', '>').strip()
            recipient_email = test_email if test_email else prof.user.email

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
                self.stdout.write(f"✅ E-mail ({target}) envoyé avec succès à {prenom} ({recipient_email})")
                time.sleep(0.5)
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"❌ Erreur lors de l'envoi à {recipient_email}: {str(e)}"))

        connection.close()
        self.stdout.write(self.style.SUCCESS(f"\nTerminé ! {success_count} e-mails envoyés avec succès. {error_count} erreurs."))
