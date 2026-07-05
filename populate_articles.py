import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from help_center.models import Category, Article
from django.utils.text import slugify

# Base URL for internal links
BASE = "/centre-daide"

def link(cat_slug, art_slug, text):
    """Helper to generate an internal link to another help center article."""
    return f'<a href="{BASE}/{cat_slug}/{art_slug}/">{text}</a>'

# Shortcut link builders per category
def lp(slug, text): return link("parents", slug, text)
def lt(slug, text): return link("professeurs", slug, text)
def la(slug, text): return link("a-propos", slug, text)


def run():
    # =========================================================================
    # 1. Categories
    # =========================================================================
    cat_parents, _ = Category.objects.update_or_create(
        slug="parents",
        defaults={
            "name": "Parents & Apprenants",
            "description": "Tout ce qu'un parent doit savoir pour utiliser Prof Chez Vous en toute confiance.",
            "icon": "bi bi-people",
            "order": 1,
            "target_audience": "parents"
        }
    )
    
    cat_profs, _ = Category.objects.update_or_create(
        slug="professeurs",
        defaults={
            "name": "Professeurs",
            "description": "Guides pour les professeurs partenaires de la plateforme.",
            "icon": "bi bi-mortarboard",
            "order": 2,
            "target_audience": "teachers"
        }
    )
    
    cat_apropos, _ = Category.objects.update_or_create(
        slug="a-propos",
        defaults={
            "name": "A propos de Prof Chez Vous",
            "description": "Notre mission, notre vision et nos engagements.",
            "icon": "bi bi-info-circle",
            "order": 3,
            "target_audience": "all"
        }
    )

    # =========================================================================
    # 2. Articles - PARENTS
    # =========================================================================
    articles_data = [
        {
            "category": cat_parents,
            "title": "Qu'est-ce que Prof Chez Vous ?",
            "slug": "quest-ce-que-prof-chez-vous",
            "keywords": "plateforme, presentation, concept, professeurs, benin, soutien scolaire, mise en relation, profils verifies",
            "order": 1,
            "content": f"""
<h2>Réponse rapide</h2>
<p>Prof Chez Vous est une plateforme béninoise de mise en relation qui permet aux parents et aux apprenants de trouver facilement un professeur particulier correspondant à leurs besoins.</p>
<p>Contrairement aux méthodes traditionnelles reposant sur les recommandations ou le bouche-à-oreille, Prof Chez Vous offre un espace où les parents peuvent consulter plusieurs profils vérifiés, comparer les enseignants et choisir librement celui qui leur inspire le plus confiance.</p>

<h2>Une nouvelle façon de trouver un professeur</h2>
<p>Trouver un bon répétiteur n'est pas toujours simple.</p>
<p>Beaucoup de parents doivent demander autour d'eux, attendre une recommandation ou accepter le premier professeur disponible sans réellement connaître son parcours.</p>
<p>Prof Chez Vous a été créé pour rendre cette recherche plus simple, plus transparente et plus rassurante.</p>
<p>Chaque professeur dispose d'un profil détaillé présentant notamment :</p>
<ul>
    <li>les matières enseignées ;</li>
    <li>les classes prises en charge ;</li>
    <li>les zones d'intervention ;</li>
    <li>son expérience ;</li>
    <li>sa présentation ;</li>
    <li>ses disponibilités.</li>
</ul>
<p>Le parent peut ainsi comparer plusieurs profils avant de faire son choix.</p>
<p>(Le fonctionnement détaillé de cette recherche est expliqué dans l'article {lp("comment-trouver-un-professeur", "Comment trouver un professeur ?")}.)</p>

<h2>Des professeurs vérifiés avant d'être visibles</h2>
<p>L'un des principes fondamentaux de Prof Chez Vous est la {lp("pourquoi-les-professeurs-sont-ils-verifies", "vérification des profils")}.</p>
<p>Avant qu'un professeur puisse apparaître dans les résultats de recherche, son dossier est examiné par l'équipe de vérification.</p>
<p>Cette étape permet de contrôler les informations fournies ainsi que les justificatifs demandés.</p>
<p>L'objectif est d'offrir aux parents un environnement plus fiable pour rechercher un professeur.</p>
<p>(Pour comprendre cette procédure, consultez l'article {lp("pourquoi-les-professeurs-sont-ils-verifies", "Pourquoi les professeurs sont-ils vérifiés ?")}.)</p>

<h2>Le choix appartient toujours au parent</h2>
<p>Prof Chez Vous ne désigne pas un professeur à votre place.</p>
<p>La plateforme met à votre disposition plusieurs profils afin que vous puissiez comparer les enseignants selon vos propres critères.</p>
<p>Vous êtes libre de consulter les profils, d'examiner leurs informations et de sélectionner le professeur qui correspond le mieux aux besoins de votre enfant.</p>
<p>Cette liberté de choix constitue l'un des fondements de la plateforme.</p>
<p>(Découvrez également {lp("comment-choisir-le-bon-professeur", "Comment choisir le bon professeur ?")}.)</p>

<h2>Une première rencontre avant tout engagement</h2>
<p>Choisir un professeur est une décision importante.</p>
<p>C'est pourquoi Prof Chez Vous prévoit une première {lp("comment-fonctionne-la-seance-dessai", "séance d'essai")} permettant au parent, à l'apprenant et au professeur de faire connaissance avant de poursuivre leur collaboration.</p>
<p>Cette rencontre permet à chacun d'évaluer si les attentes sont réunies avant de commencer un accompagnement régulier.</p>
<p>(Voir {lp("comment-fonctionne-la-seance-dessai", "Comment fonctionne la séance d'essai ?")}.)</p>

<h2>À qui s'adresse Prof Chez Vous ?</h2>
<p>La plateforme est destinée :</p>
<ul>
    <li>aux parents recherchant un professeur particulier pour leurs enfants ;</li>
    <li>aux apprenants souhaitant bénéficier d'un accompagnement personnalisé ;</li>
    <li>aux professeurs souhaitant proposer leurs compétences dans un cadre professionnel.</li>
</ul>

<h2>Notre objectif</h2>
<p>Prof Chez Vous souhaite rendre la recherche d'un professeur plus simple, plus transparente et plus professionnelle.</p>
<p>En permettant aux parents de choisir librement parmi des {lp("pourquoi-les-professeurs-sont-ils-verifies", "profils vérifiés")}, la plateforme favorise une relation de confiance entre les familles et les enseignants.</p>

<h2>En résumé</h2>
<p>Prof Chez Vous est une plateforme qui permet :</p>
<ul>
    <li>✓ de rechercher facilement un professeur particulier ;</li>
    <li>✓ de consulter plusieurs profils vérifiés ;</li>
    <li>✓ de comparer les enseignants avant de choisir ;</li>
    <li>✓ de bénéficier d'une première séance d'essai avant tout engagement.</li>
</ul>
"""
        },
        {
            "category": cat_parents,
            "title": "Comment trouver un professeur ?",
            "slug": "comment-trouver-un-professeur",
            "keywords": "recherche, trouver, parcours, chercher, filtrer, localisation, profils, comparer, recommandations, espace personnel",
            "order": 2,
            "content": f"""
<h2>Réponse rapide</h2>
<p>Trouver un professeur sur Prof Chez Vous est simple et entièrement guidé.</p>
<p>Vous pouvez consulter librement les profils des professeurs partenaires vérifiés, comparer leurs informations et choisir celui qui correspond le mieux à vos besoins. La plateforme vous accompagne tout au long de votre recherche, tout en vous laissant libre de votre décision.</p>

<h2>Une recherche simple et organisée</h2>
<p>Prof Chez Vous a été conçu pour rendre la recherche d'un professeur plus simple, plus transparente et plus rassurante.</p>
<p>Que vous soyez un parent à la recherche d'un accompagnement pour votre enfant ou un apprenant souhaitant bénéficier de cours particuliers, la plateforme met à votre disposition des outils qui vous permettent d'identifier rapidement les professeurs correspondant à vos besoins.</p>

<h2>Étape 1 : Accéder aux professeurs</h2>
<p>Il existe deux façons d'accéder aux profils des professeurs sur Prof Chez Vous.</p>

<h3>Si vous n'êtes pas encore connecté</h3>
<p>Vous pouvez consulter librement la page de recherche des professeurs. Vous y trouverez l'ensemble des professeurs partenaires actuellement vérifiés.</p>
<p>Aucune inscription n'est nécessaire pour parcourir les profils.</p>

<h3>Si vous êtes déjà connecté</h3>
<p>Votre espace personnel facilite encore davantage votre recherche.</p>
<p>En fonction des informations renseignées pour votre enfant ou pour vous-même (classe, matière, zone géographique, etc.), Prof Chez Vous peut vous proposer directement des professeurs correspondant à vos besoins.</p>
<p>Vous pouvez consulter leurs profils depuis ces recommandations ou accéder à tout moment à la page complète de recherche afin d'explorer davantage de possibilités.</p>
<p>Dans les deux cas, vous restez libre de consulter autant de profils que vous le souhaitez avant de faire votre choix.</p>

<h2>Étape 2 : Affiner votre recherche</h2>
<p>Pour gagner du temps, utilisez les filtres proposés par la plateforme.</p>
<p>Selon votre besoin, vous pouvez notamment rechercher un professeur par :</p>
<ul>
    <li>matière ;</li>
    <li>classe ou niveau ;</li>
    <li>zone d'intervention ;</li>
    <li>ou tout autre critère disponible.</li>
</ul>
<p>Ces filtres permettent d'afficher uniquement les professeurs correspondant à votre recherche.</p>

<h2>Étape 3 : Comparer les profils</h2>
<p>Chaque professeur partenaire possède une fiche détaillée.</p>
<p>Vous pouvez notamment y consulter :</p>
<ul>
    <li>sa présentation ;</li>
    <li>les matières qu'il enseigne ;</li>
    <li>les classes qu'il accompagne ;</li>
    <li>son expérience ;</li>
    <li>ses diplômes ou qualifications validés ;</li>
    <li>sa zone d'intervention ;</li>
    <li>ses disponibilités.</li>
</ul>
<p>Prenez le temps de comparer plusieurs profils.</p>
<p>Chaque enseignant possède sa propre expérience, sa méthode de travail et ses domaines de compétence.</p>
<p>Pour savoir quels éléments observer avant de faire votre choix, consultez également l'article {lp("comment-choisir-le-bon-professeur", "Comment choisir le bon professeur ?")}.</p>

<h2>Étape 4 : Choisir le professeur qui vous convient</h2>
<p>Une fois votre comparaison effectuée, vous pouvez sélectionner le professeur qui répond le mieux à vos attentes.</p>
<p>Prof Chez Vous ne désigne jamais un professeur à votre place.</p>
<p>La décision finale vous appartient toujours.</p>
<p>Vous choisissez selon les critères qui sont importants pour vous : expérience, présentation, proximité, matières enseignées, disponibilités ou tout autre élément qui vous inspire confiance.</p>

<h2>Étape 5 : Créer votre espace personnel</h2>
<p>La consultation des profils est libre.</p>
<p>En revanche, lorsque vous souhaitez programmer une première séance avec un professeur, vous devez disposer d'un espace personnel.</p>
<p>Cet espace vous permet notamment :</p>
<ul>
    <li>d'enregistrer vos informations ;</li>
    <li>d'ajouter votre ou vos enfants si vous êtes parent ;</li>
    <li>de gérer vos demandes ;</li>
    <li>de retrouver facilement vos professeurs ;</li>
    <li>de suivre vos échanges sur la plateforme.</li>
</ul>
<p>La création du compte est rapide et ne prend que quelques minutes.</p>

<h2>Étape 6 : Programmer une première séance d'essai</h2>
<p>Une fois votre compte créé et votre professeur choisi, vous pouvez programmer une première {lp("comment-fonctionne-la-seance-dessai", "séance d'essai")}.</p>
<p>Cette première rencontre permet :</p>
<ul>
    <li>au professeur ;</li>
    <li>au parent ou à l'apprenant ;</li>
    <li>et, le cas échéant, à l'enfant concerné,</li>
</ul>
<p>de faire connaissance et de vérifier que les attentes de chacun sont bien comprises avant de commencer un accompagnement régulier.</p>
<p>Le déroulement complet de cette étape est présenté dans l'article {lp("comment-fonctionne-la-seance-dessai", "Comment fonctionne la séance d'essai ?")}.</p>

<h2>Une plateforme qui vous guide sans choisir à votre place</h2>
<p>Chez Prof Chez Vous, nous pensons que choisir un professeur est une décision importante.</p>
<p>C'est pourquoi la plateforme ne vous impose jamais un enseignant.</p>
<p>En revanche, elle met à votre disposition un environnement organisé pour faciliter votre décision :</p>
<ul>
    <li>des recommandations adaptées à votre profil lorsque vous êtes connecté ;</li>
    <li>des filtres pour affiner votre recherche ;</li>
    <li>des profils détaillés ;</li>
    <li>des informations {lp("pourquoi-les-professeurs-sont-ils-verifies", "vérifiées")} ;</li>
    <li>une présentation claire de chaque professeur.</li>
</ul>
<p>Vous bénéficiez ainsi d'un accompagnement structuré qui vous aide à identifier les professeurs les plus pertinents, tout en conservant une liberté totale dans votre décision.</p>
<p>Notre rôle est de vous guider. Le choix vous appartient toujours.</p>

<h2>Si vous ne trouvez pas immédiatement le professeur recherché</h2>
<p>Prof Chez Vous continue d'accueillir régulièrement de nouveaux professeurs partenaires.</p>
<p>Si aucun profil ne correspond encore à votre besoin, n'hésitez pas à contacter notre équipe.</p>
<p>Nous pourrons vous accompagner dans votre recherche et vous informer lorsqu'un professeur répondant à vos critères rejoint la plateforme.</p>

<h2>En résumé</h2>
<p>Trouver un professeur sur Prof Chez Vous consiste à :</p>
<ul>
    <li>✓ consulter librement les profils des professeurs partenaires ;</li>
    <li>✓ utiliser les filtres ou les recommandations proposées par la plateforme ;</li>
    <li>✓ comparer plusieurs profils vérifiés ;</li>
    <li>✓ choisir librement le professeur qui vous convient ;</li>
    <li>✓ créer votre espace personnel au moment de programmer une première séance ;</li>
    <li>✓ organiser une {lp("comment-fonctionne-la-seance-dessai", "séance d'essai")} avant tout engagement.</li>
</ul>
"""
        },
        {
            "category": cat_parents,
            "title": "Comment choisir le bon professeur ?",
            "slug": "comment-choisir-le-bon-professeur",
            "keywords": "choix, comparer, meilleur, profil, decision, criteres, experience, matieres, localisation",
            "order": 3,
            "content": f"""
<h2>Réponse rapide</h2>
<p>Le bon professeur n'est pas forcément celui qui possède le plus de diplômes ou le plus d'années d'expérience.</p>
<p>C'est avant tout celui dont les compétences, la méthode de travail et la personnalité correspondent aux besoins de l'apprenant.</p>
<p>Prof Chez Vous vous fournit les informations nécessaires pour comparer plusieurs profils et faire un choix éclairé.</p>

<h2>Il n'existe pas un professeur idéal pour tout le monde</h2>
<p>Chaque apprenant est différent.</p>
<p>Certains ont besoin d'un professeur très pédagogue.</p>
<p>D'autres recherchent davantage de rigueur.</p>
<p>Certains souhaitent préparer un examen précis.</p>
<p>D'autres veulent simplement renforcer leurs bases.</p>
<p>Le meilleur professeur est donc celui qui répond à votre besoin particulier.</p>
<p>C'est pourquoi Prof Chez Vous vous laisse toujours libre de comparer plusieurs profils avant de prendre votre décision.</p>

<h2>Commencez par définir votre besoin</h2>
<p>Avant de consulter les profils, posez-vous quelques questions simples.</p>
<p>Par exemple :</p>
<ul>
    <li>Quelle matière souhaitez-vous renforcer ?</li>
    <li>Quel est le niveau de l'apprenant ?</li>
    <li>S'agit-il d'un accompagnement ponctuel ou régulier ?</li>
    <li>Quels sont les objectifs recherchés ?</li>
    <li>Existe-t-il des contraintes de localisation ou de disponibilité ?</li>
</ul>
<p>Plus votre besoin est clair, plus votre choix sera facile.</p>

<h2>Lisez attentivement la présentation du professeur</h2>
<p>Chaque professeur dispose d'une présentation personnelle.</p>
<p>Prenez le temps de la lire.</p>
<p>Elle vous permet souvent de comprendre :</p>
<ul>
    <li>sa manière d'enseigner ;</li>
    <li>son expérience ;</li>
    <li>sa vision de l'accompagnement ;</li>
    <li>le public avec lequel il est le plus à l'aise.</li>
</ul>
<p>Cette présentation complète les informations techniques affichées sur son profil.</p>

<h2>Vérifiez que le professeur correspond au niveau recherché</h2>
<p>Tous les professeurs n'enseignent pas les mêmes classes.</p>
<p>Consultez les niveaux pris en charge afin de vérifier qu'ils correspondent bien aux besoins de l'apprenant.</p>
<p>Même lorsqu'un professeur intervient sur plusieurs classes, son expérience peut être particulièrement importante sur certains niveaux.</p>
<p>Les informations présentes sur son profil vous aideront à apprécier cette expérience.</p>

<h2>Vérifiez les matières proposées</h2>
<p>Assurez-vous que le professeur enseigne bien la ou les matières recherchées.</p>
<p>Chaque matière affichée sur la plateforme est associée aux compétences déclarées par le professeur et examinées lors de la vérification de son dossier.</p>

<h2>Prenez en compte son expérience</h2>
<p>L'expérience permet souvent d'apprécier la diversité des situations déjà rencontrées par un professeur.</p>
<p>Selon les profils, vous pourrez retrouver :</p>
<ul>
    <li>les établissements dans lesquels il a exercé ;</li>
    <li>son ancienneté ;</li>
    <li>son parcours professionnel ;</li>
    <li>ou d'autres informations utiles.</li>
</ul>
<p>L'expérience est un élément important, mais elle ne doit pas être le seul critère de décision.</p>

<h2>Vérifiez sa zone d'intervention</h2>
<p>Si les cours se déroulent en présentiel, assurez-vous que le professeur intervient bien dans votre secteur.</p>
<p>Cela facilitera l'organisation des séances.</p>

<h2>Consultez ses disponibilités</h2>
<p>Les disponibilités indiquent les périodes pendant lesquelles le professeur peut généralement assurer des cours.</p>
<p>Vérifiez qu'elles sont compatibles avec votre propre organisation.</p>
<p>Ces informations peuvent évoluer au cours de l'année scolaire.</p>

<h2>La vérification apporte une sécurité supplémentaire</h2>
<p>Avant d'être rendu visible sur la plateforme, chaque professeur partenaire passe par une procédure de vérification.</p>
<p>Cette étape permet de contrôler les informations et les justificatifs demandés.</p>
<p>Elle constitue un élément supplémentaire pour vous aider à choisir en toute confiance.</p>
<p>Pour en savoir davantage, consultez l'article {lp("pourquoi-les-professeurs-sont-ils-verifies", "Pourquoi les professeurs sont-ils vérifiés ?")}</p>

<h2>La séance d'essai fait partie du choix</h2>
<p>Même après avoir comparé plusieurs profils, il est parfois difficile de savoir si un professeur conviendra parfaitement.</p>
<p>C'est précisément le rôle de la séance d'essai.</p>
<p>Cette première rencontre permet :</p>
<ul>
    <li>de faire connaissance ;</li>
    <li>d'échanger sur les attentes ;</li>
    <li>d'observer la manière dont le professeur communique ;</li>
    <li>d'évaluer si une collaboration durable est envisageable.</li>
</ul>
<p>La séance d'essai constitue donc une étape importante dans votre prise de décision.</p>
<p>Son déroulement est présenté dans l'article {lp("comment-fonctionne-la-seance-dessai", "Comment fonctionne la séance d'essai ?")}</p>

<h2>Prenez le temps de comparer</h2>
<p>Il n'est pas nécessaire de choisir le premier profil consulté.</p>
<p>Comparer plusieurs professeurs vous permettra de mieux apprécier les différences entre leurs parcours, leurs compétences et leur présentation.</p>
<p>Quelques minutes supplémentaires peuvent vous aider à faire un choix plus serein.</p>

<h2>En résumé</h2>
<p>Pour choisir le bon professeur :</p>
<ul>
    <li>✓ définissez clairement votre besoin ;</li>
    <li>✓ comparez plusieurs profils ;</li>
    <li>✓ consultez attentivement les présentations ;</li>
    <li>✓ vérifiez les matières, les classes et la zone d'intervention ;</li>
    <li>✓ tenez compte de l'expérience et des disponibilités ;</li>
    <li>✓ profitez de la {lp("comment-fonctionne-la-seance-dessai", "séance d'essai")} pour confirmer votre choix.</li>
</ul>

<div style="background-color: var(--hc-primary-light); padding: 1.5rem; border-radius: 8px; margin-top: 2rem; border-left: 4px solid var(--hc-primary);">
    <p style="margin: 0; font-weight: 500;"><strong>À retenir :</strong> Un bon professeur n'est pas seulement celui qui maîtrise une matière. C'est aussi une personne avec laquelle l'apprenant se sent écouté, compris et encouragé à progresser. C'est pourquoi Prof Chez Vous prévoit une première {lp("comment-fonctionne-la-seance-dessai", "séance d'essai")} avant tout engagement régulier.</p>
</div>
"""
        },
        {
            "category": cat_parents,
            "title": "Pourquoi les professeurs sont-ils vérifiés ?",
            "slug": "pourquoi-les-professeurs-sont-ils-verifies",
            "keywords": "verification, confiance, securite, diplomes, identite, badge, certifie, controle, procedure",
            "order": 4,
            "content": f"""
<h2>Réponse rapide</h2>
<p>Avant d'apparaître publiquement sur Prof Chez Vous, chaque professeur partenaire passe par une procédure de vérification.</p>
<p>Cette vérification permet de contrôler son identité ainsi que les informations et les justificatifs nécessaires à l'étude de son dossier.</p>
<p>L'objectif est d'offrir aux parents et aux apprenants un environnement plus fiable pour rechercher un professeur.</p>

<h2>Pourquoi cette vérification est-elle nécessaire ?</h2>
<p>Choisir un professeur est une décision importante.</p>
<p>Les parents comme les apprenants souhaitent naturellement savoir à qui ils confient leur apprentissage.</p>
<p>Prof Chez Vous a donc mis en place une procédure de vérification afin que chaque profil visible sur la plateforme fasse l'objet d'un examen préalable.</p>
<p>Cette démarche contribue à instaurer un climat de confiance avant même la première prise de contact.</p>

<h2>Que vérifie Prof Chez Vous ?</h2>
<p>Avant qu'un professeur puisse être rendu visible, notre équipe examine notamment :</p>
<ul>
    <li>son identité ;</li>
    <li>les informations renseignées sur son profil ;</li>
    <li>les diplômes ou autres justificatifs présentés ;</li>
    <li>les documents complémentaires lorsque cela est nécessaire pour apprécier certaines compétences ou expériences.</li>
</ul>
<p>Chaque dossier est étudié individuellement.</p>
<p>Selon le profil du professeur, des informations complémentaires peuvent être demandées avant toute validation.</p>

<h2>Une qualification peut être démontrée de différentes façons</h2>
<p>Toutes les compétences ne s'acquièrent pas uniquement par un diplôme portant exactement le nom de la matière enseignée.</p>
<p>Dans certains cas, un professeur peut justifier ses compétences grâce :</p>
<ul>
    <li>à un diplôme compatible avec la discipline concernée ;</li>
    <li>à une formation pertinente ;</li>
    <li>à une expérience professionnelle significative ;</li>
    <li>ou à des justificatifs complémentaires permettant d'apprécier son parcours.</li>
</ul>
<p>Chaque situation est étudiée individuellement par l'équipe de vérification.</p>
<p>Cette approche permet d'évaluer les candidatures avec équité tout en maintenant un niveau d'exigence élevé.</p>

<h2>Tous les dossiers ne sont pas validés automatiquement</h2>
<p>Le dépôt d'un dossier ne garantit pas sa validation.</p>
<p>Chaque candidature est examinée avant toute publication.</p>
<p>Si certains éléments sont insuffisants ou nécessitent des précisions, le professeur peut être invité à compléter son dossier avant qu'une décision définitive ne soit prise.</p>
<p>Cette procédure contribue à préserver la qualité des profils proposés sur la plateforme.</p>

<h2>Que signifie un profil vérifié ?</h2>
<p>Lorsqu'un professeur est indiqué comme vérifié sur Prof Chez Vous, cela signifie que son dossier a satisfait à la procédure de vérification mise en place par la plateforme.</p>
<p>Autrement dit, son identité et les éléments nécessaires à l'étude de sa candidature ont été examinés avant la publication de son profil.</p>
<p>Cette vérification constitue un niveau supplémentaire de confiance dans votre recherche.</p>

<h2>Ce que la vérification ne signifie pas</h2>
<p>La vérification ne signifie pas que Prof Chez Vous classe les professeurs entre eux ou garantit qu'un enseignant conviendra à tous les apprenants.</p>
<p>Chaque professeur possède sa propre personnalité, sa méthode de travail et son expérience.</p>
<p>C'est pourquoi la plateforme vous laisse toujours libre de comparer plusieurs profils et de choisir celui qui correspond le mieux à vos attentes.</p>
<p>La {lp("comment-fonctionne-la-seance-dessai", "séance d'essai")} permet ensuite de confirmer que ce choix répond bien à vos besoins.</p>

<h2>Pourquoi conserver une liberté de choix ?</h2>
<p>Même après une vérification, plusieurs professeurs peuvent parfaitement répondre à votre recherche.</p>
<p>Prof Chez Vous préfère donc vous fournir toutes les informations utiles afin que vous puissiez comparer les profils et prendre une décision éclairée.</p>
<p>Notre rôle est de créer un cadre de confiance.</p>
<p>Votre rôle est de choisir le professeur qui vous semble le plus adapté.</p>

<h2>Une confiance qui se construit à plusieurs</h2>
<p>La qualité d'une relation pédagogique repose sur plusieurs éléments :</p>
<ul>
    <li>les compétences du professeur ;</li>
    <li>les attentes du parent ou de l'apprenant ;</li>
    <li>une bonne communication ;</li>
    <li>des objectifs clairement définis.</li>
</ul>
<p>La vérification constitue la première étape de cette relation de confiance.</p>
<p>La {lp("comment-fonctionne-la-seance-dessai", "séance d'essai")} permet ensuite de confirmer que chacun souhaite poursuivre l'accompagnement dans de bonnes conditions.</p>

<h2>En résumé</h2>
<p>La vérification permet de :</p>
<ul>
    <li>✓ contrôler l'identité du professeur ;</li>
    <li>✓ examiner les informations et justificatifs de son dossier ;</li>
    <li>✓ évaluer ses compétences à partir de son parcours et des documents fournis ;</li>
    <li>✓ publier uniquement les profils ayant satisfait à la procédure de vérification.</li>
</ul>
<p>Elle ne remplace toutefois ni votre propre appréciation, ni la première {lp("comment-fonctionne-la-seance-dessai", "séance d'essai")}, qui restent essentielles pour choisir le professeur le plus adapté à vos besoins.</p>
"""
        },
        {
            "category": cat_parents,
            "title": "Comment fonctionne la séance d'essai ?",
            "slug": "comment-fonctionne-la-seance-dessai",
            "keywords": "essai, gratuit, premier cours, rencontre, test, seance, faire connaissance",
            "order": 5,
            "content": f"""
<h2>Réponse rapide</h2>
<p>La séance d'essai est une première rencontre organisée entre le professeur, le parent ou l'apprenant.</p>
<p>Elle permet à chacun de faire connaissance, de préciser les besoins, de découvrir la manière de travailler du professeur et de vérifier si une collaboration durable est envisageable.</p>
<p>À son issue, chacun reste entièrement libre de poursuivre ou non l'accompagnement.</p>

<h2>Pourquoi une séance d'essai ?</h2>
<p>Choisir un professeur est une décision importante.</p>
<p>Même après avoir consulté un profil détaillé, il est difficile de savoir si une collaboration conviendra réellement.</p>
<p>La séance d'essai permet donc de transformer un choix effectué sur un écran en une véritable rencontre.</p>
<p>Elle aide le professeur, le parent et l'apprenant à confirmer que leurs attentes sont compatibles avant tout engagement régulier.</p>

<h2>Quel est l'objectif de cette première séance ?</h2>
<p>La séance d'essai ne sert pas uniquement à dispenser un premier cours.</p>
<p>Elle permet notamment :</p>
<ul>
    <li>de faire connaissance ;</li>
    <li>de comprendre les besoins de l'apprenant ;</li>
    <li>de discuter des objectifs à atteindre ;</li>
    <li>de découvrir la méthode de travail du professeur ;</li>
    <li>de répondre aux premières questions ;</li>
    <li>d'établir un premier climat de confiance.</li>
</ul>
<p>Cette première rencontre pose les bases d'une éventuelle collaboration.</p>

<h2>Comment une séance d'essai est-elle organisée ?</h2>
<p>Une fois votre professeur choisi, vous pouvez demander une séance d'essai depuis votre espace personnel.</p>
<p>Après confirmation, la date, l'heure et les modalités de la rencontre sont convenues entre les différentes parties.</p>
<p>Selon la situation, cette séance peut être organisée dans le respect des modalités prévues par la plateforme.</p>

<h2>Que se passe-t-il pendant la séance ?</h2>
<p>Chaque professeur possède sa propre façon d'enseigner.</p>
<p>En fonction des besoins de l'apprenant, la séance peut notamment comprendre :</p>
<ul>
    <li>une prise de contact ;</li>
    <li>des échanges avec le parent ou l'apprenant ;</li>
    <li>une évaluation du niveau si cela est nécessaire ;</li>
    <li>une présentation de la méthode de travail ;</li>
    <li>un premier accompagnement pédagogique.</li>
</ul>
<p>Il n'existe pas de déroulement unique.</p>
<p>L'objectif est avant tout de permettre à chacun de mieux se connaître.</p>

<h2>Comment savoir si le professeur vous convient ?</h2>
<p>À l'issue de cette première rencontre, posez-vous quelques questions simples.</p>
<p>Par exemple :</p>
<ul>
    <li>Le professeur a-t-il bien compris les besoins de l'apprenant ?</li>
    <li>Sa manière d'expliquer est-elle adaptée ?</li>
    <li>Le dialogue s'est-il installé facilement ?</li>
    <li>Vous sentez-vous en confiance ?</li>
    <li>Pensez-vous qu'il pourra accompagner efficacement l'apprenant dans la durée ?</li>
</ul>
<p>Ces éléments sont souvent aussi importants que les diplômes ou les années d'expérience.</p>

<h2>Êtes-vous obligé de poursuivre ?</h2>
<p>Non.</p>
<p>La séance d'essai n'entraîne aucun engagement automatique.</p>
<p>Elle est précisément prévue pour permettre à chacun d'évaluer sereinement si une collaboration est souhaitable.</p>
<p>Si le professeur, le parent ou l'apprenant estime que cette collaboration ne correspond pas à ses attentes, chacun reste libre de ne pas poursuivre.</p>
<p>Dans le cas contraire, l'accompagnement peut débuter dans les conditions convenues entre les deux parties.</p>

<h2>Pourquoi Prof Chez Vous a-t-il choisi cette approche ?</h2>
<p>Chez Prof Chez Vous, nous pensons qu'une relation pédagogique durable repose autant sur les compétences que sur la confiance.</p>
<p>Une fiche de présentation permet de découvrir un professeur.</p>
<p>Une séance d'essai permet de le rencontrer.</p>
<p>C'est cette rencontre qui aide le plus souvent à prendre une décision éclairée.</p>
<p>Notre objectif n'est pas simplement de mettre en relation des personnes, mais de favoriser des collaborations solides et durables.</p>

<h2>Quelques conseils avant votre séance</h2>
<p>Pour profiter pleinement de cette première rencontre, il est conseillé de :</p>
<ul>
    <li>réfléchir aux difficultés rencontrées ;</li>
    <li>définir les objectifs recherchés ;</li>
    <li>préparer les questions que vous souhaitez poser ;</li>
    <li>permettre au professeur de bien comprendre votre situation.</li>
</ul>
<p>Une bonne préparation facilite les échanges et permet au professeur de proposer un accompagnement plus adapté.</p>

<h2>En résumé</h2>
<p>La séance d'essai permet :</p>
<ul>
    <li>✓ de rencontrer le professeur avant tout engagement ;</li>
    <li>✓ de présenter les besoins et les objectifs de l'apprenant ;</li>
    <li>✓ de découvrir la méthode de travail du professeur ;</li>
    <li>✓ d'instaurer un climat de confiance ;</li>
    <li>✓ de décider librement si l'accompagnement doit se poursuivre.</li>
</ul>
"""
        },
        {
            "category": cat_parents,
            "title": "Comment se déroule un accompagnement avec un professeur ?",
            "slug": "comment-se-deroule-un-engagement",
            "keywords": "accompagnement, engagement, suivi, cours, journal de séance, modalités, horaires, fin, changer, plans",
            "order": 6,
            "content": f"""
<h2>Réponse rapide</h2>
<p>Si la {lp("comment-fonctionne-la-seance-dessai", "séance d'essai")} est concluante, le parent ou l'apprenant et le professeur peuvent décider de poursuivre leur collaboration.</p>
<p>Ils conviennent alors ensemble des modalités de l'accompagnement (fréquence, horaires, lieu des cours, objectifs, etc.), tandis que Prof Chez Vous reste la plateforme qui facilite cette mise en relation et accompagne ses utilisateurs tout au long de leur parcours.</p>

<h2>L'accompagnement commence après une décision commune</h2>
<p>La séance d'essai permet à chacun de découvrir l'autre.</p>
<p>Si le professeur, le parent ou l'apprenant estime que la collaboration est adaptée, ils peuvent décider ensemble de poursuivre l'accompagnement.</p>
<p>Cette décision est toujours prise d'un commun accord.</p>
<p>Prof Chez Vous n'impose jamais le début d'un accompagnement.</p>

<h2>Les modalités sont définies ensemble</h2>
<p>Une fois la décision prise, le professeur et le parent ou l'apprenant définissent ensemble l'organisation des cours.</p>
<p>Ils conviennent notamment :</p>
<ul>
    <li>des jours de cours ;</li>
    <li>des horaires ;</li>
    <li>de la fréquence des séances ;</li>
    <li>du lieu où elles se dérouleront ;</li>
    <li>des objectifs pédagogiques à atteindre.</li>
</ul>
<p>Chaque accompagnement est donc adapté aux besoins spécifiques de l'apprenant.</p>

<h2>Un accompagnement qui évolue avec les besoins</h2>
<p>Les besoins d'un apprenant évoluent naturellement au cours de l'année.</p>
<p>Selon les progrès réalisés ou les nouveaux objectifs fixés, le professeur et le parent ou l'apprenant peuvent décider ensemble :</p>
<ul>
    <li>d'augmenter ou de réduire la fréquence des séances ;</li>
    <li>de renforcer certaines notions ;</li>
    <li>de préparer un examen ou un concours ;</li>
    <li>d'adapter les objectifs pédagogiques.</li>
</ul>
<p>Cette souplesse permet d'offrir un accompagnement réellement personnalisé.</p>

<h2>Le rôle de Prof Chez Vous pendant l'accompagnement</h2>
<p>Même après le début des cours, Prof Chez Vous continue d'assurer son rôle de plateforme.</p>
<p>Notre équipe reste disponible pour :</p>
<ul>
    <li>répondre aux questions liées au fonctionnement de la plateforme ;</li>
    <li>accompagner les utilisateurs en cas de difficulté ;</li>
    <li>faciliter certaines démarches lorsque cela est nécessaire ;</li>
    <li>contribuer au bon déroulement de chaque accompagnement.</li>
</ul>
<p>Notre objectif est de proposer un cadre organisé et sécurisé, afin que chacun puisse se concentrer sur l'essentiel : la réussite de l'apprenant.</p>

<h2>Une relation fondée sur la confiance</h2>
<p>La réussite d'un accompagnement repose autant sur la qualité du professeur que sur une communication régulière entre les différentes parties.</p>
<p>Pour faciliter ce suivi, Prof Chez Vous met à disposition un <strong>journal de séance</strong> que le professeur complète après chaque cours.</p>
<p>Ce journal permet notamment de renseigner :</p>
<ul>
    <li>les notions abordées ;</li>
    <li>les objectifs travaillés ;</li>
    <li>les difficultés rencontrées ;</li>
    <li>les progrès observés ;</li>
    <li>les recommandations pour les prochaines séances.</li>
</ul>
<p>Le parent ou l'apprenant peut ainsi suivre l'évolution de l'accompagnement presque en temps réel, sans devoir attendre plusieurs semaines pour faire le point.</p>
<p>Cet outil renforce la transparence, facilite les échanges et permet à chacun de suivre la progression de l'apprenant tout au long de son parcours.</p>

<h2>Peut-on mettre fin à un accompagnement ?</h2>
<p>Oui.</p>
<p>Le parent ou l'apprenant comme le professeur restent libres de mettre fin à leur collaboration si celle-ci ne répond plus à leurs attentes.</p>
<p>Toutefois, avant toute rupture, les deux parties doivent respecter les engagements prévus dans le contrat conclu au début de l'accompagnement, notamment en ce qui concerne le règlement des éventuelles obligations financières restant dues.</p>
<p>Cette règle permet de garantir une séparation claire, équitable et respectueuse des engagements pris par chacun.</p>
<p>En cas de besoin, Prof Chez Vous peut accompagner les utilisateurs afin que cette transition se déroule dans les meilleures conditions.</p>

<h2>Peut-on choisir un autre professeur ?</h2>
<p>Oui.</p>
<p>Si vos besoins évoluent ou si vous souhaitez poursuivre votre accompagnement avec un autre enseignant, vous pouvez effectuer une nouvelle recherche et sélectionner un autre professeur partenaire.</p>
<p>Toutefois, les possibilités de remplacement dépendent du plan associé à votre compte.</p>
<p>Dans le <strong>plan Standard</strong>, proposé actuellement dans le cadre de notre offre de lancement, chaque parent ou apprenant bénéficie <strong>d'une seule séance d'essai offerte à vie</strong> sur la plateforme.</p>
<p>Si vous souhaitez rencontrer un autre professeur avant de vous engager, cette possibilité est ensuite déterminée par les avantages prévus dans votre plan.</p>
<p>Les plans offrant davantage de liberté permettent notamment de réaliser plusieurs essais ou remplacements, dans les limites qui leur sont propres.</p>
<p>Il est important de préciser que ces plans ne facturent pas les séances d'essai elles-mêmes. Ils donnent accès à des avantages supplémentaires tels qu'une plus grande liberté dans le choix des professeurs, un nombre d'essais adapté au plan souscrit ainsi que l'accès aux outils de suivi et aux fonctionnalités qui accompagnent votre parcours sur Prof Chez Vous.</p>

<h2>Nos conseils pour une collaboration réussie</h2>
<p>Quelques bonnes pratiques permettent généralement d'obtenir les meilleurs résultats :</p>
<ul>
    <li>définir des objectifs clairs dès le départ ;</li>
    <li>respecter les horaires convenus ;</li>
    <li>consulter régulièrement le journal de séance ;</li>
    <li>échanger avec le professeur sur les progrès et les difficultés rencontrées ;
    <li>signaler rapidement tout changement important.</li>
</ul>
<p>Une collaboration bien organisée favorise les progrès de l'apprenant et permet au professeur d'adapter son accompagnement au fil du temps.</p>

<h2>En résumé</h2>
<p>Après une {lp("comment-fonctionne-la-seance-dessai", "séance d'essai")} concluante :</p>
<ul>
    <li>✓ le professeur et le parent ou l'apprenant décident ensemble de poursuivre l'accompagnement ;</li>
    <li>✓ les modalités des cours sont définies d'un commun accord ;</li>
    <li>✓ le suivi de la progression est assuré grâce au journal de séance ;</li>
    <li>✓ Prof Chez Vous reste disponible pour accompagner les utilisateurs dans l'utilisation de la plateforme ;</li>
    <li>✓ toute fin d'accompagnement doit respecter les engagements prévus au contrat ;</li>
    <li>✓ les possibilités de changement de professeur dépendent du plan associé à votre compte.</li>
</ul>
"""
        },
        {
            "category": cat_parents,
            "title": "Que faire si je ne suis pas satisfait ?",
            "slug": "que-faire-si-je-ne-suis-pas-satisfait",
            "keywords": "insatisfait, probleme, changer, conflit, litige, signalement",
            "order": 7,
            "content": f"""
<h2>Vous restez toujours aux commandes</h2>
<p>L'accompagnement scolaire doit etre une solution, pas un probleme. Si la prestation d'un professeur ne vous convient plus, vous avez tous les droits.</p>

<h3>Comment reagir ?</h3>
<ul>
    <li><strong>Communiquez d'abord :</strong> Souvent, un simple echange avec le professeur permet de reajuster la methode de travail.</li>
    <li><strong>Mettez fin a l'engagement :</strong> Vous n'etes lie par aucun contrat a long terme. Vous pouvez stopper les cours a tout moment (en reglant uniquement les cours deja effectues).</li>
    <li><strong>Signalez a la plateforme :</strong> Si le professeur a eu un comportement inapproprie ou non professionnel, vous pouvez le signaler a notre equipe de support. Nous prendrons des mesures immediates, pouvant aller jusqu'a l'exclusion du professeur.</li>
</ul>

<h2>Trouver un autre professeur</h2>
<p>N'hesitez jamais a chercher un autre professeur sur la plateforme si le premier ne convient pas ! {lp("comment-trouver-un-professeur", "Relancez une recherche")} et profitez a nouveau d'une {lp("comment-fonctionne-la-seance-dessai", "seance d'essai gratuite")} avec le nouveau professeur.</p>
<p>{la("comment-protegeons-nous-les-parents", "Decouvrez comment nous protegeoons les parents et les apprenants")}.</p>
"""
        },
        {
            "category": cat_parents,
            "title": "Combien coute Prof Chez Vous ?",
            "slug": "combien-coute-prof-chez-vous",
            "keywords": "prix, tarif, cout, commission, gratuite, payer, argent",
            "order": 8,
            "content": f"""
<h2>La transparence financiere</h2>
<p>Chez Prof Chez Vous, il n'y a pas de frais caches. Voici exactement ce qui est gratuit et ce qui ne l'est pas.</p>

<h3>Ce qui est 100% GRATUIT</h3>
<ul>
    <li>La creation de votre compte parent.</li>
    <li>La {lp("comment-trouver-un-professeur", "recherche et la consultation des profils")} de professeurs.</li>
    <li>La mise en relation et l'echange via messagerie.</li>
    <li><strong>Les 45 premieres minutes du premier cours</strong> ({lp("comment-fonctionne-la-seance-dessai", "seance d'essai")}).</li>
</ul>

<h3>Ce que vous payez</h3>
<p>Vous ne payez <strong>que les heures de cours</strong> effectuees par le professeur, au tarif qu'il a lui-meme fixe sur son profil.</p>
<p>La plateforme se remunere en prelevant une petite commission transparente sur les transactions, ce qui nous permet de maintenir le site, de {lp("pourquoi-les-professeurs-sont-ils-verifies", "verifier les profils")} et de vous offrir un support client de qualite.</p>

<h2>Nos engagements financiers</h2>
<p>{la("quels-sont-les-engagements", "Decouvrez tous les engagements de Prof Chez Vous")} en matiere de transparence, de securite et de qualite.</p>
"""
        },

        # =====================================================================
        # PROFESSEURS
        # =====================================================================
        {
            "category": cat_profs,
            "title": "Qui peut devenir professeur partenaire ?",
            "slug": "qui-peut-devenir-professeur-partenaire",
            "keywords": "profil, eligibilite, diplome, etudiant, repetiteur, inscription",
            "order": 1,
            "content": f"""
<h2>Une opportunite pour les passionnes d'enseignement</h2>
<p>Prof Chez Vous n'est pas reserve uniquement aux enseignants de metier. Nous croyons que la pedagogie et la maitrise d'une matiere peuvent venir de differents profils.</p>

<h3>Vous pouvez nous rejoindre si vous etes</h3>
<ul>
    <li><strong>Un enseignant certifie :</strong> Professeur de college/lycee ou instituteur.</li>
    <li><strong>Un repetiteur experimente :</strong> Vous faites deja du soutien scolaire depuis plusieurs annees.</li>
    <li><strong>Un etudiant universitaire :</strong> Vous avez un excellent niveau dans votre filiere (Licence, Master, Ingenierie) et une forte envie de transmettre vos connaissances.</li>
    <li><strong>Un professionnel :</strong> Vous maitrisez une competence specifique (ex: informatique, langues) que vous souhaitez enseigner.</li>
</ul>

<h2>La seule condition absolue</h2>
<p>Vous devez etre capable de justifier votre niveau (par un diplome ou un releve de notes) dans la matiere que vous souhaitez enseigner. {lt("quels-documents-sont-demandes", "Consultez la liste des documents necessaires")}.</p>
<p>Pret a vous lancer ? {lt("comment-creer-son-profil", "Suivez le guide de creation de profil")}.</p>
<p>{la("quest-ce-quun-professeur-partenaire", "Decouvrez ce que signifie etre un professeur partenaire")}.</p>
"""
        },
        {
            "category": cat_profs,
            "title": "Comment creer son profil ?",
            "slug": "comment-creer-son-profil",
            "keywords": "inscription, creation, formulaire, etapes, compte, guide",
            "order": 2,
            "content": f"""
<h2>Votre vitrine professionnelle en ligne</h2>
<p>Creer votre profil est la premiere etape pour attirer des eleves. C'est l'equivalent de votre CV en ligne, mais en mieux.</p>

<h3>Les etapes de creation</h3>
<ol>
    <li>Allez sur la page d'inscription et selectionnez le role <strong>Professeur</strong>.</li>
    <li>Remplissez vos informations de base (Nom, prenom, email).</li>
    <li>Completez votre tableau de bord : ajoutez une belle photo de profil (souriante et professionnelle).</li>
    <li>Redigez votre biographie : expliquez qui vous etes et quelle est votre methode pedagogique.</li>
    <li>Selectionnez vos matieres, les niveaux que vous ciblez, et definissez votre tarif horaire. {lt("comment-choisir-matieres-et-classes", "Nos conseils pour bien choisir")}.</li>
    <li>Soumettez vos {lt("quels-documents-sont-demandes", "pieces justificatives")} pour la verification.</li>
</ol>

<h2>L'importance d'une bonne presentation</h2>
<p>Prenez votre temps pour rediger une bonne presentation. C'est ce qui convaincra les parents de vous choisir ! {lt("comment-ameliorer-qualite-profil", "Decouvrez nos conseils pour un profil qui convertit")}.</p>
"""
        },
        {
            "category": cat_profs,
            "title": "Quels documents sont demandes ?",
            "slug": "quels-documents-sont-demandes",
            "keywords": "documents, justificatifs, carte identite, diplome, releve, pieces",
            "order": 3,
            "content": f"""
<h2>Les pieces a fournir pour etre certifie</h2>
<p>Pour garantir la securite et le niveau des enseignants sur la plateforme, nous exigeons des documents officiels lors de votre inscription.</p>

<h3>Documents obligatoires</h3>
<ul>
    <li><strong>Une piece d'identite valide :</strong> Carte d'Identite Nationale (CIP ou biometrique), Passeport ou Permis de conduire.</li>
    <li><strong>Une preuve de niveau academique :</strong> Le diplome le plus eleve que vous possedez (BAC, Licence, Master) OU un releve de notes recent si vous etes encore etudiant.</li>
</ul>

<h3>Confidentialite de vos documents</h3>
<p>Vos documents ne seront jamais publies sur votre profil public. Ils sont stockes de maniere securisee et ne servent qu'a notre equipe de validation.</p>

<h2>Etape suivante</h2>
<p>Une fois vos documents soumis, {lt("comment-fonctionne-la-verification", "decouvrez comment se deroule le processus de verification")}.</p>
<p>Vous souhaitez enseigner une matiere qui ne figure pas sur votre diplome ? {lt("enseigner-matiere-differente-diplome", "C'est possible, decouvrez comment")}.</p>
"""
        },
        {
            "category": cat_profs,
            "title": "Comment fonctionne la verification ?",
            "slug": "comment-fonctionne-la-verification",
            "keywords": "validation, equipe, controle, delai, approuve, rejete, badge",
            "order": 4,
            "content": f"""
<h2>Le processus d'approbation</h2>
<p>Une fois que vous avez {lt("comment-creer-son-profil", "rempli votre profil")} et soumis vos {lt("quels-documents-sont-demandes", "documents")}, notre equipe prend le relais.</p>

<h3>Les etapes de la verification</h3>
<ol>
    <li><strong>Controle manuel :</strong> Un membre de notre equipe examine vos informations, votre photo, votre presentation et verifie la coherence de vos diplomes avec les matieres que vous souhaitez enseigner.</li>
    <li><strong>Retour sous 48h :</strong> Vous recevrez une notification (et un email) vous informant de la decision.</li>
    <li><strong>Validation :</strong> Si tout est conforme, votre profil obtient le badge "Certifie" et devient visible publiquement sur la plateforme.</li>
    <li><strong>Correction :</strong> S'il manque une information (photo floue, description trop courte), votre profil passera en statut "A corriger" et nous vous indiquerons ce qu'il faut modifier.</li>
</ol>

<h2>Apres la validation</h2>
<p>Nous ne rejetons jamais un profil par pur plaisir. Notre but est de vous aider a avoir la meilleure presentation possible ! Une fois valide, {lt("comment-recevoir-premieres-demandes", "decouvrez comment recevoir vos premieres demandes d'eleves")}.</p>
"""
        },
        {
            "category": cat_profs,
            "title": "Puis-je enseigner une matiere differente de mon diplome ?",
            "slug": "enseigner-matiere-differente-diplome",
            "keywords": "derogation, autre matiere, competences, talent, diplome",
            "order": 5,
            "content": f"""
<h2>Vos competences au-dela des diplomes</h2>
<p>Oui, c'est tout a fait possible ! Nous savons qu'un etudiant en Droit peut exceller en Anglais, ou qu'un etudiant en Medecine peut etre un brillant professeur de Mathematiques au college.</p>

<h3>La regle d'or</h3>
<p>Si vous souhaitez enseigner une matiere qui ne figure pas sur l'intitule direct de votre diplome superieur, vous devez simplement etre en mesure de <strong>prouver votre niveau</strong> dans cette matiere.</p>

<h3>Exemple concret</h3>
<p>Fournissez votre releve de notes du Baccalaureat montrant que vous avez eu une excellente note dans cette matiere specifique. Notre equipe evaluera votre demande avec bienveillance.</p>

<h2>Comment soumettre votre demande ?</h2>
<p>Lors de la {lt("comment-creer-son-profil", "creation de votre profil")}, selectionnez les matieres souhaitees et joignez les {lt("quels-documents-sont-demandes", "justificatifs correspondants")}. Notre equipe de {lt("comment-fonctionne-la-verification", "verification")} evaluera votre dossier.</p>
"""
        },
        {
            "category": cat_profs,
            "title": "Comment choisir les matieres et les classes ?",
            "slug": "comment-choisir-matieres-et-classes",
            "keywords": "niveaux, classes, matieres, specialite, cibler, strategie",
            "order": 6,
            "content": f"""
<h2>Misez sur vos points forts</h2>
<p>L'erreur la plus commune des nouveaux repetiteurs est de vouloir "tout enseigner, de la maternelle a l'universite". C'est une erreur strategique.</p>

<h3>Nos conseils pour un profil attractif</h3>
<ul>
    <li><strong>Soyez specialiste, pas generaliste :</strong> Les parents preferent engager un "Expert en Mathematiques pour le Lycee" plutot qu'un professeur "Toutes matieres, tous niveaux".</li>
    <li><strong>Soyez honnete sur vos capacites :</strong> N'acceptez d'enseigner en classe d'examen (3eme, Terminale) que si vous maitrisez parfaitement les programmes officiels.</li>
    <li><strong>Adaptez votre tarif :</strong> Les cours pour les classes superieures demandent plus de preparation et justifient un tarif legerement plus eleve.</li>
</ul>

<h2>Envie d'enseigner une matiere hors diplome ?</h2>
<p>{lt("enseigner-matiere-differente-diplome", "Decouvrez comment enseigner une matiere differente de votre diplome")}. C'est possible sous conditions.</p>
<p>Pour maximiser vos chances de recevoir des demandes, {lt("comment-ameliorer-qualite-profil", "optimisez la qualite de votre profil")}.</p>
"""
        },
        {
            "category": cat_profs,
            "title": "Comment recevoir mes premieres demandes ?",
            "slug": "comment-recevoir-premieres-demandes",
            "keywords": "clients, eleves, demandes, visibilite, premiers, attractivite",
            "order": 7,
            "content": f"""
<h2>Sortir du lot des le premier jour</h2>
<p>Une fois votre profil {lt("comment-fonctionne-la-verification", "valide")}, vous etes en competition avec d'autres excellents professeurs. Voici comment attirer l'attention des parents.</p>

<h3>Les 4 cles du succes</h3>
<ol>
    <li><strong>Une description impeccable :</strong> Evitez les fautes d'orthographe. Une seule faute dans votre biographie peut dissuader un parent.</li>
    <li><strong>Une tarification juste :</strong> Pour obtenir vos premiers eleves et vos premiers avis positifs, commencez par un tarif raisonnable et attractif. Vous pourrez l'augmenter par la suite.</li>
    <li><strong>Reactivite :</strong> Lorsque vous recevez un message d'un parent, repondez le plus vite possible. La rapidite de reponse est tres appreciee.</li>
    <li><strong>Partagez votre profil :</strong> Utilisez le lien direct de votre profil Prof Chez Vous et partagez-le sur vos reseaux sociaux (WhatsApp, Facebook) pour montrer votre professionnalisme a votre entourage.</li>
</ol>

<h2>Ameliorez votre profil en continu</h2>
<p>{lt("comment-ameliorer-qualite-profil", "Decouvrez tous nos conseils pour un profil qui convertit")} : photo, bio, disponibilites et bien plus.</p>
"""
        },
        {
            "category": cat_profs,
            "title": "Comment ameliorer la qualite de mon profil ?",
            "slug": "comment-ameliorer-qualite-profil",
            "keywords": "optimisation, photo, bio, presentation, marketing, qualite",
            "order": 8,
            "content": f"""
<h2>Les secrets d'un profil qui convertit</h2>
<p>Votre profil est votre argumentaire de vente. S'il est neglige, les parents passeront au profil suivant.</p>

<h3>1. La Photo (Le plus important)</h3>
<p>Utilisez une photo lumineuse, ou vous etes seul, de face, et souriant. Un fond uni est preferable. Evitez les selfies de mauvaise qualite ou les lunettes de soleil.</p>

<h3>2. La Presentation (La Bio)</h3>
<p>Structurez votre presentation en 3 parties :</p>
<ul>
    <li><em>Qui etes-vous ?</em> (Votre parcours academique).</li>
    <li><em>Quelle est votre methode ?</em> (Comment faites-vous progresser un eleve en difficulte).</li>
    <li><em>Pourquoi vous choisir ?</em> (Votre patience, votre passion, vos resultats passes).</li>
</ul>

<h3>3. Les disponibilites</h3>
<p>Gardez votre calendrier de disponibilites a jour. Un parent sera frustre s'il vous contacte pour un jeudi alors que vous n'etes finalement pas disponible.</p>

<h2>Les prochaines etapes</h2>
<p>Un bon profil est la base, mais la {lt("comment-recevoir-premieres-demandes", "reactivite et le partage")} feront la difference pour recevoir vos premiers eleves.</p>
<p>{lt("comment-choisir-matieres-et-classes", "Revoyez egalement vos choix de matieres et classes")} pour vous assurer qu'ils correspondent a votre expertise.</p>
"""
        },

        # =====================================================================
        # A PROPOS
        # =====================================================================
        {
            "category": cat_apropos,
            "title": "Pourquoi Prof Chez Vous existe ?",
            "slug": "pourquoi-prof-chez-vous-existe",
            "keywords": "histoire, origine, creation, but, probleme, mission",
            "order": 1,
            "content": f"""
<h2>Ne d'un constat simple</h2>
<p>Au Benin, trouver un bon repetiteur a toujours ete un parcours du combattant, base uniquement sur le bouche-a-oreille et la chance. De l'autre cote, d'excellents jeunes enseignants et etudiants brillants peinent a trouver des eleves pour rentabiliser leurs competences.</p>

<h2>Notre mission</h2>
<p><strong>Prof Chez Vous</strong> a ete cree pour resoudre ce probleme : creer un pont numerique, fiable et transparent entre la demande des parents soucieux de la reussite de leurs enfants, et l'offre des talents locaux.</p>
<p>Nous croyons que chaque enfant merite un accompagnement de qualite, et que chaque enseignant competent merite une {la("quest-ce-quun-professeur-partenaire", "identite professionnelle reconnue")}.</p>
<p>{la("quelle-est-notre-vision", "Decouvrez ou nous allons dans les prochaines annees")}.</p>
"""
        },
        {
            "category": cat_apropos,
            "title": "Comment fonctionne la plateforme ?",
            "slug": "comment-fonctionne-la-plateforme",
            "keywords": "technologie, mise en relation, concept, mecanisme, marketplace",
            "order": 2,
            "content": f"""
<h2>Le numerique au service de l'education</h2>
<p>Prof Chez Vous est une "marketplace" (place de marche) de l'education.</p>
<p>Nous centralisons les profils de professeurs particuliers de tout le pays dans une base de donnees consultable par tous. Lorsqu'un parent trouve un profil interessant, notre systeme de messagerie integree permet la mise en relation.</p>

<h2>Notre role</h2>
<p>Nous n'intervenons pas dans la pedagogie du professeur. Nous fournissons simplement les outils technologiques pour que la rencontre et le suivi se fassent dans les meilleures conditions :</p>
<ul>
    <li>Un {lp("comment-trouver-un-professeur", "moteur de recherche intelligent")} pour les parents.</li>
    <li>Un {lt("comment-creer-son-profil", "espace professionnel")} pour les professeurs.</li>
    <li>Un {lp("pourquoi-les-professeurs-sont-ils-verifies", "systeme de verification")} rigoureux.</li>
    <li>Une {lp("comment-fonctionne-la-seance-dessai", "seance d'essai gratuite")} pour chaque nouvel engagement.</li>
</ul>
"""
        },
        {
            "category": cat_apropos,
            "title": "Pourquoi verifions-nous les professeurs ?",
            "slug": "pourquoi-verifions-nous-les-professeurs",
            "keywords": "philosophie, controle, charte, qualite, serieux, valeurs",
            "order": 3,
            "content": f"""
<h2>L'excellence par la selection</h2>
<p>Notre promesse aux parents est la serenite. Sans verification, n'importe qui pourrait s'improviser professeur de mathematiques, au risque de detruire le niveau d'un enfant au lieu de l'ameliorer.</p>

<h2>Le coeur de notre valeur ajoutee</h2>
<p>La verification est le pilier central de Prof Chez Vous. Elle prouve notre engagement envers la qualite educative et donne aux professeurs inscrits un veritable label de serieux qui justifie leurs tarifs.</p>
<p>Pour les parents : {lp("pourquoi-les-professeurs-sont-ils-verifies", "decouvrez ce que garantit le badge Certifie")}.</p>
<p>Pour les professeurs : {lt("comment-fonctionne-la-verification", "consultez le detail du processus de verification")}.</p>
"""
        },
        {
            "category": cat_apropos,
            "title": "Comment protegeons-nous les parents et les apprenants ?",
            "slug": "comment-protegeons-nous-les-parents",
            "keywords": "protection, signalement, exclusion, securite, ecosysteme",
            "order": 4,
            "content": f"""
<h2>Un ecosysteme sain et encadre</h2>
<p>Au-dela de la {la("pourquoi-verifions-nous-les-professeurs", "verification initiale des identites")}, nous protegeons notre communaute grace a plusieurs mecanismes.</p>

<h3>Nos dispositifs de protection</h3>
<ul>
    <li><strong>Un systeme d'evaluation (a venir) :</strong> Les parents pourront noter les professeurs, ce qui ecartera naturellement les profils peu performants.</li>
    <li><strong>La {lp("comment-fonctionne-la-seance-dessai", "seance d'essai")} :</strong> Qui agit comme un filet de securite pour s'assurer du bon comportement du professeur.</li>
    <li><strong>Un service client reactif :</strong> Pret a intervenir et a suspendre tout compte qui ne respecterait pas notre charte ethique.</li>
</ul>

<h2>Que faire en cas de probleme ?</h2>
<p>Si vous rencontrez un souci avec un professeur, {lp("que-faire-si-je-ne-suis-pas-satisfait", "decouvrez les options a votre disposition")}.</p>
"""
        },
        {
            "category": cat_apropos,
            "title": "Pourquoi proposons-nous une seance d'essai ?",
            "slug": "pourquoi-une-seance-dessai",
            "keywords": "raisonnement, essai, gratuit, logique, philosophie, choix",
            "order": 5,
            "content": f"""
<h2>Le droit de choisir librement</h2>
<p>L'apprentissage humain est avant tout une question de "feeling" et de relation interpersonnelle. Un professeur peut etre excellent sur le papier, mais sa pedagogie peut ne pas resonner avec le caractere de votre enfant.</p>

<h2>Debloquer la prise de decision</h2>
<p>Nous imposons cette seance d'essai gratuite car elle retire le stress financier du premier contact et permet de construire l'engagement sur des bases saines et volontaires.</p>
<p>Pour connaitre les details pratiques de l'essai : {lp("comment-fonctionne-la-seance-dessai", "consultez le guide complet de la seance d'essai")}.</p>
<p>Pour comprendre ce qui se passe apres : {lp("comment-se-deroule-un-engagement", "decouvrez le deroulement d'un engagement")}.</p>
"""
        },
        {
            "category": cat_apropos,
            "title": "Qu'est-ce qu'un professeur partenaire ?",
            "slug": "quest-ce-quun-professeur-partenaire",
            "keywords": "partenaire, statut, identite, freelance, independant, label",
            "order": 6,
            "content": f"""
<h2>Des independants valorises</h2>
<p>Un professeur partenaire n'est pas un employe de Prof Chez Vous. C'est un travailleur independant qui utilise notre plateforme pour gerer son activite de soutien scolaire.</p>

<h2>Liberte et credibilite</h2>
<p>Il est maitre de son emploi du temps, de sa methode pedagogique et de sa tarification. Nous lui offrons simplement :</p>
<ul>
    <li>La <strong>credibilite</strong> via le badge Certifie ({la("pourquoi-verifions-nous-les-professeurs", "en savoir plus sur la verification")}).</li>
    <li>La <strong>visibilite</strong> via notre trafic web et notre moteur de recherche.</li>
    <li>Les <strong>outils</strong> pour gerer ses cours et sa communication avec les parents.</li>
</ul>
<p>Vous souhaitez devenir professeur partenaire ? {lt("qui-peut-devenir-professeur-partenaire", "Verifiez votre eligibilite")} et {lt("comment-creer-son-profil", "creez votre profil")}.</p>
"""
        },
        {
            "category": cat_apropos,
            "title": "Quels sont les engagements de Prof Chez Vous ?",
            "slug": "quels-sont-les-engagements",
            "keywords": "valeurs, transparence, securite, qualite, ethique, charte",
            "order": 7,
            "content": f"""
<h2>Notre charte de confiance</h2>
<p>Notre entreprise repose sur 3 piliers fondamentaux.</p>

<h3>1. Transparence</h3>
<p>Les tarifs affiches sont ceux qui sont appliques. Pas de frais caches. {lp("combien-coute-prof-chez-vous", "Decouvrez notre politique tarifaire")}.</p>

<h3>2. Securite</h3>
<p>Nous ne publierons jamais le profil d'un enseignant dont nous n'avons pas {la("pourquoi-verifions-nous-les-professeurs", "verifie l'identite")}. {la("comment-protegeons-nous-les-parents", "Decouvrez comment nous protegeons les familles")}.</p>

<h3>3. Soutien</h3>
<p>Nous nous engageons a repondre rapidement a toute preoccupation d'un parent ou d'un professeur via notre service de support.</p>
"""
        },
        {
            "category": cat_apropos,
            "title": "Quelle est notre vision ?",
            "slug": "quelle-est-notre-vision",
            "keywords": "futur, afrique, developpement, edtech, avenir, ambition",
            "order": 8,
            "content": f"""
<h2>Democratiser l'excellence educative au Benin et au-dela</h2>
<p>Aujourd'hui, nous structurons le marche du soutien scolaire a domicile et en ligne au Benin.</p>

<h2>Notre feuille de route</h2>
<p>Demain, notre vision est de devenir la plateforme EdTech de reference en Afrique francophone, en proposant non seulement des {la("quest-ce-quun-professeur-partenaire", "professeurs partenaires")}, mais aussi :</p>
<ul>
    <li>Des outils de suivi pedagogique avances.</li>
    <li>Des classes virtuelles interactives.</li>
    <li>Des ressources d'apprentissage adaptees aux realites de nos systemes educatifs.</li>
</ul>
<p>Tout a commence par un constat simple. {la("pourquoi-prof-chez-vous-existe", "Decouvrez l'histoire de Prof Chez Vous")}.</p>
<p>{la("quels-sont-les-engagements", "Nos engagements")} guident chacune de nos decisions.</p>
"""
        },
    ]

    # =========================================================================
    # 3. Populate
    # =========================================================================
    Article.objects.all().delete()
    Category.objects.exclude(slug__in=["parents", "professeurs", "a-propos"]).delete()

    for item in articles_data:
        article, created = Article.objects.update_or_create(
            slug=item["slug"],
            defaults={
                "category": item["category"],
                "title": item["title"],
                "keywords": item["keywords"],
                "content": item["content"],
            }
        )
        print(f"[{'CREATED' if created else 'UPDATED'}] {article.title}")

    print("\nDone! 24 articles with inline cross-links populated successfully.")


if __name__ == '__main__':
    run()
