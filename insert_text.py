import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('templates/core/prof_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

target = """                <div style="padding: 1.5rem 2rem; background: #f8fafc; color: var(--dash-text-muted, #64748b); font-size: 0.9rem; line-height: 1.5; border-top: 1px solid var(--dash-border, #f1f5f9);">
                    Continuez à renseigner vos bilans de séance et à répondre aux demandes des familles pour faire progresser votre score.
                </div>
            </div>"""

replacement = target + """
            
            <!-- Informations explicatives -->
            <div style="margin-top: 2rem; padding: 0 0.5rem; color: var(--dash-text-muted, #475569); line-height: 1.6; font-size: 0.95rem;">
                <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--dash-text, #0f172a); margin-bottom: 0.75rem;">Le score de fiabilité : que devez-vous savoir à propos ?</h3>
                <p style="margin-bottom: 1.5rem;">Votre score de fiabilité reflète votre régularité et votre sérieux dans l’utilisation de Prof Chez Vous. Il évolue au fil de vos actions sur la plateforme et permet de mieux valoriser votre fiabilité dans votre parcours de professeur.</p>

                <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--dash-text, #0f172a); margin-bottom: 0.75rem;">Découvrez comment il est établi</h3>
                <p style="margin-bottom: 1.5rem;">Votre score est constitué progressivement à partir de plusieurs éléments liés à votre activité sur Prof Chez Vous : la régularité dans le suivi des séances, votre réactivité face aux demandes d’essai, les collaborations menées à leur terme et les appréciations reçues des familles.<br>Chaque élément contribue à votre score selon des règles précises.</p>

                <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--dash-text, #0f172a); margin-bottom: 0.75rem;">Quel impact a-t-il réellement pour vous ?</h3>
                <p style="margin-bottom: 1.5rem;">Le score de fiabilité permet de mieux valoriser votre sérieux auprès des familles. À profil comparable, un score plus élevé peut contribuer à mieux positionner votre profil parmi les professeurs correspondant à la recherche d'une famille.<br>Il ne constitue toutefois pas le seul critère de classement : les matières enseignées, les niveaux, la localisation, les disponibilités, les avis et les informations de votre profil sont également pris en compte.</p>

                <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--dash-text, #0f172a); margin-bottom: 0.75rem;">Comment entretenir un bon score de fiabilité ?</h3>
                <p style="margin-bottom: 1.5rem;">Il n’est pas nécessaire de chercher à « maximiser » votre score artificiellement. Le meilleur moyen de l’entretenir est simplement d’être régulier et sérieux dans vos engagements.<br><br>Renseignez vos journaux de séance après les cours, répondez aux demandes d’essai dans des délais raisonnables, honorez vos collaborations et accordez de l’importance à la qualité de vos accompagnements.<br><br>Votre score se construit ainsi naturellement au fil de votre activité.</p>
            </div>"""

if "Le score de fiabilité : que devez-vous savoir à propos ?" not in text:
    if target in text:
        text = text.replace(target, replacement)
        with open('templates/core/prof_dashboard.html', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Mise à jour réussie")
    else:
        print("Cible non trouvée")
else:
    print("Déjà ajouté")
