from django.core.management.base import BaseCommand
from core.models import Engagement
from core.choices import StatutGeneral, EngagementType

class Command(BaseCommand):
    help = "Vérifie les essais confirmés et les passe à réalisés si l'heure est dépassée, puis envoie l'email."

    def handle(self, *args, **options):
        engagements = Engagement.objects.filter(
            type_engagement=EngagementType.ESSAI,
            statut_general=StatutGeneral.ESSAI_CONFIRME,
            date_heure_essai__isnull=False
        )

        count = 0
        for eng in engagements:
            # check_and_update_essai_status envoie automatiquement l'email si le statut est mis à jour
            if eng.check_and_update_essai_status():
                count += 1
                self.stdout.write(self.style.SUCCESS(f'Essai {eng.id} passé à RÉALISÉ et email envoyé.'))

        self.stdout.write(self.style.SUCCESS(f'Terminé ! {count} essais mis à jour.'))
