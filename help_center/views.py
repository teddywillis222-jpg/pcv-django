from django.shortcuts import render, get_object_or_404
from django.db.models import Q, F
from django.http import JsonResponse
from .models import Category, Article

def help_home(request):
    popular_articles = Article.objects.filter(is_published=True).order_by('-views')[:6]
    latest_articles = Article.objects.filter(is_published=True).order_by('-updated_at')[:4]
    categories = Category.objects.all().order_by('order')
    
    context = {
        'popular_articles': popular_articles,
        'latest_articles': latest_articles,
        'categories': categories,
    }
    return render(request, 'help_center/home.html', context)

def category_detail(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    articles = category.articles.filter(is_published=True)
    return render(request, 'help_center/category.html', {'category': category, 'articles': articles})

def article_detail(request, category_slug, article_slug):
    category = get_object_or_404(Category, slug=category_slug)
    article = get_object_or_404(Article, slug=article_slug, category=category, is_published=True)
    
    # Incrémentation des vues de manière atomique
    Article.objects.filter(pk=article.pk).update(views=F('views') + 1)
    
    # Récupérer les articles liés s'il y en a
    related_articles = article.related_articles.filter(is_published=True)[:5]
    
    return render(request, 'help_center/article.html', {'article': article, 'category': category, 'related_articles': related_articles})

def api_search_articles(request):
    query = request.GET.get('q', '').strip()
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
        
    articles = Article.objects.filter(is_published=True).filter(
        Q(title__icontains=query) |
        Q(content__icontains=query) |
        Q(keywords__icontains=query)
    ).order_by('-views')[:8]
    
    results = [
        {
            'id': article.id,
            'title': article.title,
            'url': f"/centre-daide/{article.category.slug}/{article.slug}/",
            'category': article.category.name
        }
        for article in articles
    ]
    
    return JsonResponse({'results': results})
