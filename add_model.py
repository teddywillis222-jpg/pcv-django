import uuid

model_code = '''

import uuid
class ParentSelection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom_client_prospect = models.CharField(max_length=150, blank=True, null=True, help_text="Optionnel. Nom ou pseudo WhatsApp du parent (ex: M. Dossou).")
    professeurs = models.ManyToManyField('TeacherProfile', related_name='selections', help_text="Sélectionnez les professeurs à présenter au parent.")
    message_personnalise = models.TextField(blank=True, null=True, help_text="Optionnel. Un petit mot d'introduction affiché en haut de la page.")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sélection WhatsApp"
        verbose_name_plural = "Sélections WhatsApp"

    def __str__(self):
        nom = self.nom_client_prospect if self.nom_client_prospect else "Prospect Anonyme"
        return f"Sélection pour {nom} ({self.date_creation.strftime('%d/%m/%Y')})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('selection_personnalisee', kwargs={'uuid': str(self.id)})
'''
with open('core/models.py', 'a', encoding='utf-8') as f:
    f.write(model_code)
