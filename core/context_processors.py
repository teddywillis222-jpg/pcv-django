from django.conf import settings
from .choices import Matiere, ClassLevel, CourseMode, SupportCategory, PriceRange
from .models import Quartier

def global_choices(request):
    """Fournit les choix standardisés à tous les templates."""
    quartiers = Quartier.objects.all().order_by('ville', 'nom')
    return {
        'LOCALISATION_CHOICES': [(q.id, q.nom) for q in quartiers],
        'quartiers_all': quartiers,
        'MATIERE_LISTE': Matiere.LISTE,
        'MATIERE_CHOICES': Matiere.get_choices(),
        'CLASS_LEVEL_CHOICES': ClassLevel.get_choices(),
        'COURSE_MODE_CHOICES': CourseMode.CHOICES,
        'SUPPORT_CATEGORY_CHOICES': SupportCategory.CHOICES,
        'PRICE_RANGE_CHOICES': PriceRange.CHOICES,
        'SITE_DOMAIN': settings.SITE_DOMAIN,
    }

