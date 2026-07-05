from django.shortcuts import render, get_object_or_404
from django.db.models import Q, F, Count
from django.http import JsonResponse
from .models import Category, Article

def help_home(request):
    popular_articles = Article.objects.filter(is_published=True).order_by('-views')[:6]
    latest_articles = Article.objects.filter(is_published=True).order_by('-updated_at')[:4]
    categories = Category.objects.annotate(
        published_articles_count=Count('articles', filter=Q(articles__is_published=True))
    ).order_by('order')
    
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
    
    # Récupérer les articles liés s'il y en a (définis manuellement)
    related_articles = list(article.related_articles.filter(is_published=True)[:3])
    
    # Si pas assez d'articles liés manuellement, utiliser les mots-clés pour trouver des similarités
    if len(related_articles) < 3 and article.keywords:
        import operator
        from functools import reduce
        keywords_list = [k.strip() for k in article.keywords.split(',') if len(k.strip()) > 3]
        if keywords_list:
            # Recherche des articles contenant l'un des mots clés
            query = reduce(operator.or_, (Q(keywords__icontains=k) | Q(title__icontains=k) for k in keywords_list))
            similar_articles = Article.objects.filter(is_published=True).filter(query).exclude(id=article.id).exclude(id__in=[a.id for a in related_articles]).distinct()
            # On complète jusqu'à 3
            needed = 3 - len(related_articles)
            related_articles.extend(list(similar_articles[:needed]))
            
    # Fallback final sur les articles les plus vus de la même catégorie
    if len(related_articles) < 3:
        needed = 3 - len(related_articles)
        cat_articles = category.articles.filter(is_published=True).exclude(id=article.id).exclude(id__in=[a.id for a in related_articles]).order_by('-views')[:needed]
        related_articles.extend(list(cat_articles))
    
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
