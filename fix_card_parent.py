import re

with open('templates/core/components/engagement_card_parent.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace footer options
new_footer = """<!-- Footer : Bouton principal et Options -->
    <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 1rem; border-top: 1px solid #f1f5f9; gap: 0.75rem;">
        {% if eng.statut_general == 'ESSAI_REALISE' %}
            <a href="{% url 'suivi_engagement' eng.id %}" class="btn-eng-main" style="flex: 1; text-align: center; background: var(--primary); color: white; padding: 0.7rem; border-radius: 12px; font-weight: 700; font-size: 0.85rem; text-decoration: none; box-shadow: 0 4px 12px rgba(22, 163, 74, 0.2);">
                ✨ Finaliser l'engagement
            </a>
        {% elif eng.statut_general != 'REFUSE' and eng.statut_general != 'ESSAI_PROGRAMME' and eng.statut_general != 'EN_ATTENTE' and eng.statut_general != 'ESSAI_REALISE' and eng.type_engagement != 'ESSAI' %}
            <a href="{% url 'suivi_engagement' eng.id %}" class="btn-eng-main" style="flex: 1; text-align: center; background: var(--primary); color: white; padding: 0.7rem; border-radius: 12px; font-weight: 700; font-size: 0.85rem; text-decoration: none;">
                Accéder à l'espace de l'engagement
            </a>
        {% elif eng.statut_general == 'ESSAI_CONFIRME' %}
             <button onclick="convertirEnEngagement({{ eng.id }})" class="btn-eng-main" style="flex: 1; text-align: center; background: var(--primary); color: white; padding: 0.7rem; border-radius: 12px; font-weight: 700; font-size: 0.85rem; border: none; cursor: pointer; box-shadow: 0 4px 12px rgba(22, 163, 74, 0.2);">
                ✨ Engager ce professeur
             </button>
        {% else %}
             <button onclick="openDetailModal({{ eng.id }})" class="btn-eng-main" style="flex: 1; text-align: center; background: #f1f5f9; color: var(--text-dark); padding: 0.7rem; border-radius: 12px; font-weight: 700; font-size: 0.85rem; border: none; cursor: pointer;">
                {% if eng.type_engagement == 'ESSAI' %}Voir l'essai{% else %}Voir les détails{% endif %}
             </button>
        {% endif %}
        
        <div style="position: relative;">
            <button class="options-btn" onclick="toggleOptions(this)" style="background: #f1f5f9; border: none; width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: var(--text-gray);">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
            </button>
            
            <div class="options-menu" style="display: none; position: absolute; bottom: 3.5rem; right: 0; background: white; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.15); z-index: 100; width: 220px; border: 1px solid #f1f5f9; overflow: hidden;">
                <!-- Accéder à l'espace de l'engagement (dans le menu si ESSAI_REALISE) -->
                {% if eng.statut_general == 'ESSAI_REALISE' %}
                <a href="{% url 'suivi_engagement' eng.id %}" class="menu-item" style="display: block; padding: 0.85rem 1rem; color: var(--text-dark); text-decoration: none; font-size: 0.9rem; font-weight: 600; border-bottom: 1px solid #f1f5f9;">
                    📁 Accéder à l'espace de l'engagement
                </a>
                {% endif %}

                <!-- Modifier ma proposition -->
                {% if eng.statut_general == 'ESSAI_PROGRAMME' and eng.professeur %}
                <a href="{% url 'professeur_detail' eng.professeur.slug %}" class="menu-item" style="display: block; padding: 0.85rem 1rem; color: var(--text-dark); text-decoration: none; font-size: 0.9rem; font-weight: 600; border-bottom: 1px solid #f1f5f9;">
                    ✏️ Modifier ma proposition
                </a>
                {% endif %}

                <!-- Messagerie -->
                {% if eng.conversation %}
                <a href="{% url 'conversation_detail' eng.conversation.id %}" class="menu-item" style="display: block; padding: 0.85rem 1rem; color: var(--text-dark); text-decoration: none; font-size: 0.9rem; font-weight: 600; border-bottom: 1px solid #f1f5f9;">
                    💬 Rejoindre la conversation
                </a>
                {% endif %}

                <!-- Actions de gestion (Seulement si Finalisé) -->
                {% if eng.statut_general == 'FINALISE' %}
                <button type="button" class="menu-item" onclick="openClotureModal('{{ eng.id }}', '{% if eng.cloture_initiee_par %}{{ eng.cloture_initiee_par.id }}{% endif %}')" style="display: block; width: 100%; text-align: left; background: none; border: none; padding: 0.85rem 1rem; color: var(--text-dark); font-size: 0.9rem; font-weight: 600; border-bottom: 1px solid #f1f5f9; cursor: pointer;">
                    {% if not eng.cloture_initiee_par %}
                        ✅ Demander la clôture
                    {% elif eng.cloture_initiee_par == user %}
                        ⏳ Clôture en attente
                    {% else %}
                        ✅ Confirmer la clôture
                    {% endif %}
                </button>
                <button type="button" class="menu-item danger" onclick="openAnnulationModal('{{ eng.id }}', '{% if eng.annulation_initiee_par %}{{ eng.annulation_initiee_par.id }}{% endif %}')" style="display: block; width: 100%; text-align: left; background: none; border: none; padding: 0.85rem 1rem; color: #ef4444; font-size: 0.9rem; font-weight: 600; border-bottom: 1px solid #f1f5f9; cursor: pointer;">
                    {% if not eng.annulation_initiee_par %}
                        🚫 Demander l'annulation
                    {% elif eng.annulation_initiee_par == user %}
                        ⏳ Annulation en attente
                    {% else %}
                        🚫 Confirmer l'annulation
                    {% endif %}
                </button>
                {% endif %}

                <!-- Avis / Note -->
                {% if eng.statut_general == 'FINALISE' or eng.statut_general == 'TERMINE' or eng.statut_general == 'ANNULE' %}
                <button type="button" class="menu-item" onclick="openRatingModal('{{ eng.id }}', '{{ eng.evaluation_liee.note|default:0 }}', '{{ eng.evaluation_liee.commentaire|default:""|escapejs }}')" style="display: block; width: 100%; text-align: left; background: none; border: none; padding: 0.85rem 1rem; color: var(--text-dark); font-size: 0.9rem; font-weight: 600; border-bottom: 1px solid #f1f5f9; cursor: pointer;">
                    {% if eng.evaluation_liee %}
                    ⭐ Modifier votre avis
                    {% else %}
                    ⭐ Noter ce prof
                    {% endif %}
                </button>
                {% endif %}

                <!-- Favoris -->
                {% if eng.professeur %}
                <button type="button" class="menu-item fav-eng-btn {% if user.is_authenticated and user in eng.professeur.parents_favoris.all %}active{% endif %}" onclick="toggleFavoriteAjax(this, '{{ eng.professeur.id }}')" style="display: flex; align-items: center; gap: 0.5rem; width: 100%; text-align: left; padding: 0.85rem 1rem; background: none; border: none; color: var(--text-dark); text-decoration: none; font-size: 0.9rem; font-weight: 600; border-bottom: 1px solid #f1f5f9; cursor: pointer;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="{% if user.is_authenticated and user in eng.professeur.parents_favoris.all %}#ef4444{% else %}none{% endif %}" stroke="{% if user.is_authenticated and user in eng.professeur.parents_favoris.all %}#ef4444{% else %}currentColor{% endif %}" stroke-width="2" style="transition: all 0.3s ease; flex-shrink: 0;">
                        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                    </svg>
                    <span class="fav-text">{% if user.is_authenticated and user in eng.professeur.parents_favoris.all %}Retirer des favoris{% else %}Ajouter aux favoris{% endif %}</span>
                </button>
                {% endif %}

                <!-- Masquer (Toujours visible) -->
                <button type="button" class="menu-item" onclick="masquerEngagement('{{ eng.id }}', this)" style="display: block; width: 100%; text-align: left; padding: 0.85rem 1rem; background: none; border: none; color: var(--text-gray); text-decoration: none; font-size: 0.9rem; font-weight: 600; cursor: pointer;">
                    🗑️ Masquer l'engagement
                </button>
            </div>

        </div>
    </div>"""

pattern = r'<!-- Footer : Bouton principal et Options -->.*?</div>\s*</div>'
content = re.sub(pattern, new_footer, content, flags=re.DOTALL)

with open('templates/core/components/engagement_card_parent.html', 'w', encoding='utf-8') as f:
    f.write(content)
