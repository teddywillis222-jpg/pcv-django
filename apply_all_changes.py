import re
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

errors = []

# ================================
# 1. MODELS.PY
# ================================
with open('core/models.py', 'r', encoding='utf-8') as f:
    text = f.read()

m_target = '    est_certifie = models.BooleanField(default=False)\n'
m_rep = m_target + '    score_fiabilite = models.PositiveBigIntegerField(default=0, help_text="Total des points cumulés de fiabilité")\n    date_dernier_calcul_score = models.DateTimeField(null=True, blank=True, help_text="Date de la dernière actualisation du score")\n'
if 'score_fiabilite' not in text:
    if m_target in text:
        text = text.replace(m_target, m_rep)
        print("[OK] models.py: champs score_fiabilite ajoutés")
    else:
        errors.append("models.py: cible est_certifie introuvable")

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
    points = models.IntegerField(help_text="Nombre de points attribués")
    reference_type = models.CharField(max_length=100, help_text="Type d'objet source (ex: Seance, Engagement, Avis)")
    reference_id = models.CharField(max_length=255, help_text="ID de l'objet source")
    date_creation = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='VALIDE')
    operation_origine = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

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
if 'class OperationScoreFiabilite' not in text:
    text += new_model
    print("[OK] models.py: modèle OperationScoreFiabilite ajouté")

with open('core/models.py', 'w', encoding='utf-8') as f:
    f.write(text)

# ================================
# 2. VIEWS.PY
# ================================
with open('core/views.py', 'r', encoding='utf-8') as f:
    text = f.read()

changes_count = 0

# a) post_signup redirect
t = 'return redirect("prof_intro")'
r = 'return redirect("prof_create_profile")'
if t in text:
    text = text.replace(t, r)
    changes_count += 1
    print("[OK] views.py: redirect prof_intro -> prof_create_profile")

# b) réactivité
t = "engagement.date_confirmation = timezone.now()"
r = t + '''
            try:
                from .services_fiabilite import attribuer_points_reactivite
                attribuer_points_reactivite(engagement, engagement.date_confirmation)
            except Exception:
                pass'''
if 'attribuer_points_reactivite' not in text:
    if t in text:
        text = text.replace(t, r)
        changes_count += 1
        print("[OK] views.py: trigger réactivité ajouté")
    else:
        errors.append("views.py: cible date_confirmation introuvable")

# c) journal
t = "    seance.validee = True\n    seance.save()"
r = t + '''

    try:
        from .services_fiabilite import attribuer_points_journal
        attribuer_points_journal(seance)
    except Exception:
        pass'''
if 'attribuer_points_journal' not in text:
    if t in text:
        text = text.replace(t, r)
        changes_count += 1
        print("[OK] views.py: trigger journal ajouté")
    else:
        errors.append("views.py: cible seance.validee introuvable")

# d) engagement terminé
t = "        engagement.statut_general = StatutGeneral.TERMINE\n        engagement.save()"
r = t + '''

        try:
            from .services_fiabilite import attribuer_points_engagement_termine
            attribuer_points_engagement_termine(engagement)
        except Exception:
            pass'''
if 'attribuer_points_engagement_termine' not in text:
    if t in text:
        text = text.replace(t, r)
        changes_count += 1
        print("[OK] views.py: trigger engagement terminé ajouté")
    else:
        errors.append("views.py: cible TERMINE introuvable")

# e) avis
t = """        evaluation, created = Evaluation.objects.update_or_create(
            parent_evaluateur=request.user,
            professeur_evalue=engagement.professeur,
            defaults={
                'engagement_lie': engagement,
                'note': note,
                'commentaire': commentaire
            }
        )"""
r = t + '''

        if created:
            try:
                from .services_fiabilite import attribuer_points_avis
                attribuer_points_avis(evaluation)
            except Exception:
                pass'''
if 'attribuer_points_avis' not in text:
    if t in text:
        text = text.replace(t, r)
        changes_count += 1
        print("[OK] views.py: trigger avis ajouté")
    else:
        errors.append("views.py: cible update_or_create introuvable")

# f) algorithme de recherche
t = """        # Ordre par défaut : Expert de la classe (si recherchée) > Certifiés > Suivi rigoureux > Complétion > Moyenne > Récent
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
r = """        # Ordre par défaut : Actifs récemment > Score fiabilité > Moyenne avis > Profil complet
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
if '-score_fiabilite' not in text:
    if "'-suivi_rigoureux'" in text:
        text = text.replace(t, r)
        changes_count += 1
        print("[OK] views.py: algorithme de recherche mis à jour")
    else:
        errors.append("views.py: cible sort_args introuvable")

# g) contexte dashboard fiabilité
t = "    context['ambassador_stats'] = ambassador_stats\n    context['site_config'] = SiteConfiguration.get_solo()"
r = t + '''

    from django.db.models import Sum
    from .models import OperationScoreFiabilite
    ops = OperationScoreFiabilite.objects.filter(professeur=teacher, statut='VALIDE').values('type_operation').annotate(total=Sum('points'))
    stats_fiabilite = {
        'JOURNAL': 0,
        'REACTIVITE': 0,
        'ENGAGEMENT_TERMINE': 0,
        'AVIS': 0,
    }
    for op in ops:
        stats_fiabilite[op['type_operation']] = op['total'] or 0
    context['stats_fiabilite'] = stats_fiabilite'''
if 'stats_fiabilite' not in text:
    if t in text:
        text = text.replace(t, r)
        changes_count += 1
        print("[OK] views.py: contexte stats_fiabilite ajouté au dashboard")
    else:
        errors.append("views.py: cible ambassador_stats introuvable")

with open('core/views.py', 'w', encoding='utf-8') as f:
    f.write(text)
print(f"[OK] views.py: {changes_count} modifications appliquées")

# ================================
# 3. PROF_DASHBOARD.HTML
# ================================
with open('templates/core/prof_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

# a) WhatsApp CTA dans la visite guidée
old_cta = """                card.innerHTML = `
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color: #16a34a; margin-bottom: 1.5rem;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                    <h2 style="font-size: 1.5rem; font-weight: 800; margin-bottom: 1rem; color: #0f172a;">Vous \xeates pr\xeat !</h2>
                    <p style="font-size: 1rem; color: #475569; margin-bottom: 2rem; line-height: 1.6;">Votre espace est configur\xe9. Vous pouvez maintenant g\xe9rer vos cours, r\xe9pondre aux familles et suivre vos revenus en toute simplicit\xe9.</p>
                    <button onclick="document.getElementById('tour-completion-overlay').remove()" style="background: #16a34a; color: white; border: none; padding: 0.8rem 2rem; border-radius: 12px; font-size: 1.05rem; font-weight: 700; cursor: pointer; width: 100%; transition: all 0.2s;">C'est parti !</button>
                `;"""
new_cta = """                card.innerHTML = `
                    <div style="background: #eef2ff; width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem auto;">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#4f46e5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                    </div>
                    <h2 style="font-size: 1.5rem; font-weight: 800; margin-bottom: 1rem; color: #0f172a;">Rejoignez la communaut\xe9</h2>
                    <p style="font-size: 1rem; color: #475569; margin-bottom: 2rem; line-height: 1.6;">Pour ne rater aucune opportunit\xe9 de cours et \xe9changer avec les autres professeurs, rejoignez notre canal WhatsApp exclusif.</p>
                    <a href="https://whatsapp.com/channel/0029Val4Hn1I7BeC0m1oXz34" target="_blank" onclick="document.getElementById('tour-completion-overlay').remove()" style="display: block; background: #25D366; color: white; text-decoration: none; padding: 0.8rem 2rem; border-radius: 12px; font-size: 1.05rem; font-weight: 700; text-align: center; margin-bottom: 1rem; transition: all 0.2s;">Rejoindre le canal WhatsApp</a>
                    <button onclick="document.getElementById('tour-completion-overlay').remove()" style="background: transparent; color: #64748b; border: none; font-size: 0.95rem; font-weight: 600; cursor: pointer; text-decoration: underline;">Plus tard, acc\xe9der \xe0 mon espace</button>
                `;"""

if "C'est parti !" in text:
    text = text.replace(old_cta, new_cta)
    print("[OK] prof_dashboard.html: CTA WhatsApp dans la visite guidée")

# b) Section Fiabilité
new_section = '''        <!-- SECTION FIABILITE -->
        <div id="section-fiabilite" class="dash-section" style="display: none; max-width: 800px; margin: 0 auto;">
            <div style="background: white; border-radius: 16px; border: 1px solid var(--dash-border, #e2e8f0); overflow: hidden;">
                <div style="padding: 2rem;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem;">
                        <div>
                            <h2 style="font-size: 1.25rem; font-weight: 700; color: var(--dash-text, #0f172a); margin: 0 0 0.25rem 0;">Mon score de fiabilit\xe9</h2>
                            <p style="font-size: 0.95rem; color: var(--dash-text-muted, #64748b); margin: 0;">Votre engagement sur Prof Chez Vous</p>
                        </div>
                        <div style="color: #16a34a; background: #f0fdf4; padding: 0.5rem; border-radius: 50%;">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>
                        </div>
                    </div>
                    <div style="font-size: 2rem; font-weight: 800; color: #16a34a;">
                        {{ teacher.score_fiabilite|default:0 }} points
                    </div>
                </div>
                <div style="height: 1px; background: var(--dash-border, #f1f5f9); margin: 0 2rem;"></div>
                <div style="padding: 2rem;">
                    <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--dash-text, #0f172a); margin: 0 0 1.5rem 0;">Mes contributions</h3>
                    <div style="display: flex; flex-direction: column; gap: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; color: var(--dash-text, #334155); font-size: 1rem;">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #94a3b8;"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"></path></svg>
                                Journaux de s\xe9ance
                            </div>
                            <div style="font-weight: 700; color: var(--dash-text, #0f172a);">+{{ stats_fiabilite.JOURNAL|default:0 }} pts</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; color: var(--dash-text, #334155); font-size: 1rem;">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #94a3b8;"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
                                R\xe9activit\xe9
                            </div>
                            <div style="font-weight: 700; color: var(--dash-text, #0f172a);">+{{ stats_fiabilite.REACTIVITE|default:0 }} pts</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; color: var(--dash-text, #334155); font-size: 1rem;">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #94a3b8;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>
                                Collaborations achev\xe9es
                            </div>
                            <div style="font-weight: 700; color: var(--dash-text, #0f172a);">+{{ stats_fiabilite.ENGAGEMENT_TERMINE|default:0 }} pts</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; color: var(--dash-text, #334155); font-size: 1rem;">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #94a3b8;"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                                Reconnaissance des familles
                            </div>
                            <div style="font-weight: 700; color: var(--dash-text, #0f172a);">+{{ stats_fiabilite.AVIS|default:0 }} pts</div>
                        </div>
                    </div>
                </div>
                <div style="padding: 1.5rem 2rem; background: #f8fafc; color: var(--dash-text-muted, #64748b); font-size: 0.9rem; line-height: 1.5; border-top: 1px solid var(--dash-border, #f1f5f9);">
                    Continuez \xe0 renseigner vos bilans de s\xe9ance et \xe0 r\xe9pondre aux demandes des familles pour faire progresser votre score.
                </div>
            </div>
        </div>'''

fiab_pattern = r'<!-- SECTION FIABILITE \(Vide pour le moment\) -->.*?</div>\s*</div>'
if 'Bientôt disponible' in text:
    text = re.sub(fiab_pattern, new_section, text, flags=re.DOTALL)
    print("[OK] prof_dashboard.html: Section fiabilité remplacée")

with open('templates/core/prof_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(text)

# ================================
# 4. PROF_ATTENTE_DASHBOARD.HTML
# ================================
with open('templates/core/prof_attente_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

banner_pattern = r'<!-- Bannière WhatsApp temporaire -->.*?</div>\s*</div>\s*</div>'
if 'Bannière WhatsApp' in text:
    text = re.sub(banner_pattern, '', text, flags=re.DOTALL)
    print("[OK] prof_attente_dashboard.html: Bannière WhatsApp supprimée")
    with open('templates/core/prof_attente_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(text)

# ================================
# RÉSUMÉ
# ================================
if errors:
    print("\n[ERREURS]:")
    for e in errors:
        print(f"  - {e}")
else:
    print("\n[SUCCÈS] Toutes les modifications ont été appliquées sans corruption d'encodage.")
