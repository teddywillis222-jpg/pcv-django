from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.conf import settings
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
    Evaluation,
    Diplome,
)


# ──────────────────────────────────────────────
# Filtres personnalisés
# ──────────────────────────────────────────────

class IsTestAccountFilter(admin.SimpleListFilter):
    """Filtre pour identifier les comptes de test définis dans TEST_ACCOUNT_EMAILS."""
    title = 'Compte de test'
    parameter_name = 'is_test_account'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Comptes de test'),
            ('no', 'Vrais comptes'),
        )

    def queryset(self, request, queryset):
        test_emails = getattr(settings, 'TEST_ACCOUNT_EMAILS', [])
        if isinstance(test_emails, str):
            test_emails = [e.strip() for e in test_emails.split(',')]
        if self.value() == 'yes':
            return queryset.filter(email__in=test_emails)
        if self.value() == 'no':
            return queryset.exclude(email__in=test_emails)
        return queryset


# ──────────────────────────────────────────────
# Custom User Admin (remplace celui par défaut)
# ──────────────────────────────────────────────

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profil'
    fk_name = 'user'


def delete_users_and_cascade(modeladmin, request, queryset):
    """Supprime les utilisateurs sélectionnés ET toutes leurs données en cascade."""
    # Protection : ne pas supprimer les superutilisateurs
    safe_qs = queryset.filter(is_superuser=False)
    count, details = safe_qs.delete()
    modeladmin.message_user(
        request,
        f"✅ {count} objet(s) supprimé(s) en cascade "
        f"({', '.join(f'{v} {k}' for k, v in details.items())})"
    )

delete_users_and_cascade.short_description = "🗑️ Supprimer les comptes sélectionnés + toutes les données"


# Désenregistrer le User par défaut, puis le réenregistrer avec notre version
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined', 'is_test_badge')
    list_filter = (IsTestAccountFilter, 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    inlines = [ProfileInline]
    actions = [delete_users_and_cascade]

    @admin.display(description='Test ?', boolean=True)
    def is_test_badge(self, obj):
        test_emails = getattr(settings, 'TEST_ACCOUNT_EMAILS', [])
        if isinstance(test_emails, str):
            test_emails = [e.strip() for e in test_emails.split(',')]
        return obj.email in test_emails


# ──────────────────────────────────────────────
# TeacherProfile Admin amélioré
# ──────────────────────────────────────────────

def delete_teacher_profiles_and_users(modeladmin, request, queryset):
    """Supprime les profils profs sélectionnés + les comptes User associés (cascade totale)."""
    user_ids = queryset.values_list('user_id', flat=True)
    from django.contrib.auth.models import User as UserModel
    safe_users = UserModel.objects.filter(id__in=user_ids, is_superuser=False)
    count, details = safe_users.delete()
    modeladmin.message_user(
        request,
        f"✅ {count} objet(s) supprimé(s) en cascade "
        f"({', '.join(f'{v} {k}' for k, v in details.items())})"
    )

delete_teacher_profiles_and_users.short_description = "🗑️ Supprimer profils + comptes utilisateurs associés"


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'user_email', 'statut_de_validation', 'ville_quartier', 'user_date_joined')
    list_filter = ('statut_de_validation', 'matiere_enseignee')
    search_fields = ('nom', 'prenom', 'matiere_enseignee', 'ville_quartier', 'user__email')
    ordering = ('-user__date_joined',)
    actions = [delete_teacher_profiles_and_users]

    @admin.display(description='Email', ordering='user__email')
    def user_email(self, obj):
        return obj.user.email if obj.user else '—'

    @admin.display(description='Inscrit le', ordering='user__date_joined')
    def user_date_joined(self, obj):
        return obj.user.date_joined.strftime('%d/%m/%Y') if obj.user else '—'


# ──────────────────────────────────────────────
# Autres modèles
# ──────────────────────────────────────────────

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

@admin.register(Diplome)
class DiplomeAdmin(admin.ModelAdmin):
    list_display = ('nom_diplome', 'teacher', 'date_upload')
    search_fields = ('nom_diplome', 'teacher__nom')

# Enregistrement simple pour les autres modèles
admin.site.register(Profile)
admin.site.register(ParentDetails)
admin.site.register(Enfant)
admin.site.register(Apprenant)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Abonnement)
admin.site.register(Evaluation)

from .models import RessourceProfesseur, FAQProfesseur

@admin.register(RessourceProfesseur)
class RessourceProfesseurAdmin(admin.ModelAdmin):
    list_display = ('titre', 'est_guide_officiel', 'ordre_affichage', 'actif', 'date_creation')
    list_editable = ('est_guide_officiel', 'ordre_affichage', 'actif')
    list_filter = ('actif', 'est_guide_officiel')
    search_fields = ('titre', 'description')

@admin.register(FAQProfesseur)
class FAQProfesseurAdmin(admin.ModelAdmin):
    list_display = ('question', 'ordre_affichage', 'actif')
    list_editable = ('ordre_affichage', 'actif')
    list_filter = ('actif',)
    search_fields = ('question', 'reponse')


from .models import SearchAlert

@admin.register(SearchAlert)
class SearchAlertAdmin(admin.ModelAdmin):
    list_display = ('matiere', 'localisation', 'contact_info', 'resolved', 'created_at')
    list_filter = ('resolved', 'created_at')
    search_fields = ('matiere', 'localisation', 'contact_info')
    list_editable = ('resolved',)


