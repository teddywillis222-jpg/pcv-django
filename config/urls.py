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
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap, TeacherProfileSitemap, SeoDirectorySitemap

from core import views as core_views
from django.views.generic import TemplateView

sitemaps = {
    'static': StaticViewSitemap,
    'teachers': TeacherProfileSitemap,
    'seo_directories': SeoDirectorySitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('', include('referrals.urls')),
    path("accounts/", include("allauth.account.urls")),
    path("", core_views.home, name="home"),
    path("signup/", core_views.signup, name="signup"),
    path("activate/<uidb64>/<token>/", core_views.activate_account, name="activate_account"),
    path("login/", core_views.login_view, name="login"),
    path("renvoyer-activation/", core_views.resend_activation_view, name="resend_activation"),
    path("api/search-alert/", core_views.create_search_alert, name="create_search_alert"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    
    # Password Reset
    path('reset_password/', auth_views.PasswordResetView.as_view(
        template_name="core/password_reset.html",
        email_template_name="core/password_reset_email.html",
        subject_template_name="core/password_reset_subject.txt",
        success_url="/reset_password_sent/",
        html_email_template_name="core/password_reset_email.html",
        extra_email_context={'protocol': 'https', 'domain': 'profchezvousapp.com'}
    ), name="password_reset"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(
        template_name="core/password_reset_done.html"
    ), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="core/password_reset_confirm.html",
        success_url="/reset_password_complete/"
    ), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name="core/password_reset_complete.html"
    ), name="password_reset_complete"),
    path("post-signup/", core_views.post_signup_redirect, name="post_signup_redirect"),
    path("finalisation-compte/", core_views.finalisation_compte, name="finalisation_compte"),
    path("prof-intro/", core_views.prof_intro, name="prof_intro"),
    path("prof/create-profile/", core_views.prof_create_profile, name="prof_create_profile"),
    path("prof/attente/", core_views.prof_attente_dashboard, name="prof_attente_dashboard"),
    path("prof/dashboard/", core_views.prof_dashboard, name="prof_dashboard"),
    path("prof/edit-profile/", core_views.prof_edit_profile, name="prof_edit_profile"),
    path("prof/video-presentation/", core_views.prof_video_presentation, name="prof_video_presentation"),
    path("prof/stats/", core_views.prof_stats_view, name="prof_stats"),
    path("api/prof/popup-partage-vu/", core_views.api_mark_popup_partage_vu, name="api_mark_popup_partage_vu"),
    path("parent/create-profile/", core_views.parent_create_profile, name="parent_create_profile"),
    path("parent/dashboard/", core_views.parent_dashboard, name="parent_dashboard"),
    path("apprenant/create-profile/", core_views.apprenant_create_profile, name="apprenant_create_profile"),
    path("apprenant/dashboard/", core_views.apprenant_dashboard, name="apprenant_dashboard"),
    path("mon-plan/", core_views.gestion_plan, name="gestion_plan"),
    path("mon-plan/downgrade/", core_views.downgrade_to_standard, name="downgrade_to_standard"),

    path("profil-eleve/<str:type_eleve>/<int:id_eleve>/", core_views.profil_eleve, name="profil_eleve"),
    path("enfant/<int:id_enfant>/edit/", core_views.edit_enfant, name="edit_enfant"),
    
    path("test-ui-cards/", core_views.test_ui_cards, name="test_ui_cards"),

    # Nouvelles URLs pour la navigation principale
    path("faq/", core_views.faq, name="faq"),
    path("support/", core_views.support, name="support"),
    path("ressources-professeurs/", core_views.ressources_professeurs_view, name="ressources_professeurs"),
    path("ressources-professeurs/<int:res_id>/download/", core_views.download_ressource_prof, name="download_ressource_prof"),
    path("messagerie/", core_views.messagerie, name="messagerie"),
    path("messagerie/<int:conversation_id>/", core_views.conversation_detail, name="conversation_detail"),
    path("messagerie/<int:conversation_id>/send/", core_views.api_send_message, name="api_send_message"),
    path("messagerie/<int:conversation_id>/fetch/", core_views.api_fetch_new_messages, name="api_fetch_new_messages"),
    path("messagerie/<int:conversation_id>/archive/", core_views.api_archive_conversation, name="api_archive_conversation"),
    path("messagerie/<int:conversation_id>/delete/", core_views.api_delete_conversation, name="api_delete_conversation"),
    path("recherche/", core_views.recherche, name="recherche"),
    path("cgu/", core_views.cgu, name="cgu"),
    path("politique-confidentialite/", core_views.politique_confidentialite, name="politique_confidentialite"),
    
    # URLs pour le système de recherche et profils (SEO + SPA)
    path("cours/<slug:subject_slug>/<slug:city_slug>/", core_views.seo_directory_page, name="seo_directory"),
    path("professeur/<slug:teacher_slug>/", core_views.professeur_detail, name="professeur_detail"),
    path("api/teacher-profile/<slug:teacher_slug>/", core_views.api_teacher_profile, name="api_teacher_profile"),
    path("api/engagement/", core_views.api_engagement, name="api_engagement"),
    path("api/engagement/<int:engagement_id>/action/", core_views.api_engagement_action, name="api_engagement_action"),
    path("api/engagement/<int:engagement_id>/update/", core_views.api_update_engagement, name="api_update_engagement"),
    path("api/engagement/<int:engagement_id>/finalize/", core_views.api_finalize_engagement, name="api_finalize_engagement"),
    path("api/engagement/<int:engagement_id>/details/", core_views.api_engagement_details, name="api_engagement_details"),
    path("api/engagement/<int:engagement_id>/rate/", core_views.api_rate_professeur, name="api_rate_professeur"),
    path("api/engagement/<int:engagement_id>/demander-annulation/", core_views.api_demander_annulation, name="api_demander_annulation"),
    path("api/engagement/<int:engagement_id>/demander-cloture/", core_views.api_demander_cloture, name="api_demander_cloture"),
    path("api/engagement/<int:eng_id>/masquer/", core_views.masquer_engagement, name="masquer_engagement"),
    path("api/engagement/<int:eng_id>/masquer-prof/", core_views.masquer_engagement_prof, name="masquer_engagement_prof"),
    path("finalisation-engagement/<int:engagement_id>/", core_views.finalisation_engagement, name="finalisation_engagement"),
    
    path("api/professeur/<int:prof_id>/toggle-favori/", core_views.toggle_favori, name="toggle_favori"),
    path("api/professeur/<int:prof_id>/toggle-reaction/", core_views.toggle_reaction, name="toggle_reaction"),
    path("api/professeur/toggle-essai/", core_views.api_toggle_essai, name="api_toggle_essai"),
    path("api/fictional-payment/", core_views.api_fictional_payment, name="api_fictional_payment"),
    path("api/track-teacher-views/", core_views.api_track_teacher_views, name="api_track_teacher_views"),

    # FedaPay Engagement
    path("paiement/initier/<int:engagement_id>/", core_views.payer_engagement, name="payer_engagement"),
    path("paiement/callback/", core_views.fedapay_callback, name="fedapay_callback"),
    path("paiement/succes/<int:engagement_id>/", core_views.paiement_succes, name="paiement_succes"),
    path("paiement/echec/<int:engagement_id>/", core_views.paiement_echec, name="paiement_echec"),
    
    # FedaPay Premium
    path("paiement/premium/initier/", core_views.payer_premium, name="payer_premium"),
    path("paiement/premium/callback/", core_views.fedapay_premium_callback, name="fedapay_premium_callback"),


    # Suivi Pédagogique
    path("engagement/<int:engagement_id>/suivi/", core_views.suivi_engagement, name="suivi_engagement"),
    path("engagement/<int:engagement_id>/seances/", core_views.toutes_seances, name="toutes_seances"),
    path("api/engagement/<int:engagement_id>/ajouter-seance/", core_views.api_ajouter_seance, name="api_ajouter_seance"),
    path("api/seance/<int:seance_id>/valider/", core_views.api_valider_seance, name="api_valider_seance"),

    # Admin Dashboard PCV (Test Route)
    path("debug-admin-pcv/", core_views.debug_admin_pcv, name="debug_admin_pcv"),
    path("debug-admin-pcv/api/accueil/", core_views.admin_api_accueil, name="admin_api_accueil"),
    path("debug-admin-pcv/api/professeurs/", core_views.admin_api_professeurs, name="admin_api_professeurs"),
    path("debug-admin-pcv/api/professeurs/<int:prof_id>/action/", core_views.admin_api_prof_action, name="admin_api_prof_action"),
    
    # Nouvelles API pour l'admin custom (Ressources & FAQ)
    path("debug-admin-pcv/api/ressources/", core_views.admin_api_ressources, name="admin_api_ressources"),
    path("debug-admin-pcv/api/faqs/", core_views.admin_api_faqs, name="admin_api_faqs"),
    path("debug-admin-pcv/api/ressources/action/", core_views.admin_api_ressources_action, name="admin_api_ressources_action"),
    path("debug-admin-pcv/api/faqs/action/", core_views.admin_api_faqs_action, name="admin_api_faqs_action"),
    
    # API pour l'admin custom (Programme Ambassadeur)
    path("debug-admin-pcv/api/ambassadeurs/", core_views.admin_api_ambassadeurs, name="admin_api_ambassadeurs"),
    path("debug-admin-pcv/api/ambassadeurs/action/", core_views.admin_api_ambassadeurs_action, name="admin_api_ambassadeurs_action"),
    
    # Temps Réel et Popup
    path("api/ping/", core_views.api_ping, name="api_ping"),
    path("api/mark-welcome-seen/", core_views.api_mark_welcome_seen, name="api_mark_welcome_seen"),
    path("api/announcement/<int:pk>/dismiss/", core_views.dismiss_announcement, name="dismiss_announcement"),
    
    # Charte Essai Gratuit
    path("charte-essai-gratuit/", core_views.charte_essai_gratuit, name="charte_essai"),
    
    # Interface Admin Custom
    path("admin-outils/creer-annonce/", core_views.create_announcement, name="create_announcement"),

    # Help Center
    path("centre-daide/", include("help_center.urls")),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

