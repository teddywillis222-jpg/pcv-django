from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import TeacherProfile
from .choices import ValidationStatus

class StaticViewSitemap(Sitemap):
    changefreq = 'weekly'

    def items(self):
        # Liste blanche explicite : garantit qu'aucune page privée/auth ne fuité
        return [
            'home', 
            'recherche', 
            'prof_intro', 
            'faq', 
            'support', 
            'cgu', 
            'politique_confidentialite'
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        priorities = {
            'home': 1.0,
            'recherche': 0.8,
            'prof_intro': 0.8,
            'faq': 0.6,
            'support': 0.6,
            'cgu': 0.5,
            'politique_confidentialite': 0.5,
        }
        return priorities.get(item, 0.5)

class TeacherProfileSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        # Filtre strict : uniquement les profils avec le statut VALIDE
        return TeacherProfile.objects.filter(
            statut_de_validation=ValidationStatus.VALIDE
        ).order_by('-user__date_joined')

    def lastmod(self, obj):
        # On utilise la date de jointure de l'utilisateur ou une date fixe si non dispo
        return obj.user.date_joined
