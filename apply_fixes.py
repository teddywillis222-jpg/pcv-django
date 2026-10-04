import sys
import re

# ================================
# 1. MODELS.PY
# ================================
with open('core/models.py', 'r', encoding='utf-8') as f:
    models_content = f.read()

models_target = '    est_certifie = models.BooleanField(default=False)\n'
models_replacement = models_target + '''
    score_fiabilite = models.PositiveBigIntegerField(default=0, help_text="Total des points cumulés de fiabilité")
    date_dernier_calcul_score = models.DateTimeField(null=True, blank=True, help_text="Date de la dernière actualisation du score")
'''
if 'score_fiabilite =' not in models_content:
    models_content = models_content.replace(models_target, models_replacement)

new_model = '''

class OperationScoreFiabilite(models.Model):
    TYPE_OPERATION_CHOICES = [
        ('JOURNAL', 'Journal de séance'),
        ('REACTIVITE', 'Réactivité'),
        ('ENGAGEMENT_TERMINE', 'Engagement terminé'),
        ('AVIS', 'Avis familial'),
        ('CORRECTION', 'Correction manuelle'),
    ]

    STATUT_CHOICES = [
        ('VALIDE', 'Valide'),
        ('NEUTRALISE', 'Neutralisé'),
        ('ANNULE', 'Annulé'),
    ]

    professeur = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='operations_fiabilite')
    type_operation = models.CharField(max_length=50, choices=TYPE_OPERATION_CHOICES)
    points = models.IntegerField(help_text="Nombre de points attribués (peut être 0 ou négatif en cas de correction)")
    reference_type = models.CharField(max_length=100, help_text="Type d'objet à l'origine (ex: Seance, Engagement, Avis)")
    reference_id = models.CharField(max_length=255, help_text="ID de l'objet source")
    date_creation = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='VALIDE')
    operation_origine = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, help_text="Référence à l'opération corrigée, si applicable")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['professeur', 'type_operation', 'reference_type', 'reference_id'],
                name='unique_operation_fiabilite_per_source'
            )
        ]

    def __str__(self):
        return f"{self.professeur.user.get_full_name()} | {self.type_operation} | {self.points} pts"
'''
if 'class OperationScoreFiabilite' not in models_content:
    models_content += new_model

with open('core/models.py', 'w', encoding='utf-8') as f:
    f.write(models_content)


# ================================
# 2. VIEWS.PY
# ================================
with open('core/views.py', 'r', encoding='utf-8') as f:
    views_content = f.read()

# Reactivite
react_target = "engagement.date_confirmation = timezone.now()"
react_rep = react_target + '''
            try:
                from .services_fiabilite import attribuer_points_reactivite
                attribuer_points_reactivite(engagement, engagement.date_confirmation)
            except Exception:
                pass'''
if 'attribuer_points_reactivite' not in views_content:
    views_content = views_content.replace(react_target, react_rep)

# Journal
journal_target = "seance.save()"
journal_rep = journal_target + '''

    try:
        from .services_fiabilite import attribuer_points_journal
        attribuer_points_journal(seance)
    except Exception:
        pass'''
# Find the specific seance.save() in api_ajouter_seance (not all seance.save())
if 'attribuer_points_journal' not in views_content:
    js_target = """    seance.validee = True
    seance.save()"""
    views_content = views_content.replace(js_target, """    seance.validee = True
    seance.save()
    try:
        from .services_fiabilite import attribuer_points_journal
        attribuer_points_journal(seance)
    except Exception:
        pass""")

# Engagement Termine
term_target = "        engagement.statut_general = StatutGeneral.TERMINE\n        engagement.save()"
term_rep = term_target + '''

        try:
            from .services_fiabilite import attribuer_points_engagement_termine
            attribuer_points_engagement_termine(engagement)
        except Exception:
            pass'''
if 'attribuer_points_engagement_termine' not in views_content:
    views_content = views_content.replace(term_target, term_rep)

# Avis
avis_target = """        evaluation, created = Evaluation.objects.update_or_create(
            parent_evaluateur=request.user,
            professeur_evalue=engagement.professeur,
            defaults={
                'engagement_lie': engagement,
                'note': note,
                'commentaire': commentaire
            }
        )"""
avis_rep = avis_target + '''

        if created:
            try:
                from .services_fiabilite import attribuer_points_avis
                attribuer_points_avis(evaluation)
            except Exception:
                pass'''
if 'attribuer_points_avis' not in views_content:
    views_content = views_content.replace(avis_target, avis_rep)

# Recherche
rech_target = """        # Ordre par défaut : Expert de la classe (si recherchée) > Certifiés > Suivi rigoureux > Complétion > Moyenne > Récent
        sort_args = []
        if classe:
            sort_args.append('-is_expert_classe')
            
        sort_args.extend([
            '-profil_complet',
            '-est_certifie',
            '-suivi_rigoureux',
            '-moyenne_avis',
            '-id'
        ])
        professeurs = professeurs.order_by(*sort_args)"""
rech_rep = """        # Ordre par défaut : Actifs récemment > Score fiabilité > Moyenne avis > Profil complet
        # Si filtre classe : Expert de la classe en premier
        sort_args = []
        if classe:
            sort_args.append('-is_expert_classe')

        sort_args.extend([
            '-user__last_login',
            '-score_fiabilite',
            '-moyenne_avis',
            '-profil_complet',
        ])
        professeurs = professeurs.order_by(*sort_args)"""
if '-score_fiabilite' not in views_content:
    views_content = views_content.replace(rech_target, rech_rep)

# Context Prof Dashboard
ctx_target = "    context['ambassador_stats'] = ambassador_stats\n    context['site_config'] = SiteConfiguration.get_solo()"
ctx_rep = ctx_target + '''

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
if 'stats_fiabilite' not in views_content:
    views_content = views_content.replace(ctx_target, ctx_rep)

with open('core/views.py', 'w', encoding='utf-8') as f:
    f.write(views_content)


# ================================
# 3. PROF_DASHBOARD.HTML
# ================================
with open('templates/core/prof_dashboard.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

new_section = '''        <!-- SECTION FIABILITE (Détails du score) -->
        <div id="section-fiabilite" class="dash-section" style="display: none; max-width: 800px; margin: 0 auto;">
            <div style="background: white; border-radius: 16px; border: 1px solid var(--dash-border, #e2e8f0); overflow: hidden;">
                <!-- Header -->
                <div style="padding: 2rem;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem;">
                        <div>
                            <h2 style="font-size: 1.25rem; font-weight: 700; color: var(--dash-text, #0f172a); margin: 0 0 0.25rem 0;">Mon score de fiabilité</h2>
                            <p style="font-size: 0.95rem; color: var(--dash-text-muted, #64748b); margin: 0;">Votre engagement sur Prof Chez Vous</p>
                        </div>
                        <div style="color: #16a34a; padding: 0.5rem; border-radius: 50%;">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>
                        </div>
                    </div>
                    <div style="font-size: 2rem; font-weight: 800; color: #16a34a;">
                        {{ teacher.score_fiabilite|default:0 }} points
                    </div>
                </div>

                <div style="height: 1px; background: var(--dash-border, #f1f5f9); margin: 0 2rem;"></div>

                <!-- Body -->
                <div style="padding: 2rem;">
                    <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--dash-text, #0f172a); margin: 0 0 1.5rem 0;">Mes contributions</h3>
                    
                    <div style="display: flex; flex-direction: column; gap: 1rem;">
                        <!-- Ligne 1 -->
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; color: var(--dash-text, #334155); font-size: 1rem;">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #94a3b8;"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"></path></svg>
                                Journaux de séance
                            </div>
                            <div style="font-weight: 700; color: var(--dash-text, #0f172a);">
                                +{{ stats_fiabilite.JOURNAL|default:0 }} pts
                            </div>
                        </div>

                        <!-- Ligne 2 -->
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; color: var(--dash-text, #334155); font-size: 1rem;">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #94a3b8;"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
                                Réactivité
                            </div>
                            <div style="font-weight: 700; color: var(--dash-text, #0f172a);">
                                +{{ stats_fiabilite.REACTIVITE|default:0 }} pts
                            </div>
                        </div>

                        <!-- Ligne 3 -->
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; color: var(--dash-text, #334155); font-size: 1rem;">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #94a3b8;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>
                                Collaborations achevées
                            </div>
                            <div style="font-weight: 700; color: var(--dash-text, #0f172a);">
                                +{{ stats_fiabilite.ENGAGEMENT_TERMINE|default:0 }} pts
                            </div>
                        </div>

                        <!-- Ligne 4 -->
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; color: var(--dash-text, #334155); font-size: 1rem;">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #94a3b8;"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                                Reconnaissance des familles
                            </div>
                            <div style="font-weight: 700; color: var(--dash-text, #0f172a);">
                                +{{ stats_fiabilite.AVIS|default:0 }} pts
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer -->
                <div style="padding: 1.5rem 2rem; background: #f8fafc; color: var(--dash-text-muted, #64748b); font-size: 0.9rem; line-height: 1.5; border-top: 1px solid var(--dash-border, #f1f5f9);">
                    Continuez à renseigner vos bilans de séance et à répondre aux demandes des familles pour faire progresser votre score.
                </div>
            </div>
        </div>'''

html_pattern = r'<!-- SECTION FIABILITE \(Vide pour le moment\) -->.*?</div>\s*</div>'
if 'Détails du score' not in html_content:
    html_content = re.sub(html_pattern, new_section, html_content, flags=re.DOTALL)
    with open('templates/core/prof_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

print("All fixes applied successfully.")
