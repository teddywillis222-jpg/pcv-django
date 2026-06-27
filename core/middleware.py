"""Middleware : garde vérifiant la complétion du profil avant accès au dashboard."""

from django.shortcuts import redirect
from django.urls import resolve

from .models import Apprenant, Enfant, Parent, Profile


EXEMPT_URLS = [
    "home",
    "signup",
    "login",
    "logout",
    "finalisation_compte",
    "post_signup_redirect",
    "prof_intro",
]

# django-allauth
EXEMPT_PATH_PREFIXES = ["/accounts/"]


class ProfileCompletionMiddleware:
    """
    Redirige vers la page d'onboarding si le profil n'est pas complet.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        if request.path.startswith("/admin/"):
            return self.get_response(request)
        if any(request.path.startswith(p) for p in EXEMPT_PATH_PREFIXES):
            return self.get_response(request)

        try:
            url_name = resolve(request.path).url_name
        except Exception:
            url_name = None

        if url_name in EXEMPT_URLS:
            return self.get_response(request)

        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            if url_name != "finalisation_compte":
                return redirect("finalisation_compte")
            return self.get_response(request)

        if not request.user.first_name or not str(request.user.first_name).strip():
            return redirect("finalisation_compte")

        # Vérifier selon le rôle
        if profile.role == Profile.ROLE_PARENT:
            try:
                parent = request.user.parent
            except Parent.DoesNotExist:
                if url_name != "parent_create_profile":
                    return redirect("parent_create_profile")
            else:
                if not parent.enfants.exists() and url_name not in ("parent_create_profile",):
                    return redirect("parent_create_profile")

        elif profile.role == Profile.ROLE_PROF:
            from .models import TeacherProfile
            from .choices import ValidationStatus
            try:
                teacher = request.user.teacher_profile
                if getattr(teacher, 'statut_de_validation', None) == ValidationStatus.INCOMPLET:
                    if url_name not in ("prof_create_profile", "logout", "finalisation_compte", "post_signup_redirect", "prof_intro"):
                        return redirect("prof_create_profile")
            except TeacherProfile.DoesNotExist:
                if url_name not in ("prof_create_profile",) + tuple(EXEMPT_URLS):
                    return redirect("prof_create_profile")

        elif profile.role == Profile.ROLE_APPRENANT:
            try:
                request.user.apprenant
            except Apprenant.DoesNotExist:
                if url_name != "apprenant_create_profile":
                    return redirect("apprenant_create_profile")

        return self.get_response(request)

from django.http import HttpResponse
from django.conf import settings

class MaintenanceMiddleware:
    """
    Middleware qui intercepte TOUTES les requêtes et renvoie une page de maintenance HTML pure
    si MAINTENANCE_MODE est True dans settings.py, sans faire AUCUN appel à la base de données.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, 'MAINTENANCE_MODE', False):
            # Page HTML statique pour ne pas dépendre de la base de données ni du moteur de template
            html_content = """
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Maintenance - Prof Chez Vous</title>
                <style>
                    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; color: #1e293b; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; padding: 20px; box-sizing: border-box; }
                    .container { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); max-width: 600px; width: 100%; border-top: 6px solid #10b981; }
                    h1 { color: #0f172a; margin-top: 0; font-size: 24px; font-weight: 800; }
                    p { line-height: 1.6; color: #475569; font-size: 16px; margin-bottom: 24px; }
"""Middleware : garde vérifiant la complétion du profil avant accès au dashboard."""

from django.shortcuts import redirect
from django.urls import resolve

from .models import Apprenant, Enfant, Parent, Profile


EXEMPT_URLS = [
    "home",
    "signup",
    "login",
    "logout",
    "finalisation_compte",
    "post_signup_redirect",
    "prof_intro",
]

# django-allauth
EXEMPT_PATH_PREFIXES = ["/accounts/"]


class ProfileCompletionMiddleware:
    """
    Redirige vers la page d'onboarding si le profil n'est pas complet.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        if request.path.startswith("/admin/"):
            return self.get_response(request)
        if any(request.path.startswith(p) for p in EXEMPT_PATH_PREFIXES):
            return self.get_response(request)

        try:
            url_name = resolve(request.path).url_name
        except Exception:
            url_name = None

        if url_name in EXEMPT_URLS:
            return self.get_response(request)

        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            if url_name != "finalisation_compte":
                return redirect("finalisation_compte")
            return self.get_response(request)

        if not request.user.first_name or not str(request.user.first_name).strip():
            return redirect("finalisation_compte")

        # Vérifier selon le rôle
        if profile.role == Profile.ROLE_PARENT:
            try:
                parent = request.user.parent
            except Parent.DoesNotExist:
                if url_name != "parent_create_profile":
                    return redirect("parent_create_profile")
            else:
                if not parent.enfants.exists() and url_name not in ("parent_create_profile",):
                    return redirect("parent_create_profile")

        elif profile.role == Profile.ROLE_PROF:
            from .models import TeacherProfile
            from .choices import ValidationStatus
            try:
                teacher = request.user.teacher_profile
                if getattr(teacher, 'statut_de_validation', None) == ValidationStatus.INCOMPLET:
                    if url_name not in ("prof_create_profile", "logout", "finalisation_compte", "post_signup_redirect", "prof_intro"):
                        return redirect("prof_create_profile")
            except TeacherProfile.DoesNotExist:
                if url_name not in ("prof_create_profile",) + tuple(EXEMPT_URLS):
                    return redirect("prof_create_profile")

        elif profile.role == Profile.ROLE_APPRENANT:
            try:
                request.user.apprenant
            except Apprenant.DoesNotExist:
                if url_name != "apprenant_create_profile":
                    return redirect("apprenant_create_profile")

        return self.get_response(request)

from django.http import HttpResponse
from django.conf import settings

class MaintenanceMiddleware:
    """
    Middleware qui intercepte TOUTES les requêtes et renvoie une page de maintenance HTML pure
    si MAINTENANCE_MODE est True dans settings.py, sans faire AUCUN appel à la base de données.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, 'MAINTENANCE_MODE', False):
            # Page HTML statique pour ne pas dépendre de la base de données ni du moteur de template
            html_content = """
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Maintenance - Prof Chez Vous</title>
                <style>
                    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; color: #1e293b; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; padding: 20px; box-sizing: border-box; }
                    .container { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); max-width: 600px; width: 100%; border-top: 6px solid #10b981; }
                    h1 { color: #0f172a; margin-top: 0; font-size: 24px; font-weight: 800; }
                    p { line-height: 1.6; color: #475569; font-size: 16px; margin-bottom: 24px; }
                    .action-box { background: #f0fdf4; border: 1px solid #bbf7d0; padding: 20px; border-radius: 12px; text-align: left; margin-top: 20px; }
                    .action-box h3 { margin: 0 0 10px 0; color: #166534; font-size: 16px; }
                    .action-box p { margin: 0; font-size: 15px; color: #15803d; }
                    svg { width: 64px; height: 64px; color: #10b981; margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <h1>Améliorations en cours !</h1>
                    <p>Prof Chez Vous est temporairement indisponible. Nous effectuons une mise à niveau technique majeure pour vous offrir une plateforme encore plus rapide et performante.</p>
                    <p><strong>Nous serons de retour en ligne le 2 Juillet.</strong></p>
                    
                    <div class="action-box">
                        <h3>📣 Message spécial pour nos Professeurs :</h3>
                        <p>Profitez de cette courte pause pour vous préparer !<br>
                        • <strong>Nouveaux venus :</strong> Rassemblez vos documents (photo pro, diplômes, pièce d'identité) pour une validation rapide à 100%.<br>
                        • <strong>Professeurs actifs :</strong> Préparez-vous à recevoir de nouvelles missions. Dès la réouverture, une grande campagne sera lancée pour vous confier de nouveaux élèves !</p>
                    </div>
                </div>
            </body>
            </html>
            """
            return HttpResponse(html_content, status=503)
            
        return self.get_response(request)
