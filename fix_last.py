import sys
import re
sys.stdout.reconfigure(encoding='utf-8')

# --- 1. RECHERCHE FIX ---
with open('core/views.py', 'r', encoding='utf-8') as f:
    text = f.read()

rech_t = r"sort_args = \[\]\s*if classe:\s*sort_args\.append\('-is_expert_classe'\)\s*sort_args\.extend\(\[\s*'-profil_complet',\s*'-est_certifie',\s*'-suivi_rigoureux',\s*'-moyenne_avis',\s*'-id'\s*\]\)\s*professeurs = professeurs\.order_by\(\*sort_args\)"
rech_r = """sort_args = []
        if classe:
            sort_args.append('-is_expert_classe')

        sort_args.extend([
            '-user__last_login',
            '-score_fiabilite',
            '-moyenne_avis',
            '-profil_complet',
        ])
        professeurs = professeurs.order_by(*sort_args)"""

text = re.sub(rech_t, rech_r, text, flags=re.MULTILINE)
with open('core/views.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Fix recherche appliqué")

# --- 2. WHATSAPP CTA FIX ---
with open('templates/core/prof_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

cta_t = r"<svg width=\"64\" height=\"64\".*?>Vous \xeates pr\xeat !</h2>\s*<p.*?>Votre espace est configur\xe9\..*?</p>\s*<button.*?C'est parti !</button>"
cta_r = """<div style="background: #eef2ff; width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem auto;">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#4f46e5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                    </div>
                    <h2 style="font-size: 1.5rem; font-weight: 800; margin-bottom: 1rem; color: #0f172a;">Rejoignez la communaut\xe9</h2>
                    <p style="font-size: 1rem; color: #475569; margin-bottom: 2rem; line-height: 1.6;">Pour ne rater aucune opportunit\xe9 de cours et \xe9changer avec les autres professeurs, rejoignez notre canal WhatsApp exclusif.</p>
                    <a href="https://whatsapp.com/channel/0029Val4Hn1I7BeC0m1oXz34" target="_blank" onclick="document.getElementById('tour-completion-overlay').remove()" style="display: block; background: #25D366; color: white; text-decoration: none; padding: 0.8rem 2rem; border-radius: 12px; font-size: 1.05rem; font-weight: 700; text-align: center; margin-bottom: 1rem; transition: all 0.2s;">Rejoindre le canal WhatsApp</a>
                    <button onclick="document.getElementById('tour-completion-overlay').remove()" style="background: transparent; color: #64748b; border: none; font-size: 0.95rem; font-weight: 600; cursor: pointer; text-decoration: underline;">Plus tard, acc\xe9der \xe0 mon espace</button>"""
text = re.sub(cta_t, cta_r, text, flags=re.DOTALL)
with open('templates/core/prof_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("Fix WhatsApp appliqué")
