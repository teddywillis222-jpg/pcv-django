import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from help_center.models import Category, Article
from django.utils.text import slugify

def run():
    # 1. Ensure Categories Exist
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
            "name": "À propos de Prof Chez Vous",
            "description": "Notre mission, notre vision et nos engagements.",
            "icon": "bi bi-info-circle",
            "order": 3,
            "target_audience": "all"
        }
    )

    articles_data = [
        # ==========================================
        # PARENTS
        # ==========================================
        {
            "category": cat_parents,
            "title": "1. Qu'est-ce que Prof Chez Vous ?",
            "slug": "quest-ce-que-prof-chez-vous-parents",
            "keywords": "plateforme, fonctionnement, principe, concept, professeurs, bénin",
            "content": """
            <h2>Une nouvelle façon de trouver le bon professeur</h2>
            <p>Prof Chez Vous n'est pas une agence de soutien scolaire classique. C'est la première plateforme au Bénin qui redonne le pouvoir aux parents et une véritable identité professionnelle aux enseignants.</p>
            <p>Notre plateforme vous permet de rechercher, comparer et engager directement des professeurs particuliers (répétiteurs) vérifiés et certifiés. Fini le bouche-à-oreille incertain : vous avez désormais accès à un catalogue transparent de profils compétents près de chez vous.</p>
            <h3>Comment ça marche ?</h3>
            <ul>
                <li><strong>Recherche libre :</strong> Vous parcourez les profils selon la matière, le niveau et la localisation.</li>
                <li><strong>Transparence totale :</strong> Les diplômes, l'expérience et les tarifs sont affichés sur chaque profil.</li>
                <li><strong>Contact direct :</strong> Vous échangez avec le professeur avant de prendre votre décision.</li>
            </ul>
            """
        },
        {
            "category": cat_parents,
            "title": "2. Comment trouver un professeur ?",
            "slug": "comment-trouver-un-professeur",
            "keywords": "recherche, trouver, parcours, chercher, filtrer, localisation",
            "content": """
            <h2>Le parcours de recherche pas-à-pas</h2>
            <p>Trouver le professeur idéal pour votre enfant se fait en quelques clics grâce à notre moteur de recherche intelligent.</p>
            <h3>Les étapes de votre recherche :</h3>
            <ol>
                <li><strong>Utilisez la barre de recherche :</strong> Depuis la page d'accueil, cliquez sur « Rechercher un prof ».</li>
                <li><strong>Appliquez vos filtres :</strong> Précisez la matière (ex: Mathématiques), le niveau (ex: Terminale) et votre localisation (ex: Cotonou).</li>
                <li><strong>Parcourez les résultats :</strong> Une liste de professeurs correspondant à vos critères s'affiche.</li>
                <li><strong>Consultez les profils :</strong> Cliquez sur un professeur pour voir sa description détaillée, ses méthodes pédagogiques et ses tarifs.</li>
                <li><strong>Prenez contact :</strong> Une fois votre choix fait, connectez-vous ou créez votre compte parent pour lui envoyer une demande d'engagement.</li>
            </ol>
            <p>Nous vous recommandons de sélectionner 2 ou 3 profils intéressants afin de pouvoir échanger avec eux et faire le meilleur choix.</p>
            """
        },
        {
            "category": cat_parents,
            "title": "3. Comment choisir le bon professeur ?",
            "slug": "comment-choisir-le-bon-professeur",
            "keywords": "choix, comparer, meilleur, profil, décision",
            "content": """
            <h2>Les critères pour faire le bon choix</h2>
            <p>Choisir un répétiteur est une décision importante. Sur Prof Chez Vous, toutes les informations sont publiques pour vous aider à prendre une décision éclairée.</p>
            <h3>Ce qu'il faut regarder sur un profil :</h3>
            <ul>
                <li><strong>L'expérience et la méthode :</strong> Lisez attentivement la description du professeur. Un bon professeur explique <em>comment</em> il enseigne, pas seulement ce qu'il enseigne.</li>
                <li><strong>La vérification :</strong> Assurez-vous que le profil possède le badge vert "Certifié". Cela garantit que nous avons contrôlé son identité et ses diplômes.</li>
                <li><strong>Le tarif :</strong> Vérifiez que les honoraires du professeur correspondent à votre budget sur le long terme.</li>
                <li><strong>La vidéo de présentation (si disponible) :</strong> Rien de tel qu'une courte vidéo pour ressentir l'énergie et la pédagogie d'un enseignant !</li>
            </ul>
            <p><strong>N'oubliez pas :</strong> Le tarif le plus élevé ne garantit pas toujours le meilleur professeur pour <em>votre</em> enfant. Le feeling et la pédagogie sont essentiels, c'est pourquoi nous proposons toujours une séance d'essai.</p>
            """
        },
        {
            "category": cat_parents,
            "title": "4. Pourquoi les professeurs sont-ils vérifiés ?",
            "slug": "pourquoi-les-professeurs-sont-ils-verifies",
            "keywords": "vérification, confiance, sécurité, diplômes, identité, badge",
            "content": """
            <h2>Votre sécurité est notre priorité absolue</h2>
            <p>Faire entrer quelqu'un chez soi pour accompagner son enfant demande une confiance totale. C'est pourquoi nous avons mis en place le processus de vérification le plus strict du Bénin.</p>
            <h3>En quoi consiste notre vérification ?</h3>
            <p>Avant d'obtenir le badge <strong>Certifié</strong> et d'être visible sur la plateforme, chaque professeur doit nous fournir :</p>
            <ul>
                <li><strong>Une pièce d'identité valide :</strong> Nous vérifions que la personne est bien celle qu'elle prétend être.</li>
                <li><strong>Ses diplômes et attestations :</strong> Si un professeur affirme être titulaire d'une Licence en Mathématiques, nous vérifions physiquement ou numériquement ce diplôme.</li>
                <li><strong>Son casier judiciaire (pour certains profils) :</strong> Afin de garantir un environnement sûr pour les apprenants.</li>
            </ul>
            <p>Sur Prof Chez Vous, il n'y a pas d'anonymat. Vous savez exactement qui vous engagez.</p>
            """
        },
        {
            "category": cat_parents,
            "title": "5. Comment fonctionne la séance d'essai ?",
            "slug": "comment-fonctionne-la-seance-dessai",
            "keywords": "essai, gratuit, premier cours, 45 minutes, test",
            "content": """
            <h2>Testez avant de vous engager</h2>
            <p>Parce qu'un CV ne fait pas tout, nous avons rendu obligatoire une <strong>séance d'essai de 45 minutes</strong> pour chaque nouvel engagement.</p>
            <h3>Les règles de l'essai :</h3>
            <ol>
                <li><strong>100% Gratuit :</strong> Vous ne payez absolument rien pour cette première séance.</li>
                <li><strong>Découverte mutuelle :</strong> Ces 45 minutes servent à faire connaissance, évaluer le niveau de l'enfant et discuter des objectifs.</li>
                <li><strong>Sans pression :</strong> Si le feeling ne passe pas, vous êtes totalement libre de ne pas donner suite, sans avoir à vous justifier.</li>
            </ol>
            <p>Cette séance protège les parents d'un mauvais choix, et permet au professeur de s'assurer qu'il a les compétences pour aider l'apprenant.</p>
            """
        },
        {
            "category": cat_parents,
            "title": "6. Comment se déroule un engagement avec un professeur ?",
            "slug": "comment-se-deroule-un-engagement",
            "keywords": "engagement, après l'essai, contrat, planning, paiement",
            "content": """
            <h2>L'organisation de l'accompagnement</h2>
            <p>Si la séance d'essai est concluante et que vous souhaitez poursuivre avec le professeur, voici comment cela s'organise :</p>
            <h3>1. Planification des cours</h3>
            <p>Vous convenez directement avec le professeur des jours et heures de cours (ex: tous les mercredis à 15h). Le planning est flexible et s'adapte à vos contraintes.</p>
            <h3>2. Tarification et paiement</h3>
            <p>Le professeur vous appliquera le tarif affiché sur son profil. Prof Chez Vous vous permet de payer le professeur via la plateforme (par Mobile Money ou carte) de manière totalement sécurisée, garantissant ainsi une trace de toutes vos transactions.</p>
            <h3>3. Suivi pédagogique</h3>
            <p>Le professeur pourra vous faire des retours réguliers sur la progression de votre enfant directement via la messagerie de la plateforme.</p>
            """
        },
        {
            "category": cat_parents,
            "title": "7. Que faire si je ne suis pas satisfait ?",
            "slug": "que-faire-si-je-ne-suis-pas-satisfait",
            "keywords": "insatisfait, problème, changer, conflit, litige",
            "content": """
            <h2>Vous restez toujours aux commandes</h2>
            <p>L'accompagnement scolaire doit être une solution, pas un problème. Si la prestation d'un professeur ne vous convient plus, vous avez tous les droits.</p>
            <h3>Comment réagir ?</h3>
            <ul>
                <li><strong>Communiquez d'abord :</strong> Souvent, un simple échange avec le professeur permet de réajuster la méthode de travail.</li>
                <li><strong>Mettez fin à l'engagement :</strong> Vous n'êtes lié par aucun contrat à long terme. Vous pouvez stopper les cours à tout moment (en réglant uniquement les cours déjà effectués).</li>
                <li><strong>Signalez à la plateforme :</strong> Si le professeur a eu un comportement inapproprié ou non professionnel, vous pouvez le signaler à notre équipe de support. Nous prendrons des mesures immédiates, pouvant aller jusqu'à l'exclusion du professeur.</li>
            </ul>
            <p>N'hésitez jamais à chercher un autre professeur sur la plateforme si le premier ne convient pas !</p>
            """
        },
        {
            "category": cat_parents,
            "title": "8. Combien coûte Prof Chez Vous ?",
            "slug": "combien-coute-prof-chez-vous",
            "keywords": "prix, tarif, coût, commission, gratuité, payer",
            "content": """
            <h2>La transparence financière</h2>
            <p>Chez Prof Chez Vous, il n'y a pas de frais cachés. Voici exactement ce qui est gratuit et ce qui ne l'est pas :</p>
            <h3>Ce qui est 100% GRATUIT :</h3>
            <ul>
                <li>La création de votre compte parent.</li>
                <li>La recherche et la consultation des profils de professeurs.</li>
                <li>La mise en relation et l'échange via messagerie.</li>
                <li><strong>Les 45 premières minutes du premier cours (séance d'essai).</strong></li>
            </ul>
            <h3>Ce que vous payez :</h3>
            <p>Vous ne payez <strong>que les heures de cours</strong> effectuées par le professeur, au tarif qu'il a lui-même fixé sur son profil. <br>
            La plateforme se rémunère en prélevant une petite commission transparente sur les transactions, ce qui nous permet de maintenir le site, de vérifier les profils et de vous offrir un support client de qualité.</p>
            """
        },

        # ==========================================
        # PROFESSEURS
        # ==========================================
        {
            "category": cat_profs,
            "title": "1. Qui peut devenir professeur partenaire ?",
            "slug": "qui-peut-devenir-professeur-partenaire",
            "keywords": "profil, éligibilité, diplôme, étudiant, répétiteur",
            "content": """
            <h2>Une opportunité pour les passionnés d'enseignement</h2>
            <p>Prof Chez Vous n'est pas réservé uniquement aux enseignants de métier. Nous croyons que la pédagogie et la maîtrise d'une matière peuvent venir de différents profils.</p>
            <h3>Vous pouvez nous rejoindre si vous êtes :</h3>
            <ul>
                <li><strong>Un enseignant certifié :</strong> Professeur de collège/lycée ou instituteur.</li>
                <li><strong>Un répétiteur expérimenté :</strong> Vous faites déjà du soutien scolaire depuis plusieurs années.</li>
                <li><strong>Un étudiant universitaire :</strong> Vous avez un excellent niveau dans votre filière (Licence, Master, Ingénierie) et une forte envie de transmettre vos connaissances.</li>
                <li><strong>Un professionnel :</strong> Vous maîtrisez une compétence spécifique (ex: informatique, langues) que vous souhaitez enseigner.</li>
            </ul>
            <p><strong>La seule condition absolue :</strong> Vous devez être capable de justifier votre niveau (par un diplôme ou un relevé de notes) dans la matière que vous souhaitez enseigner.</p>
            """
        },
        {
            "category": cat_profs,
            "title": "2. Comment créer son profil ?",
            "slug": "comment-creer-son-profil",
            "keywords": "inscription, création, formulaire, étapes, compte",
            "content": """
            <h2>Votre vitrine professionnelle en ligne</h2>
            <p>Créer votre profil est la première étape pour attirer des élèves. C'est l'équivalent de votre CV en ligne, mais en mieux.</p>
            <h3>Les étapes de création :</h3>
            <ol>
                <li>Allez sur la page d'inscription et sélectionnez le rôle <strong>Professeur</strong>.</li>
                <li>Remplissez vos informations de base (Nom, prénom, email).</li>
                <li>Complétez votre tableau de bord : ajoutez une belle photo de profil (souriante et professionnelle).</li>
                <li>Rédigez votre biographie : expliquez qui vous êtes et quelle est votre méthode pédagogique.</li>
                <li>Sélectionnez vos matières, les niveaux que vous ciblez, et définissez votre tarif horaire.</li>
                <li>Soumettez vos pièces justificatives pour la vérification.</li>
            </ol>
            <p>Prenez votre temps pour rédiger une bonne présentation. C'est ce qui convaincra les parents de vous choisir !</p>
            """
        },
        {
            "category": cat_profs,
            "title": "3. Quels documents sont demandés ?",
            "slug": "quels-documents-sont-demandes",
            "keywords": "documents, justificatifs, carte identité, diplôme, relevé",
            "content": """
            <h2>Les pièces à fournir pour être certifié</h2>
            <p>Pour garantir la sécurité et le niveau des enseignants sur la plateforme, nous exigeons des documents officiels lors de votre inscription.</p>
            <h3>Documents obligatoires :</h3>
            <ul>
                <li><strong>Une pièce d'identité valide :</strong> Carte d'Identité Nationale (CIP ou biométrique), Passeport ou Permis de conduire.</li>
                <li><strong>Une preuve de niveau académique :</strong> Le diplôme le plus élevé que vous possédez (BAC, Licence, Master) OU un relevé de notes récent si vous êtes encore étudiant.</li>
            </ul>
            <p><em>Note :</em> Vos documents ne seront jamais publiés sur votre profil public. Ils sont stockés de manière sécurisée et ne servent qu'à notre équipe de validation.</p>
            """
        },
        {
            "category": cat_profs,
            "title": "4. Comment fonctionne la vérification ?",
            "slug": "comment-fonctionne-la-verification",
            "keywords": "validation, équipe, contrôle, délai, approuvé, rejeté",
            "content": """
            <h2>Le processus d'approbation</h2>
            <p>Une fois que vous avez rempli votre profil et soumis vos documents, notre équipe prend le relais.</p>
            <h3>Les étapes de la vérification :</h3>
            <ol>
                <li><strong>Contrôle manuel :</strong> Un membre de notre équipe examine vos informations, votre photo, votre présentation et vérifie la cohérence de vos diplômes avec les matières que vous souhaitez enseigner.</li>
                <li><strong>Retour sous 48h :</strong> Vous recevrez une notification (et un email) vous informant de la décision.</li>
                <li><strong>Validation :</strong> Si tout est conforme, votre profil obtient le badge "Certifié" et devient visible publiquement sur la plateforme.</li>
                <li><strong>Correction :</strong> S'il manque une information (photo floue, description trop courte), votre profil passera en statut "À corriger" et nous vous indiquerons ce qu'il faut modifier.</li>
            </ol>
            <p>Nous ne rejetons jamais un profil par pur plaisir. Notre but est de vous aider à avoir la meilleure présentation possible !</p>
            """
        },
        {
            "category": cat_profs,
            "title": "5. Puis-je enseigner une matière différente de mon diplôme ?",
            "slug": "enseigner-matiere-differente-diplome",
            "keywords": "dérogation, autre matière, compétences, talent, diplôme",
            "content": """
            <h2>Vos compétences au-delà des diplômes</h2>
            <p>Oui, c'est tout à fait possible ! Nous savons qu'un étudiant en Droit peut exceller en Anglais, ou qu'un étudiant en Médecine peut être un brillant professeur de Mathématiques au collège.</p>
            <h3>La règle d'or :</h3>
            <p>Si vous souhaitez enseigner une matière qui ne figure pas sur l'intitulé direct de votre diplôme supérieur, vous devez simplement être en mesure de <strong>prouver votre niveau</strong> dans cette matière.</p>
            <p><strong>Exemple :</strong> Fournissez votre relevé de notes du Baccalauréat montrant que vous avez eu une excellente note dans cette matière spécifique. Notre équipe évaluera votre demande avec bienveillance.</p>
            """
        },
        {
            "category": cat_profs,
            "title": "6. Comment choisir les matières et les classes ?",
            "slug": "comment-choisir-matieres-et-classes",
            "keywords": "niveaux, classes, matières, spécialité, cibler",
            "content": """
            <h2>Misez sur vos points forts</h2>
            <p>L'erreur la plus commune des nouveaux répétiteurs est de vouloir "tout enseigner, de la maternelle à l'université". C'est une erreur stratégique.</p>
            <h3>Nos conseils pour un profil attractif :</h3>
            <ul>
                <li><strong>Soyez spécialiste, pas généraliste :</strong> Les parents préfèrent engager un "Expert en Mathématiques pour le Lycée" plutôt qu'un professeur "Toutes matières, tous niveaux".</li>
                <li><strong>Soyez honnête sur vos capacités :</strong> N'acceptez d'enseigner en classe d'examen (3ème, Terminale) que si vous maîtrisez parfaitement les programmes officiels.</li>
                <li><strong>Adaptez votre tarif :</strong> Les cours pour les classes supérieures demandent plus de préparation et justifient un tarif légèrement plus élevé.</li>
            </ul>
            """
        },
        {
            "category": cat_profs,
            "title": "7. Comment recevoir mes premières demandes ?",
            "slug": "comment-recevoir-premieres-demandes",
            "keywords": "clients, élèves, demandes, visibilité, algorithme",
            "content": """
            <h2>Sortir du lot dès le premier jour</h2>
            <p>Une fois votre profil validé, vous êtes en compétition avec d'autres excellents professeurs. Voici comment attirer l'attention des parents :</p>
            <ol>
                <li><strong>Une description impeccable :</strong> Évitez les fautes d'orthographe. Une seule faute dans votre biographie peut dissuader un parent.</li>
                <li><strong>Une tarification juste :</strong> Pour obtenir vos premiers élèves et vos premiers avis positifs, commencez par un tarif raisonnable et attractif. Vous pourrez l'augmenter par la suite.</li>
                <li><strong>Réactivité :</strong> Lorsque vous recevez un message d'un parent, répondez le plus vite possible. La rapidité de réponse est très appréciée.</li>
                <li><strong>Partagez votre profil :</strong> Utilisez le lien direct de votre profil Prof Chez Vous et partagez-le sur vos réseaux sociaux (WhatsApp, Facebook) pour montrer votre professionnalisme à votre entourage.</li>
            </ol>
            """
        },
        {
            "category": cat_profs,
            "title": "8. Comment améliorer la qualité de mon profil ?",
            "slug": "comment-ameliorer-qualite-profil",
            "keywords": "optimisation, photo, bio, présentation, marketing",
            "content": """
            <h2>Les secrets d'un profil qui convertit</h2>
            <p>Votre profil est votre argumentaire de vente. S'il est négligé, les parents passeront au profil suivant.</p>
            <h3>1. La Photo (Le plus important)</h3>
            <p>Utilisez une photo lumineuse, où vous êtes seul, de face, et souriant. Un fond uni est préférable. Évitez les selfies de mauvaise qualité ou les lunettes de soleil.</p>
            <h3>2. La Présentation (La Bio)</h3>
            <p>Structurez votre présentation en 3 parties :</p>
            <ul>
                <li><em>Qui êtes-vous ?</em> (Votre parcours académique).</li>
                <li><em>Quelle est votre méthode ?</em> (Comment faites-vous progresser un élève en difficulté).</li>
                <li><em>Pourquoi vous choisir ?</em> (Votre patience, votre passion, vos résultats passés).</li>
            </ul>
            <h3>3. Les disponibilités</h3>
            <p>Gardez votre calendrier de disponibilités à jour. Un parent sera frustré s'il vous contacte pour un jeudi alors que vous n'êtes finalement pas disponible.</p>
            """
        },

        # ==========================================
        # A PROPOS
        # ==========================================
        {
            "category": cat_apropos,
            "title": "1. Pourquoi Prof Chez Vous existe ?",
            "slug": "pourquoi-prof-chez-vous-existe",
            "keywords": "histoire, origine, création, but, problème",
            "content": """
            <h2>Né d'un constat simple</h2>
            <p>Au Bénin, trouver un bon répétiteur a toujours été un parcours du combattant, basé uniquement sur le bouche-à-oreille et la chance. De l'autre côté, d'excellents jeunes enseignants et étudiants brillants peinent à trouver des élèves pour rentabiliser leurs compétences.</p>
            <p><strong>Prof Chez Vous</strong> a été créé pour résoudre ce problème : créer un pont numérique, fiable et transparent entre la demande des parents soucieux de la réussite de leurs enfants, et l'offre des talents locaux.</p>
            """
        },
        {
            "category": cat_apropos,
            "title": "2. Comment fonctionne la plateforme ?",
            "slug": "comment-fonctionne-la-plateforme",
            "keywords": "technologie, mise en relation, concept, mécanisme",
            "content": """
            <h2>Le numérique au service de l'éducation</h2>
            <p>Prof Chez Vous est une "marketplace" (place de marché) de l'éducation.</p>
            <p>Nous centralisons les profils de professeurs particuliers de tout le pays dans une base de données consultable par tous. Lorsqu'un parent trouve un profil intéressant, notre système de messagerie intégrée permet la mise en relation.</p>
            <p>Nous n'intervenons pas dans la pédagogie du professeur, nous fournissons simplement les outils technologiques pour que la rencontre et le suivi se fassent dans les meilleures conditions.</p>
            """
        },
        {
            "category": cat_apropos,
            "title": "3. Pourquoi vérifions-nous les professeurs ?",
            "slug": "pourquoi-verifions-nous-les-professeurs",
            "keywords": "philosophie, contrôle, charte, qualité, sérieux",
            "content": """
            <h2>L'excellence par la sélection</h2>
            <p>Notre promesse aux parents est la sérénité. Sans vérification, n'importe qui pourrait s'improviser professeur de mathématiques, au risque de détruire le niveau d'un enfant au lieu de l'améliorer.</p>
            <p>La vérification est le cœur de notre valeur ajoutée. Elle prouve notre engagement envers la qualité éducative et donne aux professeurs inscrits un véritable label de sérieux qui justifie leurs tarifs.</p>
            """
        },
        {
            "category": cat_apropos,
            "title": "4. Comment protégeons-nous les parents et les apprenants ?",
            "slug": "comment-protegeons-nous-les-parents",
            "keywords": "protection, signalement, exclusion, sécurité",
            "content": """
            <h2>Un écosystème sain et encadré</h2>
            <p>Au-delà de la vérification initiale des identités, nous protégeons notre communauté grâce à :</p>
            <ul>
                <li><strong>Un système d'évaluation (à venir) :</strong> Les parents pourront noter les professeurs, ce qui écartera naturellement les profils peu performants.</li>
                <li><strong>La séance d'essai :</strong> Qui agit comme un filet de sécurité pour s'assurer du bon comportement du professeur.</li>
                <li><strong>Un service client réactif :</strong> Prêt à intervenir et à suspendre tout compte qui ne respecterait pas notre charte éthique.</li>
            </ul>
            """
        },
        {
            "category": cat_apropos,
            "title": "5. Pourquoi proposons-nous une séance d'essai ?",
            "slug": "pourquoi-une-seance-dessai",
            "keywords": "raisonnement, essai, gratuit, logique, philosophie",
            "content": """
            <h2>Le droit de choisir librement</h2>
            <p>L'apprentissage humain est avant tout une question de "feeling" et de relation interpersonnelle. Un professeur peut être excellent sur le papier, mais sa pédagogie peut ne pas résonner avec le caractère de votre enfant.</p>
            <p>Nous imposons cette séance d'essai gratuite car elle débloque la prise de décision. Elle retire le stress financier du premier contact et permet de construire l'engagement sur des bases saines et volontaires.</p>
            """
        },
        {
            "category": cat_apropos,
            "title": "6. Qu'est-ce qu'un professeur partenaire ?",
            "slug": "quest-ce-quun-professeur-partenaire",
            "keywords": "partenaire, statut, identité, freelance, indépendant",
            "content": """
            <h2>Des indépendants valorisés</h2>
            <p>Un professeur partenaire n'est pas un employé de Prof Chez Vous. C'est un travailleur indépendant qui utilise notre plateforme pour gérer son activité de soutien scolaire.</p>
            <p>Il est maître de son emploi du temps, de sa méthode pédagogique et de sa tarification. Nous lui offrons simplement la crédibilité (via le badge certifié) et les clients (via notre trafic web).</p>
            """
        },
        {
            "category": cat_apropos,
            "title": "7. Quels sont les engagements de Prof Chez Vous ?",
            "slug": "quels-sont-les-engagements",
            "keywords": "valeurs, transparence, sécurité, qualité, éthique",
            "content": """
            <h2>Notre charte de confiance</h2>
            <p>Notre entreprise repose sur 3 piliers :</p>
            <ol>
                <li><strong>Transparence :</strong> Les tarifs affichés sont ceux qui sont appliqués. Pas de frais cachés.</li>
                <li><strong>Sécurité :</strong> Nous ne publierons jamais le profil d'un enseignant dont nous n'avons pas vérifié l'identité.</li>
                <li><strong>Soutien :</strong> Nous nous engageons à répondre rapidement à toute préoccupation d'un parent ou d'un professeur.</li>
            </ol>
            """
        },
        {
            "category": cat_apropos,
            "title": "8. Quelle est notre vision ?",
            "slug": "quelle-est-notre-vision",
            "keywords": "futur, afrique, développement, edtech, avenir",
            "content": """
            <h2>Démocratiser l'excellence éducative au Bénin et au-delà</h2>
            <p>Aujourd'hui, nous structurons le marché du soutien scolaire à domicile et en ligne au Bénin.</p>
            <p>Demain, notre vision est de devenir la plateforme EdTech de référence en Afrique francophone, en proposant non seulement des professeurs particuliers, mais aussi des outils de suivi pédagogique avancés, des classes virtuelles interactives, et des ressources d'apprentissage adaptées aux réalités de nos systèmes éducatifs.</p>
            """
        }
    ]

    # Delete all existing articles and categories first to start fresh
    Article.objects.all().delete()
    
    # We don't delete categories, just use the 3 we defined. 
    # But let's delete the unused old ones to clean up the UI
    Category.objects.exclude(slug__in=["parents", "professeurs", "a-propos"]).delete()

    for item in articles_data:
        article, created = Article.objects.update_or_create(
            slug=item["slug"],
            defaults={
                "category": item["category"],
                "title": item["title"],
                "keywords": item["keywords"],
                "content": item["content"]
            }
        )
        print(f"[{'CREATED' if created else 'UPDATED'}] {article.title}")

    print("Success! Help center populated with the 24 highly optimized articles.")

if __name__ == '__main__':
    run()
