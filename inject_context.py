import sys

with open('core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = "    context['ambassador_stats'] = ambassador_stats\n    context['site_config'] = SiteConfiguration.get_solo()"

replacement = target + '''

    from django.db.models import Sum
    from core.models import OperationScoreFiabilite
    ops = OperationScoreFiabilite.objects.filter(professeur=teacher, statut='VALIDE').values('type_operation').annotate(total=Sum('points'))
    stats_fiabilite = {
        'JOURNAL': 0,
        'REACTIVITE': 0,
        'ENGAGEMENT_TERMINE': 0,
        'AVIS': 0,
    }
    for op in ops:
        stats_fiabilite[op['type_operation']] = op['total'] or 0
    context['stats_fiabilite'] = stats_fiabilite
'''

content = content.replace(target, replacement)

with open('core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Context injected")
