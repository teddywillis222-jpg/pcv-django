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

        elif profile.role == Profile.ROLE_APPRENANT:
            try:
                request.user.apprenant
            except Apprenant.DoesNotExist:
                if url_name != "apprenant_create_profile":
                    return redirect("apprenant_create_profile")

        return self.get_response(request)
