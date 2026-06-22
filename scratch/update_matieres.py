import json
import unicodedata
import os

def normalize(text):
    return unicodedata.normalize('NFKD', text.lower()).encode('ASCII', 'ignore').decode('utf-8')

file_path = r"C:\Users\JGA'TIC BENIN\Documents\ProfChezVous\core\matieres.json"
with open(file_path, "r", encoding="utf-8") as f:
    matieres = json.load(f)

existing_normalized = {normalize(m): m for m in matieres}

new_matieres_raw = """
Algèbre linéaire
Analyse numérique
Analyse réelle
Anthropologie
Architecture des ordinateurs
Audit comptable
Audit financier
Automatisme industriel
Biologie moléculaire
Biostatistiques
Cartographie
Communication
Communication digitale
Comptabilité des sociétés
Comptabilité publique
Comptabilité bancaire
Cryptographie
Cybersécurité
Data Science
Dessin assisté par ordinateur (DAO)
Django
Droit des obligations
Droit international
Droit du travail
Droit fiscal
Droit immobilier
Droit social
Écologie
Électricité bâtiment
Électrotechnique
Embryologie
Entrepreneuriat
Espagnol conversationnel
Espagnol professionnel
Esthétique
Finance d'entreprise
Finance publique
Génie civil
Génie électrique
Génie logiciel
Génie mécanique
Gestion de projet
Gestion des stocks
Gestion logistique
Gouvernance des entreprises
Grec
Hébreu
Hydraulique
Infographie
Ingénierie logicielle
Intelligence artificielle
Java EE
Journalisme et communication
Laravel
Leadership
Linux avancé
Machine Learning
Maintenance électronique
Maintenance industrielle
Management
Management stratégique
Marketing digital
Mathématiques financières
Mathématiques discrètes
Mathématiques appliquées
Mécanique des fluides
Médecine générale
Microbiologie
Montage vidéo
MySQL
Neurosciences
Node.js
Nutrition et diététique
PAO
Pathologie
Pédiatrie
Pharmacologie
Photoshop
Physique appliquée
Préparation BEPC
Préparation BAC
Préparation concours ENS
Préparation concours ENAM
Préparation concours FAST
Préparation concours FASEG
Préparation IELTS
Préparation SAT
Préparation TOEFL
Probabilités avancées
Programmation orientée objet
Programmation Java
Programmation PHP
Programmation C#
Programmation Kotlin
Programmation Flutter
Psychologie de l'enfant
Psychologie de l'éducation
Psychopédagogie
React
Recherche scientifique
Rédaction scientifique
Réseaux et télécommunications
Robotique
Sciences politiques
Sciences sociales
Sécurité informatique
SEO
Sociologie
SPSS
SQL
Statistiques appliquées
Statistiques inférentielles
Systèmes d'exploitation
Théorie des graphes
Théorie des probabilités
Traitement d'images
UI/UX Design
Urbanisme
VBA Excel
Vue.js
WordPress
Zootechnie
""".strip().split('\n')

added_count = 0
for m in new_matieres_raw:
    m = m.strip()
    if not m:
        continue
    norm = normalize(m)
    if norm not in existing_normalized:
        matieres.append(m)
        existing_normalized[norm] = m
        added_count += 1
    else:
        print(f"Skipped '{m}' (already exists as '{existing_normalized[norm]}')")

matieres.sort()

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(matieres, f, ensure_ascii=False, indent=4)

print(f"Added {added_count} new matieres.")
