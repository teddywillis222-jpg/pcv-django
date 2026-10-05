import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('templates/core/prof_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

fiab_pattern = r'<!-- SECTION FIABILITE -->\s*<div id="section-fiabilite".*?Continuez à renseigner vos bilans de séance.*?</div>\s*</div>\s*</div>'

new_section = '''<!-- SECTION FIABILITE -->
        <div id="section-fiabilite" class="dash-section" style="display: none; max-width: 800px; margin: 0 auto;">
            <div style="background: white; border-radius: 16px; border: 1px solid var(--dash-border, #e2e8f0); overflow: hidden;">
                <div style="padding: 2rem;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem;">
                        <div>
                            <h2 style="font-size: 1.25rem; font-weight: 700; color: var(--dash-text, #0f172a); margin: 0 0 0.25rem 0;">Mon score de fiabilité</h2>
                            <p style="font-size: 0.95rem; color: var(--dash-text-muted, #64748b); margin: 0;">Votre engagement sur Prof Chez Vous</p>
                        </div>
                        <div style="color: #16a34a; background: #f0fdf4; padding: 0.5rem; border-radius: 50%;">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z"></path><path d="m9 12 2 2 4-4"></path></svg>
                        </div>
                    </div>
                    <div style="font-size: 2rem; font-weight: 800; color: #16a34a; margin-bottom: 1.5rem;">
                        {{ teacher.score_fiabilite|default:0 }} points
                    </div>
                    
                    <button onclick="const details = document.getElementById('fiabilite-details'); const icon = document.getElementById('fiabilite-toggle-icon'); if(details.style.display === 'none'){ details.style.display = 'block'; icon.style.transform = 'rotate(180deg)'; this.querySelector('span').innerText = 'Masquer les détails'; } else { details.style.display = 'none'; icon.style.transform = 'rotate(0deg)'; this.querySelector('span').innerText = 'Plus de détails'; }" style="display: flex; align-items: center; gap: 0.5rem; background: #f1f5f9; border: none; color: #475569; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; font-size: 0.95rem; cursor: pointer; transition: background 0.2s;">
                        <span>Plus de détails</span>
                        <svg id="fiabilite-toggle-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="transition: transform 0.3s;"><polyline points="6 9 12 15 18 9"></polyline></svg>
                    </button>
                </div>
                
                <div id="fiabilite-details" style="display: none;">
                    <div style="height: 1px; background: var(--dash-border, #f1f5f9); margin: 0 2rem;"></div>
                    <div style="padding: 2rem;">
                        <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--dash-text, #0f172a); margin: 0 0 1.5rem 0;">Mes contributions</h3>
                        <div style="display: flex; flex-direction: column; gap: 1rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="display: flex; align-items: center; gap: 0.75rem; color: var(--dash-text, #334155); font-size: 1rem;">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #94a3b8;"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"></path></svg>
                                    Journaux de séance
                                </div>
                                <div style="font-weight: 700; color: var(--dash-text, #0f172a);">+{{ stats_fiabilite.JOURNAL|default:0 }} pts</div>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="display: flex; align-items: center; gap: 0.75rem; color: var(--dash-text, #334155); font-size: 1rem;">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #94a3b8;"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
                                    Réactivité
                                </div>
                                <div style="font-weight: 700; color: var(--dash-text, #0f172a);">+{{ stats_fiabilite.REACTIVITE|default:0 }} pts</div>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="display: flex; align-items: center; gap: 0.75rem; color: var(--dash-text, #334155); font-size: 1rem;">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #94a3b8;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>
                                    Collaborations achevées
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
                </div>
                
                <div style="padding: 1.5rem 2rem; background: #f8fafc; color: var(--dash-text-muted, #64748b); font-size: 0.9rem; line-height: 1.5; border-top: 1px solid var(--dash-border, #f1f5f9);">
                    Continuez à renseigner vos bilans de séance et à répondre aux demandes des familles pour faire progresser votre score.
                </div>
            </div>
        </div>'''

if 'Plus de détails' not in text:
    text = re.sub(fiab_pattern, new_section, text, flags=re.DOTALL)
    with open('templates/core/prof_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Mise à jour appliquée !")
else:
    print("Déjà appliqué")
