import re

with open('config/settings.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = """CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

# Configuration des Stockages (Django 5.1+)
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# --- Configuration Business (Déploiement) ---
DEFAULT_ENGAGEMENT_PRICE = os.getenv('ENGAGEMENT_PRICE', '2000')
DEFAULT_CURRENCY = os.getenv('CURRENCY', 'FCFA')

# Paramètres de notation par défaut
RATING_DEFAULT_CERTIFIED"""

new_content = re.sub(
    r'CLOUDINARY_STORAGE\s*=\s*\{[\s\S]*?RATING_DEFAULT_CERTIFIED',
    replacement,
    content
)

# Also let's clean up the double newlines globally as it ruins the file.
new_content = re.sub(r'\n\s*\n\s*\n', '\n\n', new_content)

with open('config/settings.py', 'w', encoding='utf-8', newline='') as f:
    f.write(new_content)
    
print("Settings fixed.")
