from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from pets.models import Pet, Breed, AdoptionApplication

class APITestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpassword1',
            email='testuser1@example.com'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpassword2',
            email='testuser2@example.com'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            email='admin@example.com'
        )
        
        self.breed = Breed.objects.create(
            name='Golden Retriever',
            species='Dog',
            description='Friendly family dog'
        )
        
        self.pet1 = Pet.objects.create(
            name='Buddy',
            age=24,
            breed=self.breed,
            description='Friendly golden retriever',
            status='available',
            owner=None
        )
        
        self.pet2 = Pet.objects.create(
            name='Max',
            age=12,
            breed=self.breed,
            description='Playful puppy',
            status='available',
            owner=None
        )
        
        self.client = APIClient()

class PetAPITest(APITestCase):
    def test_list_pets_unauthenticated(self):
        response = self.client.get('/api/pets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_pets_authenticated(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/pets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_create_pet_authenticated(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'Charlie',
            'age': 36,
            'breed_id': self.breed.id,
            'description': 'Friendly dog looking for a home',
            'status': 'available'
        }
        response = self.client.post('/api/pets/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Pet.objects.count(), 3)
        self.assertEqual(Pet.objects.get(name='Charlie').owner, self.user1)
    
    def test_create_pet_unauthenticated(self):
        data = {
            'name': 'Charlie',
            'age': 36,
            'breed_id': self.breed.id,
            'description': 'Friendly dog looking for a home',
            'status': 'available'
        }
        response = self.client.post('/api/pets/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Pet.objects.count(), 2)

class AdoptionApplicationAPITest(APITestCase):
    def test_create_application_authenticated(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'pet': self.pet1.id,
            'reason': 'I love dogs and have a big yard',
            'home_type': 'House',
            'has_yard': True,
            'other_pets': 'None'
        }
        response = self.client.post('/api/applications/', data)
        print("Response content:", response.content)
        print("Response status code:", response.status_code)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_application_unauthenticated(self):
        data = {
            'pet': self.pet1.id,
            'reason': 'I love dogs and have a big yard',
            'home_type': 'House',
            'has_yard': True,
            'other_pets': 'None'
        }
        response = self.client.post('/api/applications/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(AdoptionApplication.objects.count(), 0)
    
    def test_list_applications_authenticated(self):
        app1 = AdoptionApplication.objects.create(
            user=self.user1,
            pet=self.pet1,
            reason='I love dogs',
            home_type='House',
            has_yard=True
        )
        app2 = AdoptionApplication.objects.create(
            user=self.user2,
            pet=self.pet2,
            reason='Looking for a companion',
            home_type='Apartment',
            has_yard=False
        )
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/applications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], app1.id)
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/applications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_withdraw_application(self):
        app = AdoptionApplication.objects.create(
            user=self.user1,
            pet=self.pet1,
            reason='I love dogs',
            home_type='House',
            has_yard=True,
            application_status='pending'
        )
        
        self.pet1.status = 'pending'
        self.pet1.save()
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f'/api/applications/{app.id}/withdraw/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        app.refresh_from_db()
        self.assertEqual(app.application_status, 'withdrawn')
        
        self.pet1.refresh_from_db()
        self.assertEqual(self.pet1.status, 'available')

class UserRegistrationAPITest(APITestCase):
    def test_user_registration(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username='newuser').count(), 1)
        
        self.assertTrue(self.client.login(username='newuser', password='newpassword123'))
        
    def test_user_registration_duplicate_username(self):
        data = {
            'username': 'testuser1',    
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 