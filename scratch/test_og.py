import os
import sys
import django
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.templatetags.image_utils import cloudinary_og

url = "https://res.cloudinary.com/demo/image/upload/v1234567890/sample.jpg"
print("Original:", url)
print("OG transformed:", cloudinary_og(url))
