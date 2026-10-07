import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

path = 'templates/core/components/engagement_modal.html'
text = open(path, 'r', encoding='utf-8').read()

# Replace the innerHTML of engagementSuccessModal
old_modal_inner = r'<h3 style="font-size: 1\.5rem; font-weight: 800; color: #1e293b; margin-bottom: 0\.75rem;" id="eng_success_title">Proposition envoyée !</h3>\s*<p id="eng_success_desc" style="color: #64748b; margin-bottom: 2rem; line-height: 1\.6;">Votre proposition d\'engagement a été soumise avec succès\. Le professeur a été notifié et vous répondra très bientôt\.</p>\s*<div style="display: flex; flex-direction: column; gap: 0\.75rem;">\s*<a id="btn_go_dashboard" href="#" style="padding: 1rem; background: #16a34a; color: white; border-radius: 0\.75rem; font-weight: 700; text-decoration: none; transition: transform 0\.2s;">Accéder à mon espace</a>\s*<button onclick="closeEngagementSuccessModal\(\)" style="padding: 1rem; background: #f1f5f9; color: #475569; border: none; border-radius: 0\.75rem; font-weight: 700; cursor: pointer;">Rester sur cette page</button>\s*</div>'

new_modal_inner = '''
        <!-- STANDARD SUCCESS -->
        <div id="eng_success_standard" style="display: none;">
            <h3 style="font-size: 1.5rem; font-weight: 800; color: #1e293b; margin-bottom: 0.75rem;">Proposition envoyée !</h3>
            <p style="color: #64748b; margin-bottom: 2rem; line-height: 1.6;">Votre proposition d'engagement a été soumise avec succès. Le professeur a été notifié et vous répondra très bientôt.</p>
            <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                <a id="btn_go_dashboard_standard" href="#" style="padding: 1rem; background: #16a34a; color: white; border-radius: 0.75rem; font-weight: 700; text-decoration: none; transition: transform 0.2s;">Accéder à mon espace</a>
                <button onclick="closeEngagementSuccessModal()" style="padding: 1rem; background: #f1f5f9; color: #475569; border: none; border-radius: 0.75rem; font-weight: 700; cursor: pointer;">Rester sur cette page</button>
            </div>
        </div>

        <!-- ESSAI SUCCESS (PARENT) -->
        <div id="eng_success_essai_parent" style="display: none; text-align: center;">
            <h3 style="font-size: 1.5rem; font-weight: 800; color: #1e293b; margin-bottom: 0.75rem;">Essai programmé !</h3>
            <p style="color: #64748b; margin-bottom: 1.5rem; line-height: 1.6;">Votre demande a été transmise à <strong id="eng_success_prof_name_parent">ce professeur</strong>.<br>Vous recevrez une notification dès sa confirmation.</p>
            
            <hr style="border: 0; border-top: 1px dashed #cbd5e1; margin: 1.5rem 0;">
            
            <div style="background: #fdf4ff; border: 1px solid #f5d0fe; border-radius: 1rem; padding: 1.25rem; margin-bottom: 1.5rem; text-align: left;">
                <h4 style="font-size: 1rem; font-weight: 800; color: #86198f; margin: 0 0 0.75rem 0; display: flex; align-items: center; gap: 0.5rem;">
                    <span>🎁</span> PENSEZ À LA SUITE AVEC LA FORMULE ACCESS+
                </h4>
                <p style="font-size: 0.85rem; color: #4a044e; margin: 0 0 0.75rem 0; font-weight: 600;">Pour seulement 2 000 FCFA/mois, débloquez :</p>
                <ul style="font-size: 0.85rem; color: #701a75; margin: 0; padding-left: 1.25rem; line-height: 1.5;">
                    <li>Le Cahier de suivi digital de <strong id="eng_success_enfant_name">votre enfant</strong></li>
                    <li>La Garantie de remplacement gratuit si besoin</li>
                    <li>La possibilité de programmer d'autres essais</li>
                </ul>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                <a href="/parent/plan/" style="padding: 1rem; background: #c026d3; color: white; border-radius: 0.75rem; font-weight: 700; text-decoration: none; transition: transform 0.2s;">Découvrir la formule Access+</a>
                <a id="btn_go_dashboard_parent_secondary" href="#" style="padding: 1rem; background: transparent; color: #64748b; border: none; border-radius: 0.75rem; font-weight: 600; text-decoration: underline; cursor: pointer;">Non merci, je continue sans le suivi de <span id="eng_success_enfant_name_btn">mon enfant</span> ❯</a>
            </div>
        </div>

        <!-- ESSAI SUCCESS (APPRENANT) -->
        <div id="eng_success_essai_apprenant" style="display: none; text-align: center;">
            <h3 style="font-size: 1.5rem; font-weight: 800; color: #1e293b; margin-bottom: 0.75rem;">Essai programmé !</h3>
            <p style="color: #64748b; margin-bottom: 1.5rem; line-height: 1.6;">Votre demande a été transmise à <strong id="eng_success_prof_name_apprenant">ce professeur</strong>.<br>Vous recevrez une notification dès sa confirmation.</p>
            
            <hr style="border: 0; border-top: 1px dashed #cbd5e1; margin: 1.5rem 0;">
            
            <div style="background: #fdf4ff; border: 1px solid #f5d0fe; border-radius: 1rem; padding: 1.25rem; margin-bottom: 1.5rem; text-align: left;">
                <h4 style="font-size: 1rem; font-weight: 800; color: #86198f; margin: 0 0 0.75rem 0; display: flex; align-items: center; gap: 0.5rem;">
                    <span>🎁</span> PENSEZ À LA SUITE AVEC LA FORMULE ACCESS+
                </h4>
                <ul style="font-size: 0.85rem; color: #701a75; margin: 0; padding-left: 1.25rem; line-height: 1.5;">
                    <li>Votre Tableau de bord de progression & historique des séances</li>
                    <li>La garantie de changer de professeur à tout moment</li>
                    <li>Des essais illimités pour couvrir toutes vos matières</li>
                </ul>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                <a href="/apprenant/plan/" style="padding: 1rem; background: #c026d3; color: white; border-radius: 0.75rem; font-weight: 700; text-decoration: none; transition: transform 0.2s;">Découvrir la formule Access+</a>
                <a id="btn_go_dashboard_apprenant_secondary" href="#" style="padding: 1rem; background: transparent; color: #64748b; border: none; border-radius: 0.75rem; font-weight: 600; text-decoration: underline; cursor: pointer;">Non merci, je continue sans mon outil de suivi personnel ❯</a>
            </div>
        </div>
'''

if 'id="eng_success_title"' in text and 'btn_go_dashboard' in text:
    text = re.sub(old_modal_inner, new_modal_inner, text, flags=re.DOTALL)
    print("Modal HTML updated.")
else:
    print("Modal HTML pattern not found.")

# Replace the JS logic
old_js = r'''if \(data\.engagement_type === 'essai'\) \{.*?document\.getElementById\('eng_success_title'\)\.textContent = "Essai programmé !";.*?document\.getElementById\('eng_success_desc'\)\.textContent = "L'essai a été programmé avec succès\. Le professeur a reçu directement une notification pour pouvoir voir et confirmer\. Dès confirmation, un message vous sera envoyé pour vous préparer à la séance d'essai\.";.*?\} else \{.*?document\.getElementById\('eng_success_title'\)\.textContent = "Proposition envoyée !";.*?document\.getElementById\('eng_success_desc'\)\.textContent = "Votre proposition d'engagement a été soumise avec succès\. Le professeur a été notifié et vous répondra très bientôt\.";.*?\}[\s]*const dashBtn = document\.getElementById\('btn_go_dashboard'\);[\s]*const isParent = currentTeacherData && currentTeacherData\.is_parent;[\s]*dashBtn\.href = isParent \? '/parent/dashboard/' : '/apprenant/dashboard/';'''

new_js = '''const isParent = currentTeacherData && currentTeacherData.is_parent;
            
            document.getElementById('eng_success_standard').style.display = 'none';
            document.getElementById('eng_success_essai_parent').style.display = 'none';
            document.getElementById('eng_success_essai_apprenant').style.display = 'none';

            if (data.engagement_type === 'essai') {
                const profName = document.getElementById('essai_teacher_name_hidden').value || "ce professeur";
                
                if (isParent) {
                    let childName = "votre enfant";
                    const childSelect = document.getElementById('essai_enfant_id');
                    if (data.enfant_id && data.enfant_id !== 'new' && childSelect && childSelect.selectedIndex >= 0) {
                        childName = childSelect.options[childSelect.selectedIndex].text;
                    } else if (data.nouveau_prenom_enfant) {
                        childName = data.nouveau_prenom_enfant;
                    }
                    
                    document.getElementById('eng_success_prof_name_parent').textContent = "Prof. " + profName;
                    document.getElementById('eng_success_enfant_name').textContent = childName;
                    document.getElementById('eng_success_enfant_name_btn').textContent = childName;
                    document.getElementById('btn_go_dashboard_parent_secondary').href = '/parent/dashboard/';
                    document.getElementById('eng_success_essai_parent').style.display = 'block';
                } else {
                    document.getElementById('eng_success_prof_name_apprenant').textContent = "Prof. " + profName;
                    document.getElementById('btn_go_dashboard_apprenant_secondary').href = '/apprenant/dashboard/';
                    document.getElementById('eng_success_essai_apprenant').style.display = 'block';
                }
            } else {
                document.getElementById('btn_go_dashboard_standard').href = isParent ? '/parent/dashboard/' : '/apprenant/dashboard/';
                document.getElementById('eng_success_standard').style.display = 'block';
            }'''

if 'dashBtn.href = isParent' in text:
    text = re.sub(old_js, new_js, text, flags=re.DOTALL)
    print("JS logic updated.")
else:
    print("JS logic pattern not found.")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("File written.")
