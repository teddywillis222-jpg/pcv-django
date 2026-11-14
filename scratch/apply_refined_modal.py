import re

path = 'templates/core/components/engagement_modal.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern for modal
old_modal_pattern = r'(<!-- Modal Succès Engagement -->\s*<div id="engagementSuccessModal".*?)(<style>)'

new_modal_html = '''<!-- Modal Succès Engagement -->
<div id="engagementSuccessModal" class="eng-success-overlay" style="display: none;">
    <div class="eng-success-card">
        <div style="width: 50px; height: 50px; border-radius: 50%; background: #dcfce7; color: #16a34a; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.85rem; animation: scaleIn 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275); flex-shrink: 0;">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
        </div>
        
        <!-- STANDARD SUCCESS -->
        <div id="eng_success_standard" style="display: none;">
            <h3 style="font-size: 1.4rem; font-weight: 800; color: #0f172a; margin: 0 0 0.5rem 0;">Proposition envoyée !</h3>
            <p style="color: #64748b; font-size: 0.95rem; margin: 0 0 1.5rem 0; line-height: 1.55;">Votre proposition d'engagement a été soumise avec succès. Le professeur a été notifié et vous répondra très bientôt.</p>
            <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                <a id="btn_go_dashboard_standard" href="#" style="padding: 1rem 1.25rem; background: #16a34a; color: white; border-radius: 0.85rem; font-weight: 700; text-decoration: none; transition: transform 0.2s;">Accéder à mon espace</a>
                <button onclick="closeEngagementSuccessModal()" style="padding: 0.85rem 1.25rem; background: #f1f5f9; color: #475569; border: none; border-radius: 0.85rem; font-weight: 700; cursor: pointer;">Rester sur cette page</button>
            </div>
        </div>

        <!-- ESSAI SUCCESS (PARENT) -->
        <div id="eng_success_essai_parent" style="display: none; text-align: center;">
            <h3 style="font-size: 1.35rem; font-weight: 800; color: #0f172a; margin: 0 0 0.4rem 0; line-height: 1.3;">Essai programmé avec succès !</h3>
            <p style="color: #64748b; font-size: 0.92rem; margin: 0 0 1rem 0; line-height: 1.5;">
                Votre demande a été transmise à <strong id="eng_success_prof_name_parent" style="color: #0f172a;">ce professeur</strong>.<br>Vous recevrez une notification dès sa confirmation.
            </p>
            
            <hr style="border: 0; border-top: 1px dashed #cbd5e1; margin: 1rem 0 1.2rem 0;">
            
            <div style="background: #fffbeb; border: 1.5px solid #fde68a; border-radius: 1rem; padding: 1.2rem 1.25rem; margin-bottom: 1.25rem; text-align: left;">
                <h4 style="font-size: 1.05rem; font-weight: 800; color: #92400e; margin: 0 0 0.55rem 0; line-height: 1.4;">
                    💡 Et si vous pouviez mesurer concrètement chaque progrès de <span id="eng_success_enfant_name">votre enfant</span> ?
                </h4>
                <p style="font-size: 0.88rem; color: #78350f; margin: 0 0 0.85rem 0; line-height: 1.55; font-weight: 500;">
                    Grâce à Access+, recevez le compte-rendu du professeur après chaque cours, suivez sa maîtrise des notions abordées et assurez-lui un encadrement solide.
                </p>
                <ul style="font-size: 0.86rem; color: #78350f; margin: 0 0 0.85rem 0; padding-left: 1.25rem; line-height: 1.55;">
                    <li style="margin-bottom: 0.45rem;"><strong>📊 Espace de suivi en temps réel :</strong> bilans de chaque cours, notions assimilées et points à retravailler.</li>
                    <li style="margin-bottom: 0.45rem;"><strong>🛡️ Garantie de remplacement :</strong> changez de professeur sans frais si besoin.</li>
                    <li><strong>⚡ Assistance prioritaire 7j/7 :</strong> une équipe à vos côtés à chaque étape.</li>
                </ul>
                <div style="font-size: 0.92rem; font-weight: 800; color: #92400e; margin-top: 0.6rem; padding-top: 0.6rem; border-top: 1px dashed #fde68a; display: flex; justify-content: space-between; align-items: baseline;">
                    <span>Formule Access+</span>
                    <span>2 000 FCFA / mois <span style="font-size: 0.78rem; font-weight: 500; opacity: 0.85;">• Sans engagement</span></span>
                </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                <a href="/mon-plan/" style="display: block; width: 100%; box-sizing: border-box; padding: 0.95rem 1.25rem; background: #f59e0b; color: white; border-radius: 0.85rem; font-weight: 800; font-size: 0.98rem; text-decoration: none; transition: transform 0.2s, background 0.2s, box-shadow 0.2s; box-shadow: 0 4px 14px rgba(245,158,11,0.3); text-align: center;" onmouseover="this.style.background='#d97706'" onmouseout="this.style.background='#f59e0b'">
                    👉 Voir comment suivre les progrès de <span id="eng_success_cta_child_parent">votre enfant</span>
                </a>
                <a id="btn_go_dashboard_parent_secondary" href="#" style="display: block; padding: 0.65rem 0.75rem; background: transparent; color: #64748b; border: none; font-size: 0.86rem; font-weight: 600; text-decoration: underline; cursor: pointer; text-align: center; line-height: 1.4;">
                    Non merci, je continue sans suivi pour <span id="eng_success_enfant_name_btn">mon enfant</span> ❯
                </a>
            </div>
        </div>

        <!-- ESSAI SUCCESS (APPRENANT) -->
        <div id="eng_success_essai_apprenant" style="display: none; text-align: center;">
            <h3 style="font-size: 1.35rem; font-weight: 800; color: #0f172a; margin: 0 0 0.4rem 0; line-height: 1.3;">Essai programmé avec succès !</h3>
            <p style="color: #64748b; font-size: 0.92rem; margin: 0 0 1rem 0; line-height: 1.5;">
                Votre demande a été transmise à <strong id="eng_success_prof_name_apprenant" style="color: #0f172a;">ce professeur</strong>.<br>Vous recevrez une notification dès sa confirmation.
            </p>
            
            <hr style="border: 0; border-top: 1px dashed #cbd5e1; margin: 1rem 0 1.2rem 0;">
            
            <div style="background: #fffbeb; border: 1.5px solid #fde68a; border-radius: 1rem; padding: 1.2rem 1.25rem; margin-bottom: 1.25rem; text-align: left;">
                <h4 style="font-size: 1.05rem; font-weight: 800; color: #92400e; margin: 0 0 0.55rem 0; line-height: 1.4;">
                    💡 Et si tu pouvais mesurer concrètement tes progrès ?
                </h4>
                <p style="font-size: 0.88rem; color: #78350f; margin: 0 0 0.85rem 0; line-height: 1.55; font-weight: 500;">
                    Grâce à Access+, reçois le compte-rendu du professeur après chaque cours, suis ta maîtrise des notions abordées et profite d'un encadrement solide.
                </p>
                <ul style="font-size: 0.86rem; color: #78350f; margin: 0 0 0.85rem 0; padding-left: 1.25rem; line-height: 1.55;">
                    <li style="margin-bottom: 0.45rem;"><strong>📊 Espace de suivi en temps réel :</strong> bilans de chaque cours, notions assimilées et points à retravailler.</li>
                    <li style="margin-bottom: 0.45rem;"><strong>🛡️ Garantie de remplacement :</strong> change de professeur sans frais si besoin.</li>
                    <li><strong>⚡ Assistance prioritaire 7j/7 :</strong> une équipe à tes côtés à chaque étape.</li>
                </ul>
                <div style="font-size: 0.92rem; font-weight: 800; color: #92400e; margin-top: 0.6rem; padding-top: 0.6rem; border-top: 1px dashed #fde68a; display: flex; justify-content: space-between; align-items: baseline;">
                    <span>Formule Access+</span>
                    <span>2 000 FCFA / mois <span style="font-size: 0.78rem; font-weight: 500; opacity: 0.85;">• Sans engagement</span></span>
                </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                <a href="/mon-plan/" style="display: block; width: 100%; box-sizing: border-box; padding: 0.95rem 1.25rem; background: #f59e0b; color: white; border-radius: 0.85rem; font-weight: 800; font-size: 0.98rem; text-decoration: none; transition: transform 0.2s, background 0.2s, box-shadow 0.2s; box-shadow: 0 4px 14px rgba(245,158,11,0.3); text-align: center;" onmouseover="this.style.background='#d97706'" onmouseout="this.style.background='#f59e0b'">
                    👉 Voir comment suivre mes progrès
                </a>
                <a id="btn_go_dashboard_apprenant_secondary" href="#" style="display: block; padding: 0.65rem 0.75rem; background: transparent; color: #64748b; border: none; font-size: 0.86rem; font-weight: 600; text-decoration: underline; cursor: pointer; text-align: center; line-height: 1.4;">
                    Non merci, je continue sans mon espace de suivi ❯
                </a>
            </div>
        </div>

    </div>
</div>

'''

content = re.sub(old_modal_pattern, new_modal_html + r'\2', content, flags=re.DOTALL)

# Add responsive modal styles into <style> block
style_block = '''<style>
@keyframes scaleIn {
    from { transform: scale(0); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}

.eng-success-overlay {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.65);
    z-index: 5000;
    align-items: center;
    justify-content: center;
    padding: 1.25rem;
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
}

.eng-success-card {
    background: white;
    border-radius: 1.5rem;
    width: 100%;
    max-width: 480px;
    text-align: center;
    padding: 1.75rem 1.5rem;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    margin: auto;
    box-sizing: border-box;
}

@media (max-width: 640px) {
    .eng-success-overlay {
        padding: 0 !important;
        align-items: flex-start !important;
    }
    .eng-success-card {
        border-radius: 0 !important;
        max-width: 100% !important;
        min-height: 100dvh !important;
        min-height: 100vh;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        padding: max(1.75rem, env(safe-area-inset-top, 24px)) 1.25rem max(1.75rem, env(safe-area-inset-bottom, 24px)) !important;
        box-shadow: none !important;
    }
}'''

old_style_target = '''<style>
@keyframes scaleIn {
    from { transform: scale(0); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}'''

assert old_style_target in content, "old_style_target not found in content"
content = content.replace(old_style_target, style_block)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Modal refined successfully!")
