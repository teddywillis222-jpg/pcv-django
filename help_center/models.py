from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Description courte")
    icon = models.CharField(max_length=50, blank=True, help_text="Classe CSS de l'icône (ex: bi bi-person)", verbose_name="Icône")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    target_audience = models.CharField(
        max_length=20, 
        choices=[('all', 'Tous'), ('parents', 'Parents & Apprenants'), ('teachers', 'Professeurs')],
        default='all',
        verbose_name="Public cible"
    )

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre de l'article")
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, related_name='articles', on_delete=models.CASCADE, verbose_name="Catégorie")
    content = models.TextField(verbose_name="Contenu de l'article")
    keywords = models.CharField(max_length=255, blank=True, help_text="Mots-clés pour la recherche, séparés par des virgules", verbose_name="Mots-clés")
    
    views = models.PositiveIntegerField(default=0, verbose_name="Nombre de vues")
    is_published = models.BooleanField(default=True, verbose_name="Publié")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    related_articles = models.ManyToManyField('self', blank=True, symmetrical=False, verbose_name="Articles liés")

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
