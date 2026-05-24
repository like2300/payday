from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import VoteSession, Choice, VoteRecord
from django.utils.html import format_html
from django.urls import reverse

@admin.register(VoteSession)
class VoteSessionAdmin(ModelAdmin):
    list_display = ('title', 'category', 'organizer_name', 'vote_price', 'is_active', 'is_verified', 'view_link', 'created_at')
    list_filter = ('is_active', 'is_verified', 'category')
    search_fields = ('title', 'description', 'organizer_name')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'category', 'background_image', 'is_active')
        }),
        ('Organisateur', {
            'fields': ('organizer_name', 'organizer_image', 'is_verified')
        }),
        ('Paramètres de Vote', {
            'fields': ('vote_price',)
        }),
    )

    def view_link(self, obj):
        url = reverse('vote_detail', kwargs={'slug': obj.slug})
        return format_html(
            '<a href="{}" target="_blank" style="'
            'background-color: #6366f1; color: white; padding: 6px 14px; '
            'border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 11px;'
            '">Voir ↗</a>',
            url
        )
    view_link.short_description = 'Lien Public'

@admin.register(Choice)
class ChoiceAdmin(ModelAdmin):
    list_display = ('name', 'session', 'vote_count')
    list_filter = ('session',)
    search_fields = ('name',)

@admin.register(VoteRecord)
class VoteRecordAdmin(ModelAdmin):
    list_display = ('choice', 'voter_name', 'ip_address', 'amount_paid', 'created_at')
    list_filter = ('choice__session', 'choice')
    search_fields = ('voter_name', 'voter_phone', 'ip_address')
    readonly_fields = ('created_at',)
