import os
import django
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.core.exceptions import ObjectDoesNotExist
print(issubclass(ObjectDoesNotExist, AttributeError))
