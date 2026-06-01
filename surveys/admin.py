from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import WithdrawalRequest, PlatformRule

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(ModelAdmin):
    list_display = ('reference_number', 'user', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('reference_number', 'user__email')
    readonly_fields = ('reference_number', 'created_at', 'updated_at')
    
    actions = ['approve_withdrawals', 'reject_withdrawals']
    
    def approve_withdrawals(self, request, queryset):
        queryset.update(status='approved')
    approve_withdrawals.short_description = "Approuver les demandes sélectionnées"
    
    def reject_withdrawals(self, request, queryset):
        queryset.update(status='rejected')
    reject_withdrawals.short_description = "Rejeter les demandes sélectionnées"

@admin.register(PlatformRule)
class PlatformRuleAdmin(ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'content')
