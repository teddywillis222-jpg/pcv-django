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

# 3. Application des migrations à la base de données
echo "Application des migrations..."
python manage.py migrate --noinput

# 5. Vérification finale
echo "Vérification de la configuration Django..."
python manage.py check

echo "--- Build terminé avec succès ! ---"