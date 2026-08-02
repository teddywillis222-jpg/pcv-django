from django.conf import settings
from .choices import Localisation, Matiere, ClassLevel, CourseMode, SupportCategory, PriceRange

def global_choices(request):
    """Fournit les choix standardisés à tous les templates."""
    return {
        'LOCALISATION_CHOICES': Localisation.get_choices(),
        'MATIERE_LISTE': Matiere.LISTE,
        'MATIERE_CHOICES': Matiere.get_choices(),
        'CLASS_LEVEL_CHOICES': ClassLevel.get_choices(),
        'COURSE_MODE_CHOICES': CourseMode.CHOICES,
        'SUPPORT_CATEGORY_CHOICES': SupportCategory.CHOICES,
        'PRICE_RANGE_CHOICES': PriceRange.CHOICES,
        'SITE_DOMAIN': settings.SITE_DOMAIN,
    }
