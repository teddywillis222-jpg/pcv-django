
# Ajout de la route pour le CRON externe
from .views import api_cron_check_essais
urlpatterns += [
    path('api/cron/check-essais/', api_cron_check_essais, name='api_cron_check_essais'),
]
