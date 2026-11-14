import re

path = 'templates/core/components/engagement_modal.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern for modal inner
old_modal_pattern = r'(<!-- Modal Succès Engagement -->\s*<div id="engagementSuccessModal".*?)(<style>)'

new_modal_html = '''<!-- Modal Succès Engagement -->
<div id="engagementSuccessModal" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.55); z-index: 5000; align-items: center; justify-content: center; padding: 0.75rem; touch-action: manipulation; backdrop-filter: blur(2px);">
    <div style="background: white; border-radius: 1.25rem; width: 100%; max-width: 440px; text-align: center; padding: 1.15rem 1.25rem; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); max-height: 94vh; overflow-y: auto; -webkit-overflow-scrolling: touch;">
        <div style="width: 38px; height: 38px; border-radius: 50%; background: #dcfce7; color: #16a34a; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.45rem; animation: scaleIn 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
        </div>
        
        <!-- STANDARD SUCCESS -->
        <div id="eng_success_standard" style="display: none;">
            <h3 style="font-size: 1.35rem; font-weight: 800; color: #1e293b; margin-bottom: 0.4rem;">Proposition envoyée !</h3>
            <p style="color: #64748b; font-size: 0.88rem; margin-bottom: 1.25rem; line-height: 1.45;">Votre proposition d'engagement a été soumise avec succès. Le professeur a été notifié et vous répondra très bientôt.</p>
            <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                <a id="btn_go_dashboard_standard" href="#" style="padding: 0.85rem 1rem; background: #16a34a; color: white; border-radius: 0.75rem; font-weight: 700; text-decoration: none; transition: transform 0.2s;">Accéder à mon espace</a>
                <button onclick="closeEngagementSuccessModal()" style="padding: 0.75rem 1rem; background: #f1f5f9; color: #475569; border: none; border-radius: 0.75rem; font-weight: 700; cursor: pointer;">Rester sur cette page</button>
            </div>
        </div>

        <!-- ESSAI SUCCESS (PARENT) -->
        <div id="eng_success_essai_parent" style="display: none; text-align: center;">
            <h3 style="font-size: 1.25rem; font-weight: 800; color: #1e293b; margin: 0 0 0.25rem 0; line-height: 1.2;">Essai programmé avec succès !</h3>
            <p style="color: #64748b; font-size: 0.84rem; margin: 0 0 0.65rem 0; line-height: 1.4;">
                Votre demande a été transmise à <strong id="eng_success_prof_name_parent" style="color: #1e293b;">ce professeur</strong>.<br>Vous recevrez une notification dès sa confirmation.
            </p>
            
            <hr style="border: 0; border-top: 1px dashed #cbd5e1; margin: 0.6rem 0;">
            
            <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 0.85rem; padding: 0.85rem 1rem; margin-bottom: 0.75rem; text-align: left;">
                <h4 style="font-size: 0.95rem; font-weight: 800; color: #b45309; margin: 0 0 0.3rem 0; line-height: 1.35;">
                    💡 Et si vous pouviez mesurer concrètement chaque progrès de <span id="eng_success_enfant_name">votre enfant</span> ?
                </h4>
                <p style="font-size: 0.78rem; color: #92400e; margin: 0 0 0.45rem 0; line-height: 1.4; font-weight: 500;">
                    Grâce à Access+, recevez le compte-rendu du professeur après chaque cours, suivez sa maîtrise des notions abordées et assurez-lui un encadrement solide.
                </p>
                <ul style="font-size: 0.78rem; color: #92400e; margin: 0 0 0.45rem 0; padding-left: 1.1rem; line-height: 1.45;">
                    <li style="margin-bottom: 0.25rem;"><strong>📊 Espace de suivi en temps réel :</strong> bilans de chaque cours, notions assimilées et points à retravailler.</li>
                    <li style="margin-bottom: 0.25rem;"><strong>🛡️ Garantie de remplacement :</strong> changez de professeur sans frais si besoin.</li>
                    <li><strong>⚡ Assistance prioritaire 7j/7 :</strong> une équipe à vos côtés à chaque étape.</li>
                </ul>
                <div style="font-size: 0.82rem; font-weight: 800; color: #b45309; margin-top: 0.35rem; padding-top: 0.35rem; border-top: 1px dashed #fde68a; display: flex; justify-content: space-between; align-items: center;">
                    <span>Formule Access+</span>
                    <span>2 000 FCFA / mois <span style="font-size: 0.72rem; font-weight: 500; opacity: 0.85;">• Sans engagement</span></span>
                </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.35rem;">
                <a href="/mon-plan/" style="display: block; padding: 0.75rem 1rem; background: #f59e0b; color: white; border-radius: 0.65rem; font-weight: 700; font-size: 0.9rem; text-decoration: none; transition: transform 0.2s, background 0.2s; box-shadow: 0 3px 10px rgba(245,158,11,0.25); text-align: center;" onmouseover="this.style.background='#d97706'" onmouseout="this.style.background='#f59e0b'">
                    👉 Voir comment suivre les progrès de <span id="eng_success_cta_child_parent">votre enfant</span>
                </a>
                <a id="btn_go_dashboard_parent_secondary" href="#" style="padding: 0.45rem; background: transparent; color: #64748b; border: none; font-size: 0.78rem; font-weight: 600; text-decoration: underline; cursor: pointer; text-align: center; line-height: 1.3;">
                    Non merci, je continue sans suivi pour <span id="eng_success_enfant_name_btn">mon enfant</span> ❯
                </a>
            </div>
        </div>

        <!-- ESSAI SUCCESS (APPRENANT) -->
        <div id="eng_success_essai_apprenant" style="display: none; text-align: center;">
            <h3 style="font-size: 1.25rem; font-weight: 800; color: #1e293b; margin: 0 0 0.25rem 0; line-height: 1.2;">Essai programmé avec succès !</h3>
            <p style="color: #64748b; font-size: 0.84rem; margin: 0 0 0.65rem 0; line-height: 1.4;">
                Votre demande a été transmise à <strong id="eng_success_prof_name_apprenant" style="color: #1e293b;">ce professeur</strong>.<br>Vous recevrez une notification dès sa confirmation.
            </p>
            
            <hr style="border: 0; border-top: 1px dashed #cbd5e1; margin: 0.6rem 0;">
            
            <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 0.85rem; padding: 0.85rem 1rem; margin-bottom: 0.75rem; text-align: left;">
                <h4 style="font-size: 0.95rem; font-weight: 800; color: #b45309; margin: 0 0 0.3rem 0; line-height: 1.35;">
                    💡 Et si tu pouvais mesurer concrètement tes progrès ?
                </h4>
                <p style="font-size: 0.78rem; color: #92400e; margin: 0 0 0.45rem 0; line-height: 1.4; font-weight: 500;">
                    Grâce à Access+, reçois le compte-rendu du professeur après chaque cours, suis ta maîtrise des notions abordées et profite d'un encadrement solide.
                </p>
                <ul style="font-size: 0.78rem; color: #92400e; margin: 0 0 0.45rem 0; padding-left: 1.1rem; line-height: 1.45;">
                    <li style="margin-bottom: 0.25rem;"><strong>📊 Espace de suivi en temps réel :</strong> bilans de chaque cours, notions assimilées et points à retravailler.</li>
                    <li style="margin-bottom: 0.25rem;"><strong>🛡️ Garantie de remplacement :</strong> change de professeur sans frais si besoin.</li>
                    <li><strong>⚡ Assistance prioritaire 7j/7 :</strong> une équipe à tes côtés à chaque étape.</li>
                </ul>
                <div style="font-size: 0.82rem; font-weight: 800; color: #b45309; margin-top: 0.35rem; padding-top: 0.35rem; border-top: 1px dashed #fde68a; display: flex; justify-content: space-between; align-items: center;">
                    <span>Formule Access+</span>
                    <span>2 000 FCFA / mois <span style="font-size: 0.72rem; font-weight: 500; opacity: 0.85;">• Sans engagement</span></span>
                </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.35rem;">
                <a href="/mon-plan/" style="display: block; padding: 0.75rem 1rem; background: #f59e0b; color: white; border-radius: 0.65rem; font-weight: 700; font-size: 0.9rem; text-decoration: none; transition: transform 0.2s, background 0.2s; box-shadow: 0 3px 10px rgba(245,158,11,0.25); text-align: center;" onmouseover="this.style.background='#d97706'" onmouseout="this.style.background='#f59e0b'">
                    👉 Voir comment suivre mes progrès
                </a>
                <a id="btn_go_dashboard_apprenant_secondary" href="#" style="padding: 0.45rem; background: transparent; color: #64748b; border: none; font-size: 0.78rem; font-weight: 600; text-decoration: underline; cursor: pointer; text-align: center; line-height: 1.3;">
                    Non merci, je continue sans mon espace de suivi ❯
                </a>
            </div>
        </div>

    </div>
</div>

'''

content = re.sub(old_modal_pattern, new_modal_html + r'\2', content, flags=re.DOTALL)

# Update JS logic for firstProf and cta_child
old_js = """                    document.getElementById('eng_success_prof_name_parent').textContent = "Prof. " + profName;
                    document.getElementById('eng_success_enfant_name').textContent = childName;
                    document.getElementById('eng_success_enfant_name_btn').textContent = childName;
                    document.getElementById('btn_go_dashboard_parent_secondary').href = '/parent/dashboard/';
                    document.getElementById('eng_success_essai_parent').style.display = 'block';
                } else {
                    document.getElementById('eng_success_prof_name_apprenant').textContent = "Prof. " + profName;
                    document.getElementById('btn_go_dashboard_apprenant_secondary').href = '/apprenant/dashboard/';
                    document.getElementById('eng_success_essai_apprenant').style.display = 'block';
                }"""

new_js = """                    const firstProf = profName.trim().split(/\\s+/)[0] || profName;
                    document.getElementById('eng_success_prof_name_parent').textContent = "Prof. " + firstProf;
                    document.getElementById('eng_success_enfant_name').textContent = childName;
                    document.getElementById('eng_success_enfant_name_btn').textContent = childName;
                    const ctaChild = document.getElementById('eng_success_cta_child_parent');
                    if (ctaChild) ctaChild.textContent = childName;
                    document.getElementById('btn_go_dashboard_parent_secondary').href = '/parent/dashboard/';
                    document.getElementById('eng_success_essai_parent').style.display = 'block';
                } else {
                    const firstProf = profName.trim().split(/\\s+/)[0] || profName;
                    document.getElementById('eng_success_prof_name_apprenant').textContent = "Prof. " + firstProf;
                    document.getElementById('btn_go_dashboard_apprenant_secondary').href = '/apprenant/dashboard/';
                    document.getElementById('eng_success_essai_apprenant').style.display = 'block';
                }"""

assert old_js in content, "old_js not found in content"
content = content.replace(old_js, new_js)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Update successfully applied!")
