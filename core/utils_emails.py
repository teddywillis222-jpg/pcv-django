import threading
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import Profile

class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list, from_email=None):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        self.from_email = from_email or settings.DEFAULT_FROM_EMAIL
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMultiAlternatives(
            subject=self.subject,
            body="Bonjour,\n\nVotre client de messagerie ne supporte pas le HTML.",
            from_email=self.from_email,
            to=self.recipient_list
        )
        msg.attach_alternative(self.html_content, "text/html")
        try:
            msg.send(fail_silently=False)
        except Exception as e:
            print(f"Erreur d'envoi d'email à {self.recipient_list} : {e}")

def send_welcome_email_async(user, profile):
    """
    Détermine le bon template selon le rôle et envoie l'email en arrière-plan.
    """
    subject = "Bienvenue sur Prof Chez Vous !"
    
    # Détermination du template en fonction du rôle
    if profile.role == Profile.ROLE_PARENT:
        template_name = "emails/welcome_parent.html"
    elif profile.role == Profile.ROLE_APPRENANT:
        template_name = "emails/welcome_apprenant.html"
    elif profile.role == Profile.ROLE_PROF:
        template_name = "emails/welcome_teacher.html"
        subject = "Bienvenue sur Prof Chez Vous - Complétez votre profil"
    else:
        # Fallback pour un utilisateur sans rôle défini
        return
        
    context = {
        'user': user,
        'profile': profile,
    }
    
    html_content = render_to_string(template_name, context)
    
    # Envoi asynchrone
    EmailThread(subject, html_content, [user.email]).start()
