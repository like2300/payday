from django.contrib import admin
from .models import VoteSession, Candidate, VoteRecord

@admin.register(VoteSession)
class VoteSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer_name', 'vote_price', 'is_active', 'is_verified', 'created_at')
    list_filter = ('is_active', 'is_verified')
    search_fields = ('title', 'description', 'organizer_name')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'background_image', 'is_active')
        }),
        ('Organisateur', {
            'fields': ('organizer_name', 'organizer_image', 'is_verified')
        }),
        ('Paramètres de Vote', {
            'fields': ('vote_price',)
        }),
    )

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'session', 'vote_count')
    list_filter = ('session',)
    search_fields = ('name',)

@admin.register(VoteRecord)
class VoteRecordAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'voter_name', 'amount_paid', 'created_at')
    list_filter = ('candidate__session', 'candidate')
    search_fields = ('voter_name', 'voter_phone')
