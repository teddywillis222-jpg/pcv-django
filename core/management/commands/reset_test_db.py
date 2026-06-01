from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Vide entièrement la base de données et recrée un superutilisateur de test.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('1/2: Vidage de la base de données en cours...'))
        
        # Flush the database (interactive=False ensures it doesn't prompt for confirmation)
        call_command('flush', interactive=False)
        
        self.stdout.write(self.style.SUCCESS('-> Base de données vidée avec succès.'))

        self.stdout.write(self.style.WARNING('2/2: Création du superutilisateur de test...'))
        
        User = get_user_model()
        username = 'admin_test'
        password = 'password_test'
        email = 'admin@profchezvous.com'
        
        # In case the flush didn't affect the user table (e.g. if using a custom database routing setup), 
        # it's safer to check, although flush usually wipes everything.
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'-> Superutilisateur créé avec succès !'))
            self.stdout.write(self.style.SUCCESS(f'   Identifiant : {username}'))
            self.stdout.write(self.style.SUCCESS(f'   Mot de passe : {password}'))
        else:
            self.stdout.write(self.style.WARNING(f'-> Le superutilisateur "{username}" existe déjà.'))

        self.stdout.write(self.style.SUCCESS('✅ Réinitialisation de la base de données de test terminée !'))
