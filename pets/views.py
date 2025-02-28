from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Pet, AdoptionApplication, Breed
from django.forms import ModelForm, widgets
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.db import models


class AdoptionApplicationForm(ModelForm):
    class Meta:
        model = AdoptionApplication
        fields = ['reason', 'home_type', 'has_yard', 'other_pets']


class PetForm(ModelForm):
    class Meta:
        model = Pet
        fields = ['name', 'age', 'breed', 'description', 'image']
        widgets = {
            'description': widgets.Textarea(attrs={'rows': 5}),
        }


def home(request):
    recent_pets = Pet.objects.filter(status='available').order_by('-date_added')[:4]
    return render(request, 'pets/home.html', {'recent_pets': recent_pets})


def pet_list(request):
    pets_list = Pet.objects.filter(status='available')
    
    species_filter = request.GET.get('species')
    breed_filter = request.GET.get('breed')
    age_filter = request.GET.get('age')
    
    if species_filter:
        pets_list = pets_list.filter(breed__species=species_filter)
    
    if breed_filter:
        pets_list = pets_list.filter(breed__id=breed_filter)
    
    if age_filter:
        if age_filter == 'puppy':
            pets_list = pets_list.filter(age__lt=12)  
        elif age_filter == 'young':
            pets_list = pets_list.filter(age__gte=12, age__lt=36)  
        elif age_filter == 'adult':
            pets_list = pets_list.filter(age__gte=36, age__lt=96)  
        elif age_filter == 'senior':
            pets_list = pets_list.filter(age__gte=96)  
    
    pets_list = pets_list.order_by('-date_added')
    
    all_species = Breed.objects.values_list('species', flat=True).distinct()
    
    all_breeds = Breed.objects.all()
    
    breeds_data = []
    for breed in all_breeds:
        breeds_data.append({
            'id': breed.id,
            'name': breed.name,
            'species': breed.species
        })
    
    paginator = Paginator(pets_list, 9)  
    page = request.GET.get('page')
    
    try:
        pets = paginator.page(page)
    except PageNotAnInteger:
        pets = paginator.page(1)
    except EmptyPage:
        pets = paginator.page(paginator.num_pages)
    
    owned_pet_ids = []
    if request.user.is_authenticated:
        owned_pet_ids = [pet.id for pet in Pet.objects.filter(owner=request.user)]
    
    context = {
        'pets': pets,
        'all_species': all_species,
        'all_breeds': all_breeds,
        'breeds_json': json.dumps(breeds_data, cls=DjangoJSONEncoder),
        'current_species': species_filter,
        'current_breed': breed_filter,
        'current_age': age_filter,
        'owned_pet_ids': owned_pet_ids,
    }
    
    return render(request, 'pets/pet_list.html', context)


def pet_detail(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    user_has_applied = False
    is_owner = False
    
    if request.user.is_authenticated:
        user_has_applied = AdoptionApplication.objects.filter(
            user=request.user, 
            pet=pet,
            application_status__in=['pending', 'approved']
        ).exists()
        is_owner = (pet.owner == request.user)
        
    context = {
        'pet': pet,
        'user_has_applied': user_has_applied,
        'is_owner': is_owner
    }
    return render(request, 'pets/pet_detail.html', context)


@login_required
def adopt_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    
    if pet.owner == request.user:
        messages.warning(request, "You cannot adopt your own pet listing.")
        return redirect('pet_detail', pet_id=pet.id)
    
    existing_application = AdoptionApplication.objects.filter(
        user=request.user, 
        pet=pet,
        application_status__in=['pending', 'approved']
    ).first()
    
    if existing_application:
        messages.info(request, 'You have already applied to adopt this pet.')
        return redirect('pet_detail', pet_id=pet.id)
    
    if request.method == 'POST':
        form = AdoptionApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.pet = pet
            application.save()
            
            pet.status = 'pending'
            pet.save()
            
            messages.success(request, 'Your adoption application has been submitted!')
            return redirect('profile')
    else:
        form = AdoptionApplicationForm()
    
    return render(request, 'pets/adopt_form.html', {'form': form, 'pet': pet})


@login_required
def add_pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.status = 'available'
            pet.owner = request.user
            pet.save()
            messages.success(request, f'Your pet {pet.name} has been listed for adoption!')
            return redirect('pet_detail', pet_id=pet.id)
    else:
        form = PetForm()
    
    return render(request, 'pets/pet_form.html', {'form': form, 'title': 'Add a Pet for Adoption'})


@login_required
def edit_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    
    if pet.owner and pet.owner != request.user:
        messages.warning(request, "You can only edit your own pet listings.")
        return redirect('pet_detail', pet_id=pet.id)

    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, f'The pet listing for {pet.name} has been updated.')
            return redirect('pet_detail', pet_id=pet.id)
    else:
        form = PetForm(instance=pet)
    
    return render(request, 'pets/pet_form.html', {'form': form, 'title': f'Edit {pet.name}'})


@login_required
def delete_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    
    if pet.owner != request.user:
        messages.warning(request, "You can only delete your own pet listings.")
        return redirect('pet_detail', pet_id=pet.id)
    
    if request.method == 'POST':
        pet_name = pet.name
        pet.delete()
        messages.success(request, f'Your pet listing for {pet_name} has been deleted.')
        return redirect('pet_list')
    
    return render(request, 'pets/pet_confirm_delete.html', {'pet': pet})


@user_passes_test(lambda u: u.is_staff)
def admin_approve_application(request, application_id):
    """
    View for administrators to approve an adoption application.
    Updates both the application status and the pet status.
    """
    application = get_object_or_404(AdoptionApplication, id=application_id)
    
    if application.application_status != 'pending':
        messages.error(request, f"Cannot approve application that is already {application.get_application_status_display()}")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/pets/adoptionapplication/'))
    
    application.application_status = 'approved'
    application.updated_at = timezone.now()
    application.save()
    
    pet = application.pet
    pet.status = 'adopted'
    pet.owner = application.user
    pet.save()
    
    other_applications = AdoptionApplication.objects.filter(
        pet=pet, 
        application_status='pending'
    ).exclude(id=application.id)
    
    for other_app in other_applications:
        other_app.application_status = 'denied'
        other_app.save()
    
    messages.success(request, f"Application for {pet.name} by {application.user.username} has been approved!")
    return redirect('admin:pets_adoptionapplication_changelist')


@user_passes_test(lambda u: u.is_staff)
def admin_reject_application(request, application_id):
    """
    View for administrators to reject an adoption application.
    """
    application = get_object_or_404(AdoptionApplication, id=application_id)
    
    if application.application_status != 'pending':
        messages.error(request, f"Cannot reject application that is already {application.get_application_status_display()}")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/pets/adoptionapplication/'))
    
    application.application_status = 'denied'
    application.updated_at = timezone.now()
    application.save()
    
    pet = application.pet
    if not AdoptionApplication.objects.filter(pet=pet, application_status='pending').exists():
        pet.status = 'available'
        pet.save()
    
    messages.success(request, f"Application for {pet.name} by {application.user.username} has been rejected.")
    return redirect('admin:pets_adoptionapplication_changelist')


@user_passes_test(lambda u: u.is_staff)
def admin_applications_list(request):
    """
    View for administrators to list and filter all adoption applications.
    Provides a more user-friendly interface than the default admin page.
    """
    status_filter = request.GET.get('status')
    search_query = request.GET.get('q')
    pet_filter = request.GET.get('pet')
    
    applications = AdoptionApplication.objects.all()
    
    if status_filter:
        applications = applications.filter(application_status=status_filter)
    
    if pet_filter:
        applications = applications.filter(pet_id=pet_filter)
    
    if search_query:
        applications = applications.filter(
            models.Q(pet__name__icontains=search_query) |
            models.Q(user__username__icontains=search_query) |
            models.Q(user__email__icontains=search_query) |
            models.Q(reason__icontains=search_query)
        )
    
    applications = applications.order_by('-created_at')
    
    paginator = Paginator(applications, 10)
    page = request.GET.get('page')
    
    try:
        applications = paginator.page(page)
    except PageNotAnInteger:
        applications = paginator.page(1)
    except EmptyPage:
        applications = paginator.page(paginator.num_pages)
    
    context = {
        'applications': applications,
        'status_filter': status_filter,
        'search_query': search_query,
        'pet_filter': pet_filter,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': applications,
    }
    
    return render(request, 'pets/admin_applications.html', context)
