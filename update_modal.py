import sys
import re
sys.stdout.reconfigure(encoding='utf-8')

with open('templates/core/prof_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

old_fn = r"function showCompletionModal\(\) \{.*?overlay\.addEventListener\('click', function\(e\) \{\s*if \(e\.target === overlay\) overlay\.remove\(\);\s*\}\);\s*\}"

new_fn = r'''function showCompletionModal() {
            markTourCompleted();
            const overlay = document.createElement('div');
            overlay.className = 'tour-completion-overlay';
            overlay.innerHTML = `
                <div class="tour-completion-card" style="padding: 2.5rem 2rem; max-width: 420px;">
                    
                    <div style="text-align: center; margin-bottom: 1.5rem;">
                        <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🎉</div>
                        <h2 style="font-size: 1.4rem; font-weight: 800; color: #0f172a; margin: 0 0 0.75rem 0;">Vous êtes prêt(e) !</h2>
                        <p style="font-size: 0.95rem; color: #475569; line-height: 1.6; margin: 0;">Votre tableau de bord n'a plus de secret pour vous. Vous êtes paré pour recevoir et gérer vos premières demandes de cours.</p>
                    </div>

                    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 14px; padding: 1.5rem; margin-bottom: 1.5rem;">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                            <span style="font-size: 1.1rem;">🟢</span>
                            <span style="font-size: 1rem; font-weight: 700; color: #166534;">Une dernière étape importante</span>
                        </div>
                        <p style="font-size: 0.9rem; color: #334155; line-height: 1.5; margin: 0;">Intégrez la communauté des professeurs pour rester informé et développer votre activité de répétiteur à Cotonou.</p>
                    </div>

                    <a href="https://whatsapp.com/channel/0029VbD5Qni2Jl8KaiqS3k36" target="_blank" onclick="this.closest('.tour-completion-overlay').remove()" style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; background: #25D366; color: white; text-decoration: none; padding: 0.85rem 2rem; border-radius: 12px; font-size: 1.05rem; font-weight: 700; text-align: center; margin-bottom: 1rem; transition: all 0.2s; box-shadow: 0 4px 12px rgba(37, 211, 102, 0.25);">
                        <span>👉</span> Rejoindre la chaîne WhatsApp
                    </a>
                    <button onclick="this.closest('.tour-completion-overlay').remove()" style="display: block; width: 100%; background: transparent; color: #94a3b8; border: none; font-size: 0.9rem; font-weight: 500; cursor: pointer; padding: 0.5rem;">Non merci, accéder directement à mon tableau de bord</button>
                </div>
            `;
            document.body.appendChild(overlay);
            overlay.addEventListener('click', function(e) {
                if (e.target === overlay) overlay.remove();
            });
        }'''

result = re.sub(old_fn, new_fn, text, flags=re.DOTALL)

if result != text:
    with open('templates/core/prof_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(result)
    print("Modale mise à jour avec succès !")
else:
    print("Pattern non trouvé")
