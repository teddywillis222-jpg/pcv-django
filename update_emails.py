import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

path = 'core/utils_emails.py'
text = open(path, 'r', encoding='utf-8').read()

# REWRITE send_essai_confirmed_email
old_confirmed = r'def send_essai_confirmed_email\(parent_user, engagement\):.*?return True'

new_confirmed = '''def send_essai_confirmed_email(parent_user, engagement):
    """
    Email envoyé au parent ou apprenant lorsque le professeur confirme le cours d'essai.
    """
    if not parent_user.email:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("Aucun email pour %s (id=%s), notification de confirmation d'essai ignorée.", parent_user.username, parent_user.pk)
        return False

    parent_email = parent_user.email
    parent_name = parent_user.first_name or "Cher(e) utilisateur"
    prof_name = f"{engagement.professeur.prenom} {engagement.professeur.nom}".strip() or "Votre professeur"
    matiere = engagement.matiere or "Non précisée"

    # Date et heure de l'essai
    date_str = ""
    if engagement.date_heure_essai:
        from django.utils import timezone as tz
        dt_local = tz.localtime(engagement.date_heure_essai)
        # Format simple (tu peux ajuster format_date_fr si nécessaire)
        # mais on utilise celui-là par defaut
        try:
            date_str = format_date_fr(dt_local)
        except NameError:
            date_str = dt_local.strftime('%d/%m/%Y à %H:%M')
    else:
        date_str = "Date non précisée"

    from django.urls import reverse
    
    # URL vers la messagerie (si applicable) ou le dashboard
    # S'il y a une conversation avec le prof, l'utilisateur la trouvera dans sa messagerie
    dashboard_url = get_full_url(reverse("parent_dashboard")) if hasattr(parent_user, 'parent') else get_full_url(reverse("apprenant_dashboard"))
    
    sujet = f"Cours d'essai confirmé avec {prof_name} !"
    is_parent = hasattr(parent_user, 'parent')
    
    if is_parent:
        prenom_enfant = "votre enfant"
        if engagement.enfants_concernes.exists():
            prenom_enfant = engagement.enfants_concernes.first().prenom
        
        message = f"""Bonjour {parent_name},

Bonne nouvelle ! {prof_name} vient de confirmer votre séance d'essai pour {prenom_enfant}.

📋 Récapitulatif :
Professeur : {prof_name}
Matière : {matiere}
Date et heure : {date_str}

Que faire maintenant ?
Accéder à la messagerie pour préciser le lieu exact de la séance avec le professeur.
Préparez les derniers devoirs ou chapitres où {prenom_enfant} rencontre des difficultés.

💡 Remarque : L'essai est entièrement gratuit. Si la séance est concluante, vous pourrez officialiser votre professeur via la formule Access+ (2 000 F/mois) pour débloquer le cahier de suivi de {prenom_enfant}.

👉 Discuter avec le professeur :
{dashboard_url}

Cordialement,
L'équipe Prof Chez Vous"""
    else:
        message = f"""Bonjour {parent_name},

Bonne nouvelle ! {prof_name} vient de confirmer votre séance d'essai.

📋 Récapitulatif :
Professeur : {prof_name}
Matière : {matiere}
Date et heure : {date_str}

Que faire maintenant ?
Accéder à la messagerie pour préciser le lieu exact de la séance avec le professeur.
Préparez les derniers devoirs ou chapitres où vous rencontrez des difficultés.

💡 Remarque : L'essai est entièrement gratuit. Si la séance est concluante, vous pourrez officialiser votre professeur via la formule Access+ (2 000 F/mois) pour débloquer votre cahier de suivi.

👉 Discuter avec le professeur :
{dashboard_url}

Cordialement,
L'équipe Prof Chez Vous"""

    try:
        from django.core.mail import send_mail
        from django.conf import settings
        send_mail(
            subject=sujet,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[parent_email],
            fail_silently=False,
        )
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Email de confirmation d'essai envoyé avec succès à %s.", parent_email)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error("Échec d'envoi de l'email de confirmation d'essai à %s : %s", parent_email, e, exc_info=True)
    return True'''


# REWRITE send_essai_realise_email
old_realise = r'def send_essai_realise_email\(parent_user, engagement\):.*?return False'

new_realise = '''def send_essai_realise_email(parent_user, engagement):
    """
    Email envoyé au parent ou apprenant lorsque l'essai passe au statut ESSAI_REALISE.
    """
    import logging
    logger = logging.getLogger(__name__)
    if not parent_user.email:
        logger.warning("Aucun email pour %s (id=%s), notification de réalisation d'essai ignorée.", parent_user.username, parent_user.pk)
        return False

    dest_email = parent_user.email
    prof_name = f"{engagement.professeur.prenom} {engagement.professeur.nom}".strip() or "Votre professeur"
    prenom_destinataire = parent_user.first_name or "Cher(e) utilisateur"
    
    # Bouton d'officialisation
    from django.urls import reverse
    officialiser_url = get_full_url(reverse("finalisation_engagement", args=[engagement.id]))
    
    is_parent = hasattr(parent_user, 'parent')

    if is_parent:
        prenom_enfant = "votre enfant"
        if engagement.enfants_concernes.exists():
            prenom_enfant = engagement.enfants_concernes.first().prenom

        sujet = f"Comment s'est passé l'essai de {prenom_enfant} ? 🎓"
        message = f"""Bonjour {prenom_destinataire},

La séance d'essai avec {prof_name} est marquée comme réalisée.

Si sa pédagogie vous convient, il est temps d'officialiser votre collaboration sur Prof Chez Vous pour engager le professeur dans la durée.

Pourquoi officialiser avec le Pass Access+ (2 000 FCFA / mois) ?
Obligation de Suivi : {prof_name} débloque son accès au Cahier de Suivi Digital et s'engage à vous transmettre un bilan après chaque cours.
Garantie Remplacement : Si le professeur n'est plus disponible ou ne convient plus, nous vous en trouvons un autre sans aucun frais supplémentaire.

💡 Remarque : Les cours eux-mêmes sont réglés directement au professeur selon ce que vous avez convenu ensemble.

👉 Officialiser la collaboration & Activer Access+ :
{officialiser_url}

L’équipe Prof Chez Vous"""
    else:
        sujet = "Comment s'est passé votre essai ? 🎓"
        message = f"""Bonjour {prenom_destinataire},

La séance d'essai avec {prof_name} est marquée comme réalisée.

Si sa pédagogie vous convient, il est temps d'officialiser votre collaboration sur Prof Chez Vous pour engager le professeur dans la durée.

Pourquoi officialiser avec le Pass Access+ (2 000 FCFA / mois) ?
Obligation de Suivi : {prof_name} débloque son accès au Cahier de Suivi Digital et s'engage à vous transmettre un bilan après chaque cours.
Garantie Remplacement : Si le professeur n'est plus disponible ou ne convient plus, nous vous en trouvons un autre sans aucun frais supplémentaire.

💡 Remarque : Les cours eux-mêmes sont réglés directement au professeur selon ce que vous avez convenu ensemble.

👉 Officialiser la collaboration & Activer Access+ :
{officialiser_url}

L’équipe Prof Chez Vous"""

    try:
        from django.core.mail import send_mail
        from django.conf import settings
        send_mail(
            subject=sujet,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[dest_email],
            fail_silently=False,
        )
        logger.info("Email d'essai réalisé envoyé avec succès à %s.", dest_email)
        return True
    except Exception as e:
        logger.error("Échec d'envoi de l'email d'essai réalisé à %s : %s", dest_email, e, exc_info=True)
        return False'''


text = re.sub(old_confirmed, new_confirmed, text, flags=re.DOTALL)
text = re.sub(old_realise, new_realise, text, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Email logic updated.")
