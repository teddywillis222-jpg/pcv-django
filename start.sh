#!/usr/bin/env bash
# Start script pour Render - Prof Chez Vous

set -e

echo "Démarrage de Prof Chez Vous..."

# Migration de la base de données (sécurité pour Render)
python manage.py migrate --noinput

# Démarrage avec Gunicorn sur le port dynamique de Render
# Render utilise la variable d'environnement $PORT
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
