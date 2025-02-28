from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Pet, Breed, AdoptionApplication

class BreedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Breed
        fields = ['id', 'name', 'species', 'description']

class PetSerializer(serializers.ModelSerializer):
    breed = BreedSerializer(read_only=True)
    breed_id = serializers.PrimaryKeyRelatedField(
        queryset=Breed.objects.all(), 
        source='breed',
        write_only=True
    )
    
    class Meta:
        model = Pet
        fields = [
            'id', 'name', 'age', 'breed', 'breed_id', 'description', 
            'status', 'image', 'date_added', 'owner'
        ]
        read_only_fields = ['owner', 'date_added']

class AdoptionApplicationSerializer(serializers.ModelSerializer):
    pet_name = serializers.CharField(source='pet.name', read_only=True)
    applicant_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AdoptionApplication
        fields = [
            'id', 'user', 'pet', 'pet_name', 'applicant_username',
            'application_status', 'created_at', 'updated_at',
            'reason', 'home_type', 'has_yard', 'other_pets'
        ]
        read_only_fields = ['created_at', 'updated_at', 'application_status']
        
    def validate_pet(self, value):
        """
        Check that the pet is available for adoption.
        """
        if value.status != 'available':
            raise serializers.ValidationError('This pet is not available for adoption.')
        return value

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']
        
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        return user 