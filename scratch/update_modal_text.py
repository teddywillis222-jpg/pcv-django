path = 'templates/core/components/engagement_modal.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Parent sub-text
old_parent_sub = '''                <p style="font-size: 0.88rem; color: #78350f; margin: 0 0 0.85rem 0; line-height: 1.55; font-weight: 500;">
                    Grâce à Access+, recevez le compte-rendu du professeur après chaque cours, suivez sa maîtrise des notions abordées et assurez-lui un encadrement solide.
                </p>'''

new_parent_sub = '''                <p style="font-size: 0.88rem; color: #78350f; margin: 0 0 0.85rem 0; line-height: 1.55; font-weight: 500;">
                    Grâce à Access+, recevez le compte-rendu du professeur après chaque cours, suivez la maîtrise des notions abordées avec <span id="eng_success_enfant_name_sub">votre enfant</span> et assurez-lui un encadrement solide.
                </p>'''

assert old_parent_sub in content, "old_parent_sub not found"
content = content.replace(old_parent_sub, new_parent_sub)

# 2. Parent bullet: notions assimilées -> notions maîtrisées
old_parent_bullet = '<li style="margin-bottom: 0.45rem;"><strong>📊 Espace de suivi en temps réel :</strong> bilans de chaque cours, notions assimilées et points à retravailler.</li>'
new_parent_bullet = '<li style="margin-bottom: 0.45rem;"><strong>📊 Espace de suivi en temps réel :</strong> bilans de chaque cours, notions maîtrisées et points à retravailler.</li>'

assert old_parent_bullet in content, "old_parent_bullet not found"
content = content.replace(old_parent_bullet, new_parent_bullet, 1)

# 3. Apprenant bullet: notions assimilées -> notions maîtrisées
assert old_parent_bullet in content, "apprenant bullet not found"
content = content.replace(old_parent_bullet, new_parent_bullet, 1)

# 4. JS update for eng_success_enfant_name_sub
old_js = '''                    const ctaChild = document.getElementById('eng_success_cta_child_parent');
                    if (ctaChild) ctaChild.textContent = childName;
                    document.getElementById('btn_go_dashboard_parent_secondary').href = '/parent/dashboard/';'''

new_js = '''                    const ctaChild = document.getElementById('eng_success_cta_child_parent');
                    if (ctaChild) ctaChild.textContent = childName;
                    const subChild = document.getElementById('eng_success_enfant_name_sub');
                    if (subChild) subChild.textContent = childName;
                    document.getElementById('btn_go_dashboard_parent_secondary').href = '/parent/dashboard/';'''

assert old_js in content, "old_js not found"
content = content.replace(old_js, new_js)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Modal copy updated successfully!")
