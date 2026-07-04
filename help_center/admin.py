from django.contrib import admin
from .models import Category, Article

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'target_audience')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('target_audience',)
    ordering = ('order', 'name')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'views', 'is_published', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('is_published', 'category')
    search_fields = ('title', 'content', 'keywords')
    autocomplete_fields = ('category',)
    filter_horizontal = ('related_articles',)
    readonly_fields = ('views', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'slug', 'category', 'content')
        }),
        ('Méta-données & Recherche', {
            'fields': ('keywords', 'related_articles')
        }),
        ('Publication & Stats', {
            'fields': ('is_published', 'views', 'created_at', 'updated_at')
        }),
    )
