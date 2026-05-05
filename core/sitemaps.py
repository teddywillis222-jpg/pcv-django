from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import TeacherProfile
from .choices import ValidationStatus

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['home', 'recherche', 'faq', 'support', 'cgu', 'politique_confidentialite']

    def location(self, item):
        return reverse(item)

class TeacherProfileSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return TeacherProfile.objects.filter(statut_de_validation=ValidationStatus.VALIDE).order_by('-user__date_joined')

    def lastmod(self, obj):
        # On utilise la date de jointure de l'utilisateur ou une date fixe si non dispo
        return obj.user.date_joined
