from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import TeacherProfile
from .choices import ValidationStatus

class StaticViewSitemap(Sitemap):

    def items(self):
        # Liste blanche explicite : garantit qu'aucune page privée/auth ne fuité
        return [
            'home', 
            'recherche', 
            'prof_intro', 
            'faq', 
            'charte_essai',
            'support', 
            'cgu', 
            'politique_confidentialite'
        ]

    def location(self, item):
        return reverse(item)

    def changefreq(self, item):
        freqs = {
            'home': 'weekly',
            'recherche': 'daily',
            'prof_intro': 'monthly',
            'faq': 'monthly',
            'charte_essai': 'monthly',
            'support': 'monthly',
            'cgu': 'yearly',
            'politique_confidentialite': 'yearly',
        }
        return freqs.get(item, 'monthly')

    def priority(self, item):
        priorities = {
            'home': 1.0,
            'recherche': 0.9,
            'prof_intro': 0.8,
            'faq': 0.9,
            'charte_essai': 0.8,
            'support': 0.6,
            'cgu': 0.4,
            'politique_confidentialite': 0.4,
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

class SeoDirectorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        """Retourne toutes les combinaisons possibles de matières et de villes"""
        from .choices import Matiere, Localisation
        from django.utils.text import slugify
        
        combinations = []
        for mat in Matiere.LISTE:
            for loc_key, loc_val in Localisation.CHOICES:
                combinations.append({
                    'subject_slug': slugify(mat),
                    'city_slug': slugify(loc_val)
                })
        return combinations

    def location(self, item):
        return reverse('seo_directory', kwargs={
            'subject_slug': item['subject_slug'],
            'city_slug': item['city_slug']
        })

