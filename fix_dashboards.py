import re

new_tabs = """<div class="glass-tabs">
                    <button class="tab-pill active" onclick="switchTab(event, 'programmes')">
                        Essai programmé
                        {% if badge_essais_programmes > 0 %}
                        <span style="background: #ef4444; color: white; font-size: 0.65rem; padding: 2px 6px; border-radius: 10px; margin-left: 4px; vertical-align: top; box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);">{{ badge_essais_programmes }}</span>
                        {% endif %}
                    </button>
                    <button class="tab-pill" onclick="switchTab(event, 'confirmes')">
                        Essai confirmé
                        {% if badge_essais_confirmes > 0 %}
                        <span style="background: #ef4444; color: white; font-size: 0.65rem; padding: 2px 6px; border-radius: 10px; margin-left: 4px; vertical-align: top; box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);">{{ badge_essais_confirmes }}</span>
                        {% endif %}
                    </button>
                    <button class="tab-pill" onclick="switchTab(event, 'finalises')">Finalisé</button>
                    <button class="tab-pill" onclick="switchTab(event, 'termines')">Terminé</button>
                </div>"""

new_content = """<div id="tab-content">
                    <div class="tab-pane" id="programmes">
                        {% for eng in engagements_essais_programmes %}
                        {% include "core/components/engagement_card_parent.html" with eng=eng status_class="badge-attente" %}
                        {% empty %}
                        <p style="text-align: center; padding: 1.5rem; color: var(--text-gray); font-size: 0.8rem;">Aucun essai programmé.</p>
                        {% endfor %}
                    </div>
                    <div class="tab-pane" id="confirmes" style="display: none;">
                        {% for eng in engagements_essais_confirmes %}
                        {% include "core/components/engagement_card_parent.html" with eng=eng status_class="badge-actif" %}
                        {% empty %}
                        <p style="text-align: center; padding: 1.5rem; color: var(--text-gray); font-size: 0.8rem;">Aucun essai confirmé.</p>
                        {% endfor %}
                    </div>
                    <div class="tab-pane" id="finalises" style="display: none;">
                        {% for eng in engagements_finalises %}
                        {% include "core/components/engagement_card_parent.html" with eng=eng status_class="badge-actif" show_actions=True %}
                        {% empty %}
                        <p style="text-align: center; padding: 1.5rem; color: var(--text-gray); font-size: 0.8rem;">Aucun engagement finalisé.</p>
                        {% endfor %}
                    </div>
                    <div class="tab-pane" id="termines" style="display: none;">
                        {% for eng in engagements_termines %}
                        {% include "core/components/engagement_card_parent.html" with eng=eng status_class="badge-termine" %}
                        {% empty %}
                        <p style="text-align: center; padding: 1.5rem; color: var(--text-gray); font-size: 0.8rem;">Historique vide.</p>
                        {% endfor %}
                    </div>
                </div>"""

def update_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # regex to replace <div class="glass-tabs">...</div>
    pattern_tabs = r'<div class="glass-tabs">.*?</div>'
    content = re.sub(pattern_tabs, new_tabs, content, flags=re.DOTALL)
    
    # regex to replace <div id="tab-content">...</div>
    pattern_content = r'<div id="tab-content">.*?</div>\s*</section>'
    content = re.sub(pattern_content, new_content + "\n            </section>", content, flags=re.DOTALL)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

update_file('templates/core/parent_dashboard.html')
update_file('templates/core/apprenant_dashboard.html')
