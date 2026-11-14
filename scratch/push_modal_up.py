path = 'templates/core/components/engagement_modal.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update card inner elements for Parent & Apprenant to be slightly tighter vertically while preserving typography
old_parent = '''        <!-- ESSAI SUCCESS (PARENT) -->
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
                    Grâce à Access+, recevez le compte-rendu du professeur après chaque cours, suivez la maîtrise des notions abordées avec <span id="eng_success_enfant_name_sub">votre enfant</span> et assurez-lui un encadrement solide.
                </p>
                <ul style="font-size: 0.86rem; color: #78350f; margin: 0 0 0.85rem 0; padding-left: 1.25rem; line-height: 1.55;">
                    <li style="margin-bottom: 0.45rem;"><strong>📊 Espace de suivi en temps réel :</strong> bilans de chaque cours, notions maîtrisées et points à retravailler.</li>
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
        </div>'''

new_parent = '''        <!-- ESSAI SUCCESS (PARENT) -->
        <div id="eng_success_essai_parent" style="display: none; text-align: center;">
            <h3 style="font-size: 1.3rem; font-weight: 800; color: #0f172a; margin: 0 0 0.3rem 0; line-height: 1.3;">Essai programmé avec succès !</h3>
            <p style="color: #64748b; font-size: 0.88rem; margin: 0 0 0.75rem 0; line-height: 1.45;">
                Votre demande a été transmise à <strong id="eng_success_prof_name_parent" style="color: #0f172a;">ce professeur</strong>.<br>Vous recevrez une notification dès sa confirmation.
            </p>
            
            <hr style="border: 0; border-top: 1px dashed #cbd5e1; margin: 0.65rem 0 0.85rem 0;">
            
            <div style="background: #fffbeb; border: 1.5px solid #fde68a; border-radius: 0.95rem; padding: 1rem 1.15rem; margin-bottom: 0.95rem; text-align: left;">
                <h4 style="font-size: 1rem; font-weight: 800; color: #92400e; margin: 0 0 0.45rem 0; line-height: 1.4;">
                    💡 Et si vous pouviez mesurer concrètement chaque progrès de <span id="eng_success_enfant_name">votre enfant</span> ?
                </h4>
                <p style="font-size: 0.85rem; color: #78350f; margin: 0 0 0.65rem 0; line-height: 1.5; font-weight: 500;">
                    Grâce à Access+, recevez le compte-rendu du professeur après chaque cours, suivez la maîtrise des notions abordées avec <span id="eng_success_enfant_name_sub">votre enfant</span> et assurez-lui un encadrement solide.
                </p>
                <ul style="font-size: 0.84rem; color: #78350f; margin: 0 0 0.65rem 0; padding-left: 1.2rem; line-height: 1.5;">
                    <li style="margin-bottom: 0.35rem;"><strong>📊 Espace de suivi en temps réel :</strong> bilans de chaque cours, notions maîtrisées et points à retravailler.</li>
                    <li style="margin-bottom: 0.35rem;"><strong>🛡️ Garantie de remplacement :</strong> changez de professeur sans frais si besoin.</li>
                    <li><strong>⚡ Assistance prioritaire 7j/7 :</strong> une équipe à vos côtés à chaque étape.</li>
                </ul>
                <div style="font-size: 0.88rem; font-weight: 800; color: #92400e; margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px dashed #fde68a; display: flex; justify-content: space-between; align-items: baseline;">
                    <span>Formule Access+</span>
                    <span>2 000 FCFA / mois <span style="font-size: 0.75rem; font-weight: 500; opacity: 0.85;">• Sans engagement</span></span>
                </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.35rem;">
                <a href="/mon-plan/" style="display: block; width: 100%; box-sizing: border-box; padding: 0.88rem 1.15rem; background: #f59e0b; color: white; border-radius: 0.8rem; font-weight: 800; font-size: 0.95rem; text-decoration: none; transition: transform 0.2s, background 0.2s, box-shadow 0.2s; box-shadow: 0 4px 14px rgba(245,158,11,0.3); text-align: center;" onmouseover="this.style.background='#d97706'" onmouseout="this.style.background='#f59e0b'">
                    👉 Voir comment suivre les progrès de <span id="eng_success_cta_child_parent">votre enfant</span>
                </a>
                <a id="btn_go_dashboard_parent_secondary" href="#" style="display: block; padding: 0.5rem 0.5rem; background: transparent; color: #64748b; border: none; font-size: 0.84rem; font-weight: 600; text-decoration: underline; cursor: pointer; text-align: center; line-height: 1.35;">
                    Non merci, je continue sans suivi pour <span id="eng_success_enfant_name_btn">mon enfant</span> ❯
                </a>
            </div>
        </div>'''

assert old_parent in content, "old_parent not found"
content = content.replace(old_parent, new_parent)

# 2. Update card inner elements for Apprenant
old_apprenant = '''        <!-- ESSAI SUCCESS (APPRENANT) -->
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
                    <li style="margin-bottom: 0.45rem;"><strong>📊 Espace de suivi en temps réel :</strong> bilans de chaque cours, notions maîtrisées et points à retravailler.</li>
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
        </div>'''

new_apprenant = '''        <!-- ESSAI SUCCESS (APPRENANT) -->
        <div id="eng_success_essai_apprenant" style="display: none; text-align: center;">
            <h3 style="font-size: 1.3rem; font-weight: 800; color: #0f172a; margin: 0 0 0.3rem 0; line-height: 1.3;">Essai programmé avec succès !</h3>
            <p style="color: #64748b; font-size: 0.88rem; margin: 0 0 0.75rem 0; line-height: 1.45;">
                Votre demande a été transmise à <strong id="eng_success_prof_name_apprenant" style="color: #0f172a;">ce professeur</strong>.<br>Vous recevrez une notification dès sa confirmation.
            </p>
            
            <hr style="border: 0; border-top: 1px dashed #cbd5e1; margin: 0.65rem 0 0.85rem 0;">
            
            <div style="background: #fffbeb; border: 1.5px solid #fde68a; border-radius: 0.95rem; padding: 1rem 1.15rem; margin-bottom: 0.95rem; text-align: left;">
                <h4 style="font-size: 1rem; font-weight: 800; color: #92400e; margin: 0 0 0.45rem 0; line-height: 1.4;">
                    💡 Et si tu pouvais mesurer concrètement tes progrès ?
                </h4>
                <p style="font-size: 0.85rem; color: #78350f; margin: 0 0 0.65rem 0; line-height: 1.5; font-weight: 500;">
                    Grâce à Access+, reçois le compte-rendu du professeur après chaque cours, suis ta maîtrise des notions abordées et profite d'un encadrement solide.
                </p>
                <ul style="font-size: 0.84rem; color: #78350f; margin: 0 0 0.65rem 0; padding-left: 1.2rem; line-height: 1.5;">
                    <li style="margin-bottom: 0.35rem;"><strong>📊 Espace de suivi en temps réel :</strong> bilans de chaque cours, notions maîtrisées et points à retravailler.</li>
                    <li style="margin-bottom: 0.35rem;"><strong>🛡️ Garantie de remplacement :</strong> change de professeur sans frais si besoin.</li>
                    <li><strong>⚡ Assistance prioritaire 7j/7 :</strong> une équipe à tes côtés à chaque étape.</li>
                </ul>
                <div style="font-size: 0.88rem; font-weight: 800; color: #92400e; margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px dashed #fde68a; display: flex; justify-content: space-between; align-items: baseline;">
                    <span>Formule Access+</span>
                    <span>2 000 FCFA / mois <span style="font-size: 0.75rem; font-weight: 500; opacity: 0.85;">• Sans engagement</span></span>
                </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.35rem;">
                <a href="/mon-plan/" style="display: block; width: 100%; box-sizing: border-box; padding: 0.88rem 1.15rem; background: #f59e0b; color: white; border-radius: 0.8rem; font-weight: 800; font-size: 0.95rem; text-decoration: none; transition: transform 0.2s, background 0.2s, box-shadow 0.2s; box-shadow: 0 4px 14px rgba(245,158,11,0.3); text-align: center;" onmouseover="this.style.background='#d97706'" onmouseout="this.style.background='#f59e0b'">
                    👉 Voir comment suivre mes progrès
                </a>
                <a id="btn_go_dashboard_apprenant_secondary" href="#" style="display: block; padding: 0.5rem 0.5rem; background: transparent; color: #64748b; border: none; font-size: 0.84rem; font-weight: 600; text-decoration: underline; cursor: pointer; text-align: center; line-height: 1.35;">
                    Non merci, je continue sans mon espace de suivi ❯
                </a>
            </div>
        </div>'''

assert old_apprenant in content, "old_apprenant not found"
content = content.replace(old_apprenant, new_apprenant)

# 3. Adjust top icon margin
old_icon = 'margin: 0 auto 0.85rem;'
new_icon = 'margin: 0 auto 0.5rem;'
content = content.replace(old_icon, new_icon, 1)

# 4. Update CSS media query to align to top and offset slightly so both buttons are prominent
old_media = '''@media (max-width: 640px) {
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

new_media = '''@media (max-width: 640px) {
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
        justify-content: flex-start !important;
        padding: max(1.1rem, env(safe-area-inset-top, 16px)) 1.2rem max(1.25rem, env(safe-area-inset-bottom, 16px)) !important;
        box-shadow: none !important;
    }
}'''

assert old_media in content, "old_media not found"
content = content.replace(old_media, new_media)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Modal pushed up successfully!")
