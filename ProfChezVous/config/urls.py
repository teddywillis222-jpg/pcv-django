"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.account.urls")),
    path("", core_views.home, name="home"),
    path("signup/", core_views.signup, name="signup"),
    path("login/", core_views.login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("post-signup/", core_views.post_signup_redirect, name="post_signup_redirect"),
    path("finalisation-compte/", core_views.finalisation_compte, name="finalisation_compte"),
    path("prof-intro/", core_views.prof_intro, name="prof_intro"),
    path("prof/create-profile/", core_views.prof_create_profile, name="prof_create_profile"),
    path("prof/attente/", core_views.prof_attente_dashboard, name="prof_attente_dashboard"),
    path("prof/dashboard/", core_views.prof_dashboard, name="prof_dashboard"),
    path("parent/create-profile/", core_views.parent_create_profile, name="parent_create_profile"),
    path("parent/dashboard/", core_views.parent_dashboard, name="parent_dashboard"),
    path("apprenant/create-profile/", core_views.apprenant_create_profile, name="apprenant_create_profile"),
    path("apprenant/dashboard/", core_views.apprenant_dashboard, name="apprenant_dashboard"),
    
    # Nouvelles URLs pour la navigation principale
    path("faq/", core_views.faq, name="faq"),
    path("support/", core_views.support, name="support"),
    path("messagerie/", core_views.messagerie, name="messagerie"),
    path("recherche/", core_views.recherche, name="recherche"),
    path("cgu/", core_views.cgu, name="cgu"),
    
    # URLs pour le système de recherche et profils (SEO + SPA)
    path("professeur/<slug:teacher_slug>/", core_views.professeur_detail, name="professeur_detail"),
    path("api/teacher-profile/<slug:teacher_slug>/", core_views.api_teacher_profile, name="api_teacher_profile"),
    path("api/engagement/", core_views.api_engagement, name="api_engagement"),

    # Admin Dashboard PCV (Test Route)
    path("debug-admin-pcv/", core_views.debug_admin_pcv, name="debug_admin_pcv"),
    path("debug-admin-pcv/api/accueil/", core_views.admin_api_accueil, name="admin_api_accueil"),
    path("debug-admin-pcv/api/professeurs/", core_views.admin_api_professeurs, name="admin_api_professeurs"),
    path("debug-admin-pcv/api/professeurs/<int:prof_id>/action/", core_views.admin_api_prof_action, name="admin_api_prof_action"),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

