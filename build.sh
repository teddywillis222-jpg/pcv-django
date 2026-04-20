#!/usr/bin/env bash
# Build script pour Render - Prof Chez Vous

set -e

echo "Début du build Prof Chez Vous..."

# Installation des dépendances
pip install -r requirements.txt

# Collecte des fichiers statiques
python manage.py collectstatic --noinput

# Exécution des migrations de base de données
python manage.py migrate

# Vérification de la configuration
python manage.py check

echo "Build terminé avec succès !"
