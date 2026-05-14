from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import redirect
from core.models import Fundraiser, Transaction, FundraiserSettings
from unfold.admin import ModelAdmin, StackedInline

class FundraiserSettingsInline(StackedInline):
    model = FundraiserSettings
    can_delete = False
    verbose_name_plural = 'Paramètres additionnels'

@admin.register(Fundraiser)
class FundraiserAdmin(ModelAdmin):
    list_display = ['title', 'beneficiary_name', 'target_amount', 'collected_amount', 'progress_display', 'view_link', 'is_active', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['title', 'beneficiary_name', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [FundraiserSettingsInline]
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('title', 'slug', 'description', 'category')
        }),
        ('Bénéficiaire', {
            'fields': ('beneficiary_name', 'beneficiary_phone')
        }),
        ('Média d\'arrière-plan', {
            'fields': ('background_media', 'media_type', 'thumbnail'),
            'description': 'Téléchargez une vidéo ou une image qui tournera en arrière-plan.'
        }),
        ('Personnalisation du Bouton', {
            'fields': ('button_text', 'button_color'),
            'description': 'Personnalisez le message et la couleur du bouton central.'
        }),
        ('Objectif & Paiement', {
            'fields': ('target_amount', 'collected_amount', 'min_donation_amount'),
            'description': 'Laissez l\'objectif vide pour une collecte libre. Le montant minimum est imposé aux donateurs.'
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
    )

    def view_link(self, obj):
        url = reverse('fundraiser_detail', kwargs={'slug': obj.slug})
        return format_html(
            '<a href="{}" target="_blank" style="'
            'background-color: #6366f1; color: white; padding: 6px 14px; '
            'border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 11px;'
            'box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);'
            '">Voir la page ↗</a>',
            url
        )
    view_link.short_description = 'Lien Public'

    def progress_display(self, obj):
        if not obj.target_amount:
            from django.utils.safestring import mark_safe
            return mark_safe('<span style="color: #6b7280; font-style: italic;">Sans objectif</span>')
            
        progress = obj.get_progress_percentage()
        color = '#10b981' if progress >= 80 else '#f59e0b' if progress >= 40 else '#ef4444'
        return format_html(
            '<div style="width: 100px; background-color: #e5e7eb; border-radius: 4px; overflow: hidden; display: flex;">'
            '<div style="width: {}px; background-color: {}; height: 10px;"></div>'
            '</div>'
            '<span style="font-size: 10px; font-weight: bold; color: {};">{}%</span>',
            int(progress), color, color, round(progress, 1)
        )
    progress_display.short_description = 'Progression'

@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display = ['id', 'fundraiser', 'donor_name', 'amount', 'status', 'provider', 'created_at']
    list_filter = ['status', 'provider', 'created_at', 'fundraiser']
    search_fields = ['donor_name', 'donor_phone', 'openpay_transaction_id']
    readonly_fields = ['id', 'created_at', 'completed_at', 'openpay_transaction_id', 'openpay_link']
    
    actions = ['export_to_excel_action']

    def export_to_excel_action(self, request, queryset):
        return redirect('admin_export_transactions')
    
    export_to_excel_action.short_description = "Exporter les transactions sélectionnées en Excel"
