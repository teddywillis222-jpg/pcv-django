import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.forms import TeacherProfileForm
from django.http import QueryDict

# Simulate a POST request to TeacherProfileForm
qdict = QueryDict(mutable=True)
qdict.update({
    'nom': 'Test',
    'telephone_whatsapp': '12345678',
    'ville_quartier': 'COTONOU',
    'categories_de_soutien': 'SOUTIEN_SCOLAIRE',
    'matiere_enseignee': 'MATHS',
    'modes_de_cours': 'ONLINE',
})
qdict.setlist('classes_enseignees', ['6EME', '5EME'])
qdict['tarif_classe_6EME'] = '3000'
qdict['tarif_classe_5EME'] = '3500'

form = TeacherProfileForm(data=qdict)
form.is_valid()
print("Errors:", form.errors)
print("Cleaned data classes:", form.cleaned_data.get('classes_enseignees'))
print("Cleaned tarifs:", getattr(form, 'cleaned_tarifs_par_classe', None))

