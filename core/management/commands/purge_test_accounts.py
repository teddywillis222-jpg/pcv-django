from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.conf import settings


class Command(BaseCommand):
    help = (
        "Supprime des comptes utilisateurs et TOUTES leurs données associées "
        "(Profile, TeacherProfile, Diplômes, Abonnement…) via la cascade Django.\n\n"
        "Modes d'utilisation :\n"
        "  --email user@example.com        Supprimer un seul compte par email\n"
        "  --emails a@x.com,b@x.com        Supprimer plusieurs comptes (séparés par des virgules)\n"
        "  --inactive                       Supprimer TOUS les comptes non activés (is_active=False)\n"
        "  --test-accounts                  Supprimer les comptes listés dans TEST_ACCOUNT_EMAILS du .env\n"
        "  --dry-run                        Simuler sans rien supprimer (affiche ce qui serait supprimé)\n"
        "  --keep-superusers                Protéger les superutilisateurs même s'ils matchent\n"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help="Supprimer le compte associé à cet email.",
        )
        parser.add_argument(
            '--emails',
            type=str,
            help="Supprimer les comptes associés à ces emails (séparés par des virgules).",
        )
        parser.add_argument(
            '--inactive',
            action='store_true',
            help="Supprimer TOUS les comptes avec is_active=False.",
        )
        parser.add_argument(
            '--test-accounts',
            action='store_true',
            help="Supprimer les comptes listés dans TEST_ACCOUNT_EMAILS (.env).",
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Simulation : affiche ce qui serait supprimé sans rien toucher.",
        )
        parser.add_argument(
            '--keep-superusers',
            action='store_true',
            default=True,
            help="Protéger les superutilisateurs (activé par défaut).",
        )
        parser.add_argument(
            '--no-keep-superusers',
            action='store_true',
            help="Autoriser la suppression des superutilisateurs.",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        dry_run = options['dry_run']
        keep_superusers = not options['no_keep_superusers']

        # Construire le queryset des utilisateurs à supprimer
        users_to_delete = User.objects.none()

        if options['email']:
            users_to_delete = User.objects.filter(email=options['email'])

        elif options['emails']:
            email_list = [e.strip() for e in options['emails'].split(',') if e.strip()]
            users_to_delete = User.objects.filter(email__in=email_list)

        elif options['inactive']:
            users_to_delete = User.objects.filter(is_active=False)

        elif options['test_accounts']:
            test_emails = getattr(settings, 'TEST_ACCOUNT_EMAILS', [])
            if not test_emails:
                self.stdout.write(self.style.WARNING(
                    "⚠️  Aucun email trouvé dans TEST_ACCOUNT_EMAILS. "
                    "Vérifiez votre fichier .env."
                ))
                return
            if isinstance(test_emails, str):
                test_emails = [e.strip() for e in test_emails.split(',')]
            users_to_delete = User.objects.filter(email__in=test_emails)
        else:
            raise CommandError(
                "Vous devez spécifier au moins une option : "
                "--email, --emails, --inactive, ou --test-accounts.\n"
                "Utilisez --help pour plus de détails."
            )

        # Protection des superutilisateurs
        if keep_superusers:
            superusers_protected = users_to_delete.filter(is_superuser=True)
            if superusers_protected.exists():
                self.stdout.write(self.style.WARNING(
                    f"🛡️  {superusers_protected.count()} superutilisateur(s) protégé(s) et exclu(s) : "
                    f"{', '.join(superusers_protected.values_list('email', flat=True))}"
                ))
            users_to_delete = users_to_delete.filter(is_superuser=False)

        count = users_to_delete.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS("✅ Aucun compte correspondant trouvé. Rien à supprimer."))
            return

        # Afficher les détails
        self.stdout.write(self.style.WARNING(
            f"\n{'🔍 SIMULATION' if dry_run else '🗑️  SUPPRESSION'} — {count} compte(s) trouvé(s) :\n"
        ))

        for user in users_to_delete.select_related('profile'):
            role = "—"
            try:
                role = user.profile.get_role_display()
            except Exception:
                pass

            teacher_info = ""
            try:
                tp = user.teacherprofile
                diplomes_count = tp.diplomes.count()
                teacher_info = f" | Profil Prof: {tp.nom} {tp.prenom} | {diplomes_count} diplôme(s)"
            except Exception:
                pass

            status = "✅ Actif" if user.is_active else "❌ Inactif"
            self.stdout.write(
                f"  • {user.email} ({user.username}) — {role} — {status}{teacher_info}"
            )

        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"\n🔍 Simulation terminée. Aucune donnée n'a été supprimée."
                f"\n   Relancez sans --dry-run pour effectuer la suppression."
            ))
            return

        # Confirmation interactive
        self.stdout.write("")
        confirm = input(f"⚠️  Confirmer la suppression de {count} compte(s) et TOUTES leurs données ? [oui/non] : ")
        if confirm.lower() not in ('oui', 'o', 'yes', 'y'):
            self.stdout.write(self.style.WARNING("❌ Suppression annulée."))
            return

        # Suppression (CASCADE s'occupe de tout)
        deleted_count, deleted_details = users_to_delete.delete()

        self.stdout.write(self.style.SUCCESS(f"\n✅ {deleted_count} objet(s) supprimé(s) au total :"))
        for model_label, obj_count in deleted_details.items():
            self.stdout.write(f"   • {model_label}: {obj_count}")

        self.stdout.write(self.style.SUCCESS("\n🎉 Purge terminée avec succès !"))
