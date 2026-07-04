from django.urls import path
from . import views

app_name = 'help_center'

urlpatterns = [
    path('', views.help_home, name='home'),
    path('api/search/', views.api_search_articles, name='api_search'),
    path('<slug:category_slug>/', views.category_detail, name='category_detail'),
    path('<slug:category_slug>/<slug:article_slug>/', views.article_detail, name='article_detail'),
]
