from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from core.models import Like
from core.utils import process_image

class VoteSession(models.Model):
    CATEGORY_CHOICES = [
        ('music', 'Musique'),
        ('sport', 'Sport'),
        ('beauty', 'Beauté & Miss'),
        ('education', 'Éducation'),
        ('other', 'Autre'),
    ]

    # Ownership
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vote_sessions', null=True, blank=True, verbose_name="Créateur")
    
    title = models.CharField(max_length=200, verbose_name="Titre du vote")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name="Description")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name="Catégorie")
    background_image = models.ImageField(upload_to='votes/backgrounds/', verbose_name="Image d'arrière-plan")
    
    organizer_name = models.CharField(max_length=100, default="Haram", verbose_name="Organisateur")
    organizer_image = models.ImageField(upload_to='votes/organizers/', blank=True, null=True, verbose_name="Image de l'organisateur")
    is_verified = models.BooleanField(default=False, verbose_name="Vérifié")
    
    vote_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prix d'un vote (FCFA)")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de fin du vote")
    
    # Generic relations
    core_like = GenericRelation(Like, related_query_name='%(app_label)s_%(class)s_likes')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Session de Vote"
        verbose_name_plural = "Sessions de Vote"
        
    def __str__(self):
        return self.title
        
    @property
    def is_expired(self):
        from django.utils import timezone
        if self.end_date:
            return timezone.now() > self.end_date
        return False

    def clean(self):
        super().clean()
        if self.vote_price > 0 and self.vote_price < 100:
            raise ValidationError({
                'vote_price': "Le montant d'un vote doit être de 0 (gratuit) ou au minimum 100 FCFA."
            })

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            
        # Image processing
        if self.pk:
            try:
                old_instance = VoteSession.objects.get(pk=self.pk)
                if self.background_image and self.background_image != old_instance.background_image:
                    process_image(self.background_image)
                if self.organizer_image and self.organizer_image != old_instance.organizer_image:
                    process_image(self.organizer_image)
            except VoteSession.DoesNotExist:
                pass
        else:
            if self.background_image:
                process_image(self.background_image)
            if self.organizer_image:
                process_image(self.organizer_image)

        self.full_clean()
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('vote_detail', kwargs={'slug': self.slug})

class Choice(models.Model):
    session = models.ForeignKey(VoteSession, on_delete=models.CASCADE, related_name='choices', verbose_name="Session de vote")
    name = models.CharField(max_length=100, verbose_name="Nom de l'option")
    image = models.ImageField(upload_to='votes/choices/', verbose_name="Image d'illustration")
    description = models.TextField(blank=True, verbose_name="Description")
    vote_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de votes")
    
    # Generic relations
    core_like = GenericRelation(Like, related_query_name='%(app_label)s_%(class)s_likes')

    def save(self, *args, **kwargs):
        # Image processing
        if self.pk:
            try:
                old_instance = Choice.objects.get(pk=self.pk)
                if self.image and self.image != old_instance.image:
                    process_image(self.image)
            except Choice.DoesNotExist:
                pass
        else:
            if self.image:
                process_image(self.image)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.session.title})"

class VoteRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
    ]
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name='votes', verbose_name="Choix")
    voter_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nom du votant")
    voter_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone du votant")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant payé (si applicable)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed', verbose_name="Statut")
    openpay_transaction_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="ID Transaction OpenPay")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['choice', 'ip_address']),
            models.Index(fields=['openpay_transaction_id']),
        ]

    def __str__(self):
        return f"Vote pour {self.choice.name} - {self.status}"
