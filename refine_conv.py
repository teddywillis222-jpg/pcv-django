import sys, re
sys.stdout.reconfigure(encoding='utf-8')
path = 'templates/core/conversation_detail.html'
text = open(path, 'r', encoding='utf-8').read()

old_block = r'''{% if role == ROLE_PARENT or role == ROLE_APPRENANT %}.*?{% endif %}'''
# wait, the regex will match everything until the last {% endif %} in the document.

start = text.find('{% if role == ROLE_PARENT or role == ROLE_APPRENANT %}')
end = text.find('{% elif role == ROLE_PROF %}', start)

new_block = '''{% if role == ROLE_PARENT or role == ROLE_APPRENANT %}
                    {% if eng.statut_general in "EN_ATTENTE,ESSAI_PROGRAMME,ESSAI_CONFIRME" %}
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 0.85rem; margin: 1rem 1rem 1.5rem 1rem; text-align: center; color: #475569; font-size: 0.85rem; box-shadow: 0 2px 4px rgba(0,0,0,0.02); line-height: 1.4;">
                        📍 <strong>Préparation de l'essai</strong><br>
                        Précisez votre adresse et {% if role == ROLE_PARENT %}les besoins de {% if eng.enfants_concernes.first %}{{ eng.enfants_concernes.first.prenom }}{% else %}l'enfant{% endif %}{% else %}vos besoins{% endif %}.<br>
                        L'essai est gratuit. L'Espace de Suivi sera débloqué après validation de la collaboration.
                    </div>
                    {% elif eng.statut_general == 'ESSAI_REALISE' %}
                    <div style="background: #fdf4ff; border: 1px solid #f5d0fe; border-radius: 12px; padding: 0.85rem; margin: 1rem 1rem 1.5rem 1rem; text-align: center; color: #701a75; font-size: 0.85rem; box-shadow: 0 2px 4px rgba(0,0,0,0.02); line-height: 1.4;">
                        💡 <strong>L'essai est terminé ?</strong> Si vous souhaitez poursuivre, <a href="{% url 'finalisation_engagement' eng.id %}" style="color: #c026d3; font-weight: 800; text-decoration: underline; text-underline-offset: 3px; text-decoration-thickness: 2px;">Activer ici la formule Access+ (2 000 F)</a> et officialiser votre collaboration avec {{ eng.professeur.prenom }} pour débloquer {% if role == ROLE_PARENT %}l'espace de suivi de {% if eng.enfants_concernes.first %}{{ eng.enfants_concernes.first.prenom }}{% else %}l'enfant{% endif %}{% else %}votre espace de suivi{% endif %}.
                    </div>
                    {% endif %}
                '''

if start != -1 and end != -1:
    text = text[:start] + new_block + text[end:]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated text perfectly")
else:
    print("Could not find start or end")
