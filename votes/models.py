from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class VoteSession(models.Model):
    CATEGORY_CHOICES = [
        ('music', 'Musique'),
        ('sport', 'Sport'),
        ('beauty', 'Beauté & Miss'),
        ('education', 'Éducation'),
        ('other', 'Autre'),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre du vote")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name="Description")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name="Catégorie")
    background_image = models.ImageField(upload_to='votes/backgrounds/', verbose_name="Image d'arrière-plan")
    
    organizer_name = models.CharField(max_length=100, default="Tosounga", verbose_name="Organisateur")
    organizer_image = models.ImageField(upload_to='votes/organizers/', blank=True, null=True, verbose_name="Image de l'organisateur")
    is_verified = models.BooleanField(default=False, verbose_name="Vérifié")
    
    vote_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prix d'un vote (FCFA)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Session de Vote"
        verbose_name_plural = "Sessions de Vote"
        
    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('vote_detail', kwargs={'slug': self.slug})

class Candidate(models.Model):
    session = models.ForeignKey(VoteSession, on_delete=models.CASCADE, related_name='candidates', verbose_name="Session de vote")
    name = models.CharField(max_length=100, verbose_name="Nom du candidat")
    image = models.ImageField(upload_to='votes/choices/', verbose_name="Photo du candidat")
    description = models.TextField(blank=True, verbose_name="Description/Bio")
    vote_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de votes")
    
    def __str__(self):
        return f"{self.name} ({self.session.title})"

class VoteRecord(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes', verbose_name="Candidat")
    voter_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nom du votant")
    voter_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone du votant")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant payé (si applicable)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['candidate', 'ip_address']),
        ]

    def __str__(self):
        return f"Vote pour {self.candidate.name}"
