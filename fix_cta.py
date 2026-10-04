import sys
import re
sys.stdout.reconfigure(encoding='utf-8')

with open('templates/core/prof_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

cta_t = r"<div class=\"tour-completion-card\">\s*<div class=\"tour-emoji\">🎉</div>\s*<h3>Bienvenue sur Prof Chez Vous !</h3>.*?C'est parti !</button>\s*</div>"
cta_r = """<div class="tour-completion-card" style="padding: 2.5rem 2rem;">
                    <div style="background: #eef2ff; width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem auto;">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#4f46e5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                    </div>
                    <h2 style="font-size: 1.5rem; font-weight: 800; margin-bottom: 1rem; color: #0f172a;">Rejoignez la communaut\xe9</h2>
                    <p style="font-size: 1rem; color: #475569; margin-bottom: 2rem; line-height: 1.6;">Pour ne rater aucune opportunit\xe9 de cours et \xe9changer avec les autres professeurs, rejoignez notre canal WhatsApp exclusif.</p>
                    <a href="https://whatsapp.com/channel/0029Val4Hn1I7BeC0m1oXz34" target="_blank" onclick="this.closest('.tour-completion-overlay').remove()" style="display: block; background: #25D366; color: white; text-decoration: none; padding: 0.8rem 2rem; border-radius: 12px; font-size: 1.05rem; font-weight: 700; text-align: center; margin-bottom: 1rem; transition: all 0.2s;">Rejoindre le canal WhatsApp</a>
                    <button onclick="this.closest('.tour-completion-overlay').remove()" style="background: transparent; color: #64748b; border: none; font-size: 0.95rem; font-weight: 600; cursor: pointer; text-decoration: underline;">Plus tard, acc\xe9der \xe0 mon espace</button>
                </div>"""

text = re.sub(cta_t, cta_r, text, flags=re.DOTALL)

with open('templates/core/prof_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("WhatsApp CTA finally fixed!")
