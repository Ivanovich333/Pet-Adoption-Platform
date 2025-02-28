from django.db import models
from django.contrib.auth.models import User

class Breed(models.Model):
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.species})"
    
    class Meta:
        ordering = ['species', 'name']

class Pet(models.Model):
    
    STATUS_CHOICES = [
        ('available', 'Available for Adoption'),
        ('pending', 'Adoption Pending'),
        ('adopted', 'Adopted'),
        ('not_available', 'Not Available'),
    ]
    
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(help_text="Age in months")
    breed = models.ForeignKey(Breed, on_delete=models.PROTECT, related_name='pets')
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    image = models.ImageField(upload_to='pets/', blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets', null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.breed}"
    
    class Meta:
        ordering = ['-date_added']

class AdoptionApplication(models.Model):
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adoption_applications')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='adoption_applications')
    application_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reason = models.TextField(help_text="Why do you want to adopt this pet?")
    home_type = models.CharField(max_length=50, help_text="Apartment, House, etc.")
    has_yard = models.BooleanField(default=False)
    other_pets = models.TextField(blank=True, help_text="List other pets you currently have, if any")
    
    def __str__(self):
        return f"Application for {self.pet.name} by {self.user.username} ({self.application_status})"
    
    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'pet'],
                condition=models.Q(application_status='pending') | models.Q(application_status='approved'),
                name='unique_active_application'
            )
        ]

    def get_application_status_display(self):
        return dict(self.STATUS_CHOICES)[self.application_status]
