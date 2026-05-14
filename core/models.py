from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator

class Fundraiser(models.Model):
    CATEGORY_CHOICES = [
        ('birthday', 'Anniversaire'),
        ('wedding', 'Mariage'),
        ('graduation', 'Diplômation'),
    ]
    
    MEDIA_TYPE_CHOICES = [
        ('video', 'Vidéo'),
        ('image', 'Image'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name="Description")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='birthday', verbose_name="Catégorie")
    beneficiary_name = models.CharField(max_length=100, verbose_name="Nom du bénéficiaire")
    beneficiary_phone = models.CharField(max_length=20, verbose_name="Téléphone du bénéficiaire")
    
    # Media
    background_media = models.FileField(upload_to='fundraisers/backgrounds/', verbose_name="Média d'arrière-plan")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image', verbose_name="Type de média")
    thumbnail = models.ImageField(upload_to='fundraisers/thumbnails/', null=True, blank=True, verbose_name="Vignette (pour vidéo)")
    
    # Customization
    button_text = models.CharField(max_length=100, default="Contribuer", verbose_name="Texte du bouton")
    button_color = models.CharField(max_length=7, default="#FF6B6B", verbose_name="Couleur du bouton (Hex)")
    min_donation_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=500, 
        validators=[MinValueValidator(100)],
        verbose_name="Montant minimum (FCFA)"
    )
    
    # Collection Data
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Objectif (FCFA - Optionnel)")
    collected_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Collecté (FCFA)")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Collecte"
        verbose_name_plural = "Collectes"
        
    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('fundraiser_detail', kwargs={'slug': self.slug})
    
    def get_progress_percentage(self):
        if self.target_amount <= 0 or not self.target_amount:
            return 0
        percentage = (self.collected_amount / self.target_amount) * 100
        return min(float(percentage), 100.0)

    @property
    def is_closed(self):
        return self.target_amount and self.collected_amount >= self.target_amount

    def completed_transactions_count(self):
        return self.transactions.filter(status='completed').count()

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complétée'),
        ('failed', 'Échouée'),
        ('cancelled', 'Annulée'),
    ]
    
    PROVIDER_CHOICES = [
        ('MTN', 'MTN Mobile Money'),
        ('AIRTEL', 'Airtel Money'),
    ]
    
    fundraiser = models.ForeignKey(Fundraiser, on_delete=models.CASCADE, related_name='transactions', verbose_name="Collecte")
    
    # Payment Data
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant")
    donor_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Téléphone du donateur")
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES, verbose_name="Opérateur")
    
    # OpenPay Tracking
    openpay_transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name="ID Transaction OpenPay")
    openpay_link = models.URLField(null=True, blank=True, verbose_name="Lien de paiement")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    error_message = models.TextField(null=True, blank=True, verbose_name="Message d'erreur")
    
    # Additional Data
    donor_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Nom du donateur")
    message = models.TextField(null=True, blank=True, verbose_name="Message de vœux")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        indexes = [
            models.Index(fields=['fundraiser', 'status']),
            models.Index(fields=['openpay_transaction_id']),
        ]

    def __str__(self):
        return f"Transaction {self.id} - {self.amount} FCFA"

class FundraiserSettings(models.Model):
    fundraiser = models.OneToOneField(Fundraiser, on_delete=models.CASCADE, related_name='settings')
    
    # Payment parameters
    auto_update_amount = models.BooleanField(default=True, verbose_name="Mise à jour automatique")
    currency = models.CharField(max_length=10, default='XAF', verbose_name="Devise")
    
    # Notifications
    send_notification_email = models.BooleanField(default=True, verbose_name="Envoyer notification email")
    notification_email = models.EmailField(blank=True, null=True, verbose_name="Email de notification")
    
    # Status
    allow_donations = models.BooleanField(default=True, verbose_name="Autoriser les dons")
    show_donor_list = models.BooleanField(default=False, verbose_name="Afficher la liste des donateurs")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres de collecte"
        verbose_name_plural = "Paramètres de collectes"
