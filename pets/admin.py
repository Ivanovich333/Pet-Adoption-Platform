from django.contrib import admin
from .models import Pet, Breed, AdoptionApplication

@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ('name', 'species')
    list_filter = ('species',)
    search_fields = ('name', 'species')

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'breed', 'age', 'status', 'date_added')
    list_filter = ('status', 'breed__species')
    search_fields = ('name', 'description', 'breed__name')
    date_hierarchy = 'date_added'

@admin.register(AdoptionApplication)
class AdoptionApplicationAdmin(admin.ModelAdmin):
    list_display = ('pet', 'user', 'application_status', 'created_at')
    list_filter = ('application_status', 'created_at')
    search_fields = ('pet__name', 'user__username', 'user__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
