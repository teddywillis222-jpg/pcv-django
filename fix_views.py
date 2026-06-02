import re

with open('core/views.py', 'r', encoding='utf-8') as f: 
    content = f.read()

content = re.sub(r'(engagements = request\.user\.engagements_client\.all\(\)\.order_by\("-date_creation"\)\n)(?:\s*for eng in engagements:\n\s*eng\.check_and_update_essai_status\(\)\n)*', r'\g<1>    for eng in engagements:\n        eng.check_and_update_essai_status()\n', content)

content = re.sub(r'(engagements = engagements_base\.filter\(\n\s*Q\(enfants_concernes=active_enfant\) \| Q\(enfants_concernes__isnull=True\)\n\s*\)\.distinct\(\)\.order_by\("-date_creation"\)\n)(?:\s*for eng in engagements:\n\s*eng\.check_and_update_essai_status\(\)\n)*', r'\g<1>    for eng in engagements:\n        eng.check_and_update_essai_status()\n', content)

content = re.sub(r'(engagements = teacher\.engagements\.filter\(masque_par_professeur=False\)\.order_by\("-date_creation"\)\n)(?:\s*for eng in engagements:\n\s*eng\.check_and_update_essai_status\(\)\n)*', r'\g<1>    for eng in engagements:\n        eng.check_and_update_essai_status()\n', content)

with open('core/views.py', 'w', encoding='utf-8') as f: 
    f.write(content)
