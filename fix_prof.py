import re

new_tabs = """<div class="tabs-header">
                    <button class="tab-btn active" onclick="switchTab(event, 'tab-programmes')">
                        Essai programmé
                        {% if badge_essais_programmes > 0 %}
                        <span style="background: #ef4444; color: white; font-size: 0.65rem; padding: 2px 6px; border-radius: 10px; margin-left: 4px; vertical-align: top; box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);">{{ badge_essais_programmes }}</span>
                        {% endif %}
                    </button>
                    <button class="tab-btn" onclick="switchTab(event, 'tab-confirmes')">
                        Essai confirmé
                        {% if badge_essais_confirmes > 0 %}
                        <span style="background: #ef4444; color: white; font-size: 0.65rem; padding: 2px 6px; border-radius: 10px; margin-left: 4px; vertical-align: top; box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);">{{ badge_essais_confirmes }}</span>
                        {% endif %}
                    </button>
                    <button class="tab-btn" onclick="switchTab(event, 'tab-finalises')">Finalisé</button>
                    <button class="tab-btn" onclick="switchTab(event, 'tab-termines')">Terminé</button>
                    <button class="tab-btn" onclick="switchTab(event, 'tab-history')">Historique</button>
                </div>"""

new_content = """<!-- Tab: Programmes -->
                <div id="tab-programmes" class="tab-content active">
                    {% if engs_essais_programmes %}
                        {% for eng in engs_essais_programmes %}
                            {% if not eng.masque_pour_professeur %}
                                {% include "core/components/engagement_card_teacher.html" with eng=eng %}
                            {% endif %}
                        {% endfor %}
                    {% else %}
                        <p style="text-align: center; color: var(--dash-text-muted); padding: 2rem; font-size: 0.875rem;">Aucun essai programmé.</p>
                    {% endif %}
                </div>

                <!-- Tab: Confirmes -->
                <div id="tab-confirmes" class="tab-content">
                    {% if engs_essais_confirmes %}
                        {% for eng in engs_essais_confirmes %}
                            {% if not eng.masque_pour_professeur %}
                                {% include "core/components/engagement_card_teacher.html" with eng=eng %}
                            {% endif %}
                        {% endfor %}
                    {% else %}
                        <p style="text-align: center; color: var(--dash-text-muted); padding: 2rem; font-size: 0.875rem;">Aucun essai confirmé.</p>
                    {% endif %}
                </div>

                <!-- Tab: Finalises -->
                <div id="tab-finalises" class="tab-content">
                    {% if engs_finalises %}
                        {% for eng in engs_finalises %}
                            {% if not eng.masque_pour_professeur %}
                                {% include "core/components/engagement_card_teacher.html" with eng=eng %}
                            {% endif %}
                        {% endfor %}
                    {% else %}
                        <p style="text-align: center; color: var(--dash-text-muted); padding: 2rem; font-size: 0.875rem;">Aucun engagement finalisé.</p>
                    {% endif %}
                </div>

                <!-- Tab: Termines -->
                <div id="tab-termines" class="tab-content">
                    {% if engs_termines %}
                        {% for eng in engs_termines %}
                            {% if not eng.masque_pour_professeur %}
                                {% include "core/components/engagement_card_teacher.html" with eng=eng %}
                            {% endif %}
                        {% endfor %}
                    {% else %}
                        <p style="text-align: center; color: var(--dash-text-muted); padding: 2rem; font-size: 0.875rem;">Aucun engagement terminé.</p>
                    {% endif %}
                </div>

                <!-- Tab: Historique -->
                <div id="tab-history" class="tab-content">
                    {% if engs_tous %}
                        {% for eng in engs_tous %}
                            {% if not eng.masque_pour_professeur %}
                                {% include "core/components/engagement_card_teacher.html" with eng=eng %}
                            {% endif %}
                        {% endfor %}
                    {% else %}
                        <p style="text-align: center; color: var(--dash-text-muted); padding: 2rem; font-size: 0.875rem;">Historique vide.</p>
                    {% endif %}
                </div>"""

with open('templates/core/prof_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

pattern_tabs = r'<div class="tabs-header">.*?</div>'
content = re.sub(pattern_tabs, new_tabs, content, flags=re.DOTALL)

pattern_content = r'<!-- Tab: Demandes -->.*?</div>\s*</div>\s*<div id="section-settings"'
content = re.sub(pattern_content, new_content + "\n            </div>\n        </div>\n\n        <div id=\"section-settings\"", content, flags=re.DOTALL)

with open('templates/core/prof_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
