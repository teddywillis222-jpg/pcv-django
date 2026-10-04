import sys

with open('core/models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add fields to TeacherProfile
target = '    est_certifie = models.BooleanField(default=False)\n'
replacement = target + '''
    score_fiabilite = models.PositiveBigIntegerField(default=0, help_text="Total des points cumulés de fiabilité")
    date_dernier_calcul_score = models.DateTimeField(null=True, blank=True, help_text="Date de la dernière actualisation du score")
'''
content = content.replace(target, replacement)

# 2. Add OperationScoreFiabilite at the end
new_model = '''

class OperationScoreFiabilite(models.Model):
    TYPE_OPERATION_CHOICES = [
        ('JOURNAL', 'Journal de séance'),
        ('REACTIVITE', 'Réactivité'),
        ('ENGAGEMENT_TERMINE', 'Engagement terminé'),
        ('AVIS', 'Avis familial'),
        ('CORRECTION', 'Correction manuelle'),
    ]

    STATUT_CHOICES = [
        ('VALIDE', 'Valide'),
        ('NEUTRALISE', 'Neutralisé'),
        ('ANNULE', 'Annulé'),
    ]

    professeur = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='operations_fiabilite')
    type_operation = models.CharField(max_length=50, choices=TYPE_OPERATION_CHOICES)
    points = models.IntegerField(help_text="Nombre de points attribués")
    reference_type = models.CharField(max_length=100)
    reference_id = models.CharField(max_length=255)
    date_creation = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='VALIDE')
    operation_origine = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['professeur', 'type_operation', 'reference_type', 'reference_id'],
                name='unique_operation_fiabilite_per_source'
            )
        ]

    def __str__(self):
        return f"{self.professeur.user.get_full_name()} | {self.type_operation} | {self.points} pts"
'''

if 'class OperationScoreFiabilite' not in content:
    content += new_model

with open('core/models.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Modification reussie")
