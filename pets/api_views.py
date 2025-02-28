from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Pet, Breed, AdoptionApplication
from .serializers import (
    PetSerializer, 
    BreedSerializer,
    AdoptionApplicationSerializer,
    UserSerializer
)

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners to edit their objects.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.owner == request.user

class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Pet.objects.all()
        status = self.request.query_params.get('status', None)
        species = self.request.query_params.get('species', None)
        
        if status is not None:
            queryset = queryset.filter(status=status)
        if species is not None:
            queryset = queryset.filter(breed__species=species)
            
        return queryset
    
    def perform_create(self, serializer):
        """
        Set the owner automatically when creating a pet.
        """
        serializer.save(owner=self.request.user)

class BreedViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Breed.objects.all()
    serializer_class = BreedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Breed.objects.all()
        species = self.request.query_params.get('species', None)
        
        if species is not None:
            queryset = queryset.filter(species=species)
            
        return queryset

class AdoptionApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = AdoptionApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return AdoptionApplication.objects.all()
        return AdoptionApplication.objects.filter(user=user)
    
    def perform_create(self, serializer):
        application = serializer.save(user=self.request.user)
        
        pet = application.pet
        pet.status = 'pending'
        pet.save()
        
        return application
    
    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        application = self.get_object()
        
        if application.user != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'You do not have permission to withdraw this application.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        if application.application_status != 'pending':
            return Response(
                {'detail': 'Only pending applications can be withdrawn.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        application.application_status = 'withdrawn'
        application.save()
        
        pet = application.pet
        pet.status = 'available'
        pet.save()
        
        return Response({'detail': 'Application withdrawn successfully.'})

class UserRegistrationViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'detail': 'User registered successfully.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 