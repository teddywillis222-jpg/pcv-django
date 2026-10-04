import sys
sys.stdout.reconfigure(encoding='utf-8')

files = [
    'core/models.py', 'core/views.py', 'core/services_fiabilite.py',
    'templates/core/prof_dashboard.html', 'templates/core/prof_attente_dashboard.html'
]
for f in files:
    try:
        t = open(f, 'r', encoding='utf-8').read()
        has_accents = any(c in t for c in 'éèêàôùç')
        print(f'[OK] {f} ({len(t)} chars, accents={has_accents})')
    except Exception as e:
        print(f'[ERREUR] {f}: {e}')

print()
t = open('core/views.py', 'r', encoding='utf-8').read()
triggers = [
    'attribuer_points_reactivite',
    'attribuer_points_journal',
    'attribuer_points_engagement_termine',
    'attribuer_points_avis'
]
for tr in triggers:
    status = "OK" if tr in t else "MANQUANT"
    print(f'  Trigger {tr}: {status}')

status_rech = "OK" if "-score_fiabilite" in t else "MANQUANT"
print(f'  score_fiabilite dans recherche: {status_rech}')

status_ctx = "OK" if "stats_fiabilite" in t else "MANQUANT"
print(f'  stats_fiabilite dans contexte: {status_ctx}')

# Check HTML section
h = open('templates/core/prof_dashboard.html', 'r', encoding='utf-8').read()
status_html = "OK" if "teacher.score_fiabilite" in h else "MANQUANT"
print(f'  Section fiabilite dans HTML: {status_html}')

status_whatsapp = "OK" if "Rejoindre le canal WhatsApp" in h else "MANQUANT"
print(f'  CTA WhatsApp dans tour: {status_whatsapp}')
