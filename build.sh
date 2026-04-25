#!/usr/bin/env bash
# Build script optimisé pour Render - Prof Chez Vous

set -e

echo "--- Début du build Prof Chez Vous ---"

# 1. Installation des dépendances
echo "Installation des packages..."
pip install -r requirements.txt

# 2. Collecte des fichiers statiques
echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# 3. Forcer la détection des changements dans 'core' (Crucial pour ton erreur 500)
echo "Génération des migrations pour l'application core..."
python manage.py makemigrations core

# 4. Exécution des migrations générales
echo "Application des migrations à la base de données..."
python manage.py migrate

# 5. Vérification finale
echo "Vérification de la configuration Django..."
python manage.py check

echo "--- Build terminé avec succès ! ---"