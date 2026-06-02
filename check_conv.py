import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Conversation
for c in Conversation.objects.all()[:5]:
    print(f'Conv {c.id}: dernier_msg="{c.dernier_message_texte}", date={c.dernier_message_date}, auteur={c.dernier_message_auteur}')
    last_msg = c.messages.order_by('-date_envoi').first()
    if last_msg:
        print(f'  -> Real last msg: "{last_msg.contenu_texte[:80]}", date={last_msg.date_envoi}, auteur={last_msg.auteur}')
    else:
        print(f'  -> No messages in conversation')
