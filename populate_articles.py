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
            "keywords": "plateforme, presentation, concept, professeurs, benin, soutien scolaire",
            "order": 1,
            "content": f"""
<h2>Une nouvelle facon de trouver le bon professeur</h2>
<p>Prof Chez Vous n'est pas une agence de soutien scolaire classique. C'est la premiere plateforme au Benin qui redonne le pouvoir aux parents et une veritable identite professionnelle aux enseignants.</p>
<p>Notre plateforme vous permet de rechercher, comparer et engager directement des professeurs particuliers (repetiteurs) verifies et certifies. Fini le bouche-a-oreille incertain : vous avez desormais acces a un catalogue transparent de profils competents pres de chez vous.</p>

<h2>Comment ca marche concrètement ?</h2>
<ol>
    <li><strong>Recherche libre :</strong> Vous parcourez les profils selon la matiere, le niveau et la localisation. {lp("comment-trouver-un-professeur", "Decouvrez le parcours de recherche complet")}.</li>
    <li><strong>Transparence totale :</strong> Les diplomes, l'experience et les tarifs sont affiches sur chaque profil. Chaque professeur est {lp("pourquoi-les-professeurs-sont-ils-verifies", "verifie par notre equipe")}.</li>
    <li><strong>Contact direct :</strong> Vous echangez avec le professeur avant de prendre votre decision.</li>
    <li><strong>Seance d'essai :</strong> Vous testez le professeur gratuitement pendant 45 minutes avant de vous engager. {lp("comment-fonctionne-la-seance-dessai", "En savoir plus sur l'essai gratuit")}.</li>
</ol>

<h3>Pour qui est faite la plateforme ?</h3>
<p>Prof Chez Vous s'adresse a tous les parents et apprenants au Benin qui cherchent un accompagnement scolaire de qualite, du primaire au superieur. Que votre enfant ait besoin d'un soutien regulier ou d'une preparation intensive avant un examen, vous trouverez le professeur qu'il lui faut.</p>
<p>Vous voulez en savoir plus sur notre mission ? {la("pourquoi-prof-chez-vous-existe", "Decouvrez pourquoi Prof Chez Vous existe")}.</p>
"""
        },
        {
            "category": cat_parents,
            "title": "Comment trouver un professeur ?",
            "slug": "comment-trouver-un-professeur",
            "keywords": "recherche, trouver, parcours, chercher, filtrer, localisation",
            "order": 2,
            "content": f"""
<h2>Le parcours de recherche pas-a-pas</h2>
<p>Trouver le professeur ideal pour votre enfant se fait en quelques clics grace a notre moteur de recherche intelligent.</p>

<h3>Les etapes de votre recherche</h3>
<ol>
    <li><strong>Utilisez la barre de recherche :</strong> Depuis la page d'accueil, cliquez sur "Rechercher un prof".</li>
    <li><strong>Appliquez vos filtres :</strong> Precisez la matiere (ex: Mathematiques), le niveau (ex: Terminale) et votre localisation (ex: Cotonou).</li>
    <li><strong>Parcourez les resultats :</strong> Une liste de professeurs correspondant a vos criteres s'affiche.</li>
    <li><strong>Consultez les profils :</strong> Cliquez sur un professeur pour voir sa description detaillee, ses methodes pedagogiques et ses tarifs.</li>
    <li><strong>Prenez contact :</strong> Une fois votre choix fait, connectez-vous ou creez votre compte parent pour lui envoyer une demande d'engagement.</li>
</ol>

<h2>Comment faire le meilleur choix ?</h2>
<p>Nous vous recommandons de selectionner 2 ou 3 profils interessants afin de pouvoir echanger avec eux et comparer. {lp("comment-choisir-le-bon-professeur", "Consultez notre guide pour choisir le bon professeur")}.</p>
<p>Tous les professeurs affiches sur la plateforme sont {lp("pourquoi-les-professeurs-sont-ils-verifies", "verifies par notre equipe")} : vous pouvez consulter les profils en toute confiance.</p>
"""
        },
        {
            "category": cat_parents,
            "title": "Comment choisir le bon professeur ?",
            "slug": "comment-choisir-le-bon-professeur",
            "keywords": "choix, comparer, meilleur, profil, decision, criteres",
            "order": 3,
            "content": f"""
<h2>Les criteres pour faire le bon choix</h2>
<p>Choisir un repetiteur est une decision importante. Sur Prof Chez Vous, toutes les informations sont publiques pour vous aider a prendre une decision eclairee.</p>

<h3>Ce qu'il faut regarder sur un profil</h3>
<ul>
    <li><strong>L'experience et la methode :</strong> Lisez attentivement la description du professeur. Un bon professeur explique <em>comment</em> il enseigne, pas seulement ce qu'il enseigne.</li>
    <li><strong>La verification :</strong> Assurez-vous que le profil possede le badge vert "Certifie". Cela garantit que nous avons {lp("pourquoi-les-professeurs-sont-ils-verifies", "controle son identite et ses diplomes")}.</li>
    <li><strong>Le tarif :</strong> Verifiez que les honoraires du professeur correspondent a votre budget sur le long terme. {lp("combien-coute-prof-chez-vous", "Consultez notre guide sur les tarifs")}.</li>
    <li><strong>La video de presentation (si disponible) :</strong> Rien de tel qu'une courte video pour ressentir l'energie et la pedagogie d'un enseignant !</li>
</ul>

<h2>Le tarif le plus eleve est-il le meilleur ?</h2>
<p>Pas necessairement. Le tarif le plus eleve ne garantit pas toujours le meilleur professeur pour <em>votre</em> enfant. Le feeling et la pedagogie sont essentiels. C'est pourquoi nous proposons toujours une {lp("comment-fonctionne-la-seance-dessai", "seance d'essai gratuite de 45 minutes")} pour que vous puissiez juger par vous-meme.</p>
"""
        },
        {
            "category": cat_parents,
            "title": "Pourquoi les professeurs sont-ils verifies ?",
            "slug": "pourquoi-les-professeurs-sont-ils-verifies",
            "keywords": "verification, confiance, securite, diplomes, identite, badge, certifie",
            "order": 4,
            "content": f"""
<h2>Votre securite est notre priorite absolue</h2>
<p>Faire entrer quelqu'un chez soi pour accompagner son enfant demande une confiance totale. C'est pourquoi nous avons mis en place le processus de verification le plus strict du Benin.</p>

<h3>En quoi consiste notre verification ?</h3>
<p>Avant d'obtenir le badge <strong>Certifie</strong> et d'etre visible sur la plateforme, chaque professeur doit nous fournir :</p>
<ul>
    <li><strong>Une piece d'identite valide :</strong> Nous verifions que la personne est bien celle qu'elle pretend etre.</li>
    <li><strong>Ses diplomes et attestations :</strong> Si un professeur affirme etre titulaire d'une Licence en Mathematiques, nous verifions physiquement ou numeriquement ce diplome.</li>
    <li><strong>Son casier judiciaire (pour certains profils) :</strong> Afin de garantir un environnement sur pour les apprenants.</li>
</ul>

<h2>Un processus rigoureux pour votre tranquillite</h2>
<p>Sur Prof Chez Vous, il n'y a pas d'anonymat. Vous savez exactement qui vous engagez. {la("pourquoi-verifions-nous-les-professeurs", "Decouvrez la philosophie derriere notre processus de verification")}.</p>
<p>Si vous etes professeur, {lt("comment-fonctionne-la-verification", "consultez le detail du processus de verification")} et les {lt("quels-documents-sont-demandes", "documents necessaires")}.</p>
"""
        },
        {
            "category": cat_parents,
            "title": "Comment fonctionne la seance d'essai ?",
            "slug": "comment-fonctionne-la-seance-dessai",
            "keywords": "essai, gratuit, premier cours, 45 minutes, test, seance",
            "order": 5,
            "content": f"""
<h2>Testez avant de vous engager</h2>
<p>Parce qu'un CV ne fait pas tout, nous avons rendu obligatoire une <strong>seance d'essai de 45 minutes</strong> pour chaque nouvel engagement.</p>

<h3>Les regles de l'essai</h3>
<ol>
    <li><strong>100% Gratuit :</strong> Vous ne payez absolument rien pour cette premiere seance.</li>
    <li><strong>Decouverte mutuelle :</strong> Ces 45 minutes servent a faire connaissance, evaluer le niveau de l'enfant et discuter des objectifs.</li>
    <li><strong>Sans pression :</strong> Si le feeling ne passe pas, vous etes totalement libre de ne pas donner suite, sans avoir a vous justifier.</li>
</ol>

<h2>Pourquoi cet essai est-il si important ?</h2>
<p>Cette seance protege les parents d'un mauvais choix, et permet au professeur de s'assurer qu'il a les competences pour aider l'apprenant. {la("pourquoi-une-seance-dessai", "Decouvrez le raisonnement derriere cette politique")}.</p>
<p>Si l'essai est concluant, {lp("comment-se-deroule-un-engagement", "decouvrez comment se deroule la suite de l'engagement")}. Sinon, {lp("que-faire-si-je-ne-suis-pas-satisfait", "vous etes libre de chercher un autre professeur")}.</p>
"""
        },
        {
            "category": cat_parents,
            "title": "Comment se deroule un engagement avec un professeur ?",
            "slug": "comment-se-deroule-un-engagement",
            "keywords": "engagement, apres essai, contrat, planning, paiement, suivi",
            "order": 6,
            "content": f"""
<h2>L'organisation de l'accompagnement</h2>
<p>Si la {lp("comment-fonctionne-la-seance-dessai", "seance d'essai")} est concluante et que vous souhaitez poursuivre avec le professeur, voici comment cela s'organise.</p>

<h3>1. Planification des cours</h3>
<p>Vous convenez directement avec le professeur des jours et heures de cours (ex: tous les mercredis a 15h). Le planning est flexible et s'adapte a vos contraintes.</p>

<h3>2. Tarification et paiement</h3>
<p>Le professeur vous appliquera le tarif affiche sur son profil. Prof Chez Vous vous permet de payer le professeur via la plateforme (par Mobile Money ou carte) de maniere totalement securisee, garantissant ainsi une trace de toutes vos transactions. {lp("combien-coute-prof-chez-vous", "En savoir plus sur les tarifs et la transparence financiere")}.</p>

<h3>3. Suivi pedagogique</h3>
<p>Le professeur pourra vous faire des retours reguliers sur la progression de votre enfant directement via la messagerie de la plateforme.</p>

<h2>Et si ca ne se passe pas bien ?</h2>
<p>Vous n'etes jamais bloque. {lp("que-faire-si-je-ne-suis-pas-satisfait", "Decouvrez vos options en cas d'insatisfaction")}.</p>
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
