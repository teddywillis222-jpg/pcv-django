import re

with open('templates/core/components/engagement_card_teacher.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Messagerie
content = re.sub(
    r'{% if eng.conversation and eng.statut_general != \'EN_ATTENTE\' and eng.statut_general != \'REFUSE\' %}',
    r'{% if eng.conversation %}',
    content
)

# Replace Actions de gestion
content = re.sub(
    r'{% if eng.statut_general == \'FINALISE\' or eng.statut_general == \'EN_COURS\' %}',
    r'{% if eng.statut_general == \'FINALISE\' %}',
    content
)

with open('templates/core/components/engagement_card_teacher.html', 'w', encoding='utf-8') as f:
    f.write(content)
