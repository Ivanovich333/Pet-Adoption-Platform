from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Pet, AdoptionApplication
from django.forms import ModelForm


class AdoptionApplicationForm(ModelForm):
    class Meta:
        model = AdoptionApplication
        fields = ['reason', 'home_type', 'has_yard', 'other_pets']


def home(request):
    recent_pets = Pet.objects.filter(status='available').order_by('-date_added')[:4]
    return render(request, 'pets/home.html', {'recent_pets': recent_pets})


def pet_list(request):
    pets = Pet.objects.filter(status='available')
    return render(request, 'pets/pet_list.html', {'pets': pets})


def pet_detail(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    user_has_applied = False
    if request.user.is_authenticated:
        user_has_applied = AdoptionApplication.objects.filter(
            user=request.user, 
            pet=pet,
            application_status__in=['pending', 'approved']
        ).exists()
        
    context = {
        'pet': pet,
        'user_has_applied': user_has_applied
    }
    return render(request, 'pets/pet_detail.html', context)


@login_required
def adopt_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    
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
