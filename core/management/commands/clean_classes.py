import json
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import TeacherProfile
from core.choices import ClassLevel

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Nettoie et standardise les classes (classes_enseignees et classes_expertise) des professeurs.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simule les changements sans les appliquer en base de données.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Mots-clés / mappings pour transformer les données sales en données propres
        mapping = {
            # Collège
            "6": "6ème", "6e": "6ème", "6eme": "6ème", "6ème": "6ème", "sixieme": "6ème", "sixième": "6ème",
            "5": "5ème", "5e": "5ème", "5eme": "5ème", "5ème": "5ème", "cinquieme": "5ème", "cinquième": "5ème",
            "4": "4ème", "4e": "4ème", "4eme": "4ème", "4ème": "4ème", "quatrieme": "4ème", "quatrième": "4ème",
            "3": "3ème", "3e": "3ème", "3eme": "3ème", "3ème": "3ème", "troisieme": "3ème", "troisième": "3ème",

            # Lycée Littéraire / Scientifique global mapping
            # (Note: Les valeurs ambiguës comme "Terminale" sont divisées en deux)
            "2nd": ["2nde Littéraire", "2nde Scientifique"],
            "2nde": ["2nde Littéraire", "2nde Scientifique"],
            "seconde": ["2nde Littéraire", "2nde Scientifique"],
            
            "1er": ["1ère Littéraire", "1ère Scientifique"],
            "1ere": ["1ère Littéraire", "1ère Scientifique"],
            "1ère": ["1ère Littéraire", "1ère Scientifique"],
            "premiere": ["1ère Littéraire", "1ère Scientifique"],
            "première": ["1ère Littéraire", "1ère Scientifique"],

            "tle": ["Tle Littéraire", "Tle Scientifique"],
            "term": ["Tle Littéraire", "Tle Scientifique"],
            "terminal": ["Tle Littéraire", "Tle Scientifique"],
            "terminale": ["Tle Littéraire", "Tle Scientifique"],

            # Remplacement des "sci"
            "tle_sci": "Tle Scientifique",
            "tle sci": "Tle Scientifique",
            "terminale sci": "Tle Scientifique",
            
            "1ere_sci": "1ère Scientifique",
            "1ere sci": "1ère Scientifique",
            
            "2nde_sci": "2nde Scientifique",
            "2nde sci": "2nde Scientifique",
            
            # Remplacement des "lit"
            "tle_lit": "Tle Littéraire",
            "tle lit": "Tle Littéraire",
            "1ere_lit": "1ère Littéraire",
            "2nde_lit": "2nde Littéraire",

            # Primaire
            "ci": "CI",
            "cp": "CP",
            "ce1": "CE1",
            "ce2": "CE2",
            "cm1": "CM1",
            "cm2": "CM2",
            "maternelle": "MATERNELLE",
        }

        # Obtenir la liste des valeurs valides officielles définies dans ClassLevel
        valid_choices = set(ClassLevel.VALUES)

        profiles = TeacherProfile.objects.all()
        total_modified = 0

        self.stdout.write(self.style.NOTICE(f"Début du nettoyage {'(DRY-RUN)' if dry_run else ''} pour {profiles.count()} profils..."))

        try:
            with transaction.atomic():
                for profile in profiles:
                    modified = False
                    
                    # Fonction interne pour nettoyer une liste de classes
                    def clean_class_list(class_list):
                        if not isinstance(class_list, list):
                            return []
                        
                        cleaned_list = []
                        for item in class_list:
                            item_clean = str(item).strip().lower()
                            
                            # Si on a un mapping précis
                            if item_clean in mapping:
                                mapped_val = mapping[item_clean]
                                if isinstance(mapped_val, list):
                                    cleaned_list.extend(mapped_val)
                                else:
                                    cleaned_list.append(mapped_val)
                                continue
                                
                            # Si la valeur brute (sans lower()) est déjà valide
                            if item in valid_choices:
                                cleaned_list.append(item)
                                continue
                                
                            # Sinon, on vérifie si la valeur lowercase correspond à un choix valide en minuscules
                            found_valid = False
                            for valid_choice in valid_choices:
                                if item_clean == valid_choice.lower():
                                    cleaned_list.append(valid_choice)
                                    found_valid = True
                                    break
                            
                            if not found_valid:
                                # Classe totalement inconnue -> Suppression (on ne l'ajoute pas à cleaned_list)
                                self.stdout.write(self.style.WARNING(f"  [SUPPRIMÉ] '{item}' n'est pas reconnu (Profil ID: {profile.id})"))

                        # Éliminer les doublons tout en préservant l'ordre
                        return list(dict.fromkeys(cleaned_list))

                    # 1. Nettoyer classes_enseignees
                    old_enseignees = profile.classes_enseignees if isinstance(profile.classes_enseignees, list) else []
                    new_enseignees = clean_class_list(old_enseignees)
                    
                    if old_enseignees != new_enseignees:
                        if dry_run:
                            self.stdout.write(f"Profil {profile.user.email} (ID: {profile.id}) - Enseignées :")
                            self.stdout.write(f"  Ancien: {old_enseignees}")
                            self.stdout.write(self.style.SUCCESS(f"  Nouveau: {new_enseignees}"))
                        profile.classes_enseignees = new_enseignees
                        modified = True

                    # 2. Nettoyer classes_expertise
                    old_expertise = profile.classes_expertise if isinstance(profile.classes_expertise, list) else []
                    new_expertise = clean_class_list(old_expertise)
                    
                    if old_expertise != new_expertise:
                        if dry_run:
                            self.stdout.write(f"Profil {profile.user.email} (ID: {profile.id}) - Expertise :")
                            self.stdout.write(f"  Ancien: {old_expertise}")
                            self.stdout.write(self.style.SUCCESS(f"  Nouveau: {new_expertise}"))
                        profile.classes_expertise = new_expertise
                        modified = True

                    # Sauvegarde si modifications et pas en dry_run
                    if modified:
                        total_modified += 1
                        if not dry_run:
                            profile.save(update_fields=['classes_enseignees', 'classes_expertise'])

                if dry_run:
                    # En dry-run on annule la transaction pour être sûr à 100%
                    raise Exception("Dry-run complete. Transaction rollback.")

        except Exception as e:
            if str(e) == "Dry-run complete. Transaction rollback.":
                self.stdout.write(self.style.SUCCESS(f"\n[DRY-RUN] {total_modified} profils auraient été modifiés."))
            else:
                self.stdout.write(self.style.ERROR(f"Erreur: {str(e)}"))
                raise e
        else:
            self.stdout.write(self.style.SUCCESS(f"\nNettoyage terminé avec succès ! {total_modified} profils ont été mis à jour en base de données."))
