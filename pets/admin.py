from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
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
    list_display = ('pet', 'user', 'application_status', 'created_at', 'view_application_details', 'action_buttons')
    list_filter = ('application_status', 'created_at', 'pet__breed__species')
    search_fields = ('pet__name', 'user__username', 'user__email', 'reason')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'application_details')
    fieldsets = (
        ('Application Information', {
            'fields': ('user', 'pet', 'application_status', 'created_at', 'updated_at')
        }),
        ('Applicant Details', {
            'fields': ('application_details',)
        }),
        ('Application Content', {
            'fields': ('reason', 'home_type', 'has_yard', 'other_pets')
        }),
    )
    
    def application_details(self, obj):
        """Display formatted application details for admin view."""
        return format_html(
            '<strong>Applied by:</strong> {} ({})<br/>'
            '<strong>Pet:</strong> {} ({})<br/>'
            '<strong>Applied on:</strong> {}<br/>'
            '<strong>Current Status:</strong> {}<br/>',
            obj.user.username,
            obj.user.email,
            obj.pet.name,
            obj.pet.breed,
            obj.created_at.strftime('%Y-%m-%d %H:%M'),
            obj.get_application_status_display()
        )
    
    def view_application_details(self, obj):
        """Add a link to view the application details."""
        url = reverse('admin:pets_adoptionapplication_change', args=[obj.id])
        return format_html('<a href="{}">View Details</a>', url)
    view_application_details.short_description = 'Details'
    
    def action_buttons(self, obj):
        """Display action buttons for pending applications."""
        if obj.application_status != 'pending':
            return format_html('<span class="text-muted">No actions available</span>')
        
        approve_url = reverse('admin_approve_application', args=[obj.id])
        reject_url = reverse('admin_reject_application', args=[obj.id])
        
        return format_html(
            '<a class="button" href="{}">Approve</a> '
            '<a class="button" style="background-color: #ba2121;" href="{}">Reject</a>',
            approve_url, reject_url
        )
    action_buttons.short_description = 'Actions'
