from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Quartier
import os
import json

class Command(BaseCommand):
    help = "Met à jour la base de données des quartiers à partir de localisations.json"

    def handle(self, *args, **kwargs):
        file_path = getattr(settings, 'LOCALISATIONS_FILE', None)
        if not file_path:
            file_path = os.path.join(settings.BASE_DIR, 'core', 'localisations.json')
            
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"Fichier introuvable: {file_path}"))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            localisations = json.load(f)

        added = 0
        for item in localisations:
            name = item[0]
            # Vérifier si le quartier existe déjà
            if not Quartier.objects.filter(nom=name).exists():
                # Déterminer la ville basée sur le nom
                ville = "Cotonou"
                name_lower = name.lower()
                if "abomey-calavi" in name_lower or "abomey calavi" in name_lower:
                    ville = "Abomey-Calavi"
                elif "porto-novo" in name_lower:
                    ville = "Porto-Novo"
                elif "sèmè-kpodji" in name_lower or "seme-kpodji" in name_lower:
                    ville = "Sèmè-Kpodji"
                elif "inconnu" in name_lower:
                    ville = "Inconnu"
                
                Quartier.objects.create(nom=name, ville=ville)
                added += 1
                self.stdout.write(f"Ajouté : {name} (Ville: {ville})")

        self.stdout.write(self.style.SUCCESS(f"Terminé. {added} nouveaux quartiers ont été ajoutés."))
