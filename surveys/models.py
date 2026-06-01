from django.db import models
from django.conf import settings
from django.utils.text import slugify
from core.models import Fundraiser
from votes.models import VoteSession

class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('completed', 'Finalisé'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='withdrawals')
    
    # Can be linked to a fundraiser OR a vote session
    fundraiser = models.ForeignKey(Fundraiser, on_delete=models.SET_NULL, null=True, blank=True, related_name='withdrawals')
    vote_session = models.ForeignKey(VoteSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='withdrawals')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant à retirer")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    reference_number = models.CharField(max_length=20, unique=True, blank=True)
    
    # Reason for rejection
    rejection_reason = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            import random
            import string
            self.reference_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Retrait {self.reference_number} - {self.user.email}"

    class Meta:
        verbose_name = "Demande de retrait"
        verbose_name_plural = "Demandes de retrait"
        ordering = ['-created_at']

class PlatformRule(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre de la règle")
    content = models.TextField(verbose_name="Contenu de la règle")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Règle de la plateforme"
        verbose_name_plural = "Règles de la plateforme"
        ordering = ['order', 'title']

    def __str__(self):
        return self.title
