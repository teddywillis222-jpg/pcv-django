from django.contrib import admin
from .models import (
    TeacherProfile,
    Profile,
    ParentDetails,
    Enfant,
    Engagement,
    Conversation,
    Message,
    ProfessorAnnouncement,
    Apprenant,
    Abonnement,
    Evaluation
)

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'statut_de_validation', 'ville_quartier')
    list_filter = ('statut_de_validation', 'matiere_enseignee')
    search_fields = ('nom', 'prenom', 'matiere_enseignee', 'ville_quartier')

@admin.register(ProfessorAnnouncement)
class ProfessorAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = ('title', 'message')

@admin.register(Engagement)
class EngagementAdmin(admin.ModelAdmin):
    list_display = ('id', 'professeur', 'parent_apprenant', 'statut_general', 'date_creation')
    list_filter = ('statut_general', 'type_engagement')
    search_fields = ('professeur__nom', 'parent_apprenant__username')

# Enregistrement simple pour les autres modèles
admin.site.register(Profile)
admin.site.register(ParentDetails)
admin.site.register(Enfant)
admin.site.register(Apprenant)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Abonnement)
admin.site.register(Evaluation)
