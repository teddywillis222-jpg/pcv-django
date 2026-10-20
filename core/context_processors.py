from django.conf import settings
from django.core.cache import cache
from .choices import Matiere, ClassLevel, CourseMode, SupportCategory, PriceRange
from .models import Quartier, SiteConfiguration

CACHE_KEY_QUARTIERS = 'global_choices_quartiers_list'
CACHE_KEY_SITE_CONFIG = 'global_choices_site_config_obj'
CACHE_TIMEOUT_SECONDS = 7200  # 2 heures

def global_choices(request):
    """
    Fournit les choix standardisés à tous les templates.
    Optimisé pour Neon Serverless avec mise en cache mémoire (évite 2 requêtes SQL par vue).
    """
    quartiers = cache.get(CACHE_KEY_QUARTIERS)
    if quartiers is None:
        quartiers = list(Quartier.objects.all().order_by('ville', 'nom'))
        cache.set(CACHE_KEY_QUARTIERS, quartiers, CACHE_TIMEOUT_SECONDS)

    site_config = cache.get(CACHE_KEY_SITE_CONFIG)
    if site_config is None:
        site_config = SiteConfiguration.get_solo()
        cache.set(CACHE_KEY_SITE_CONFIG, site_config, CACHE_TIMEOUT_SECONDS)

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
        'site_config': site_config,
    }
