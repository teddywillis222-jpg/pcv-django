from django.contrib import admin
from .models import ReferralProgram, Ambassador, Referral, Reward

@admin.register(ReferralProgram)
class ReferralProgramAdmin(admin.ModelAdmin):
    list_display = ('current_reward_amount', 'enabled', 'terms_version')

@admin.register(Ambassador)
class AmbassadorAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at')
    search_fields = ('user__username', 'user__email', 'code')

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referral_code', 'referrer', 'referred_teacher', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('referral_code', 'referrer__username', 'referrer__email', 'referred_teacher__username')
    readonly_fields = ('visited_at', 'account_created_at', 'profile_completed_at', 'verified_at', 'reward_generated_at', 'reward_paid_at')

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('id', 'teacher', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('teacher__username', 'teacher__email', 'payment_reference')
