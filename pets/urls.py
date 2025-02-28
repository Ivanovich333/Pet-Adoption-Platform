from django.urls import path
from . import views

urlpatterns = [
    path('', views.pet_list, name='pet_list'),
    path('add/', views.add_pet, name='add_pet'),
    path('<int:pet_id>/', views.pet_detail, name='pet_detail'),
    path('<int:pet_id>/adopt/', views.adopt_pet, name='adopt_pet'),
    path('<int:pet_id>/edit/', views.edit_pet, name='edit_pet'),
    path('<int:pet_id>/delete/', views.delete_pet, name='delete_pet'),
    
    path('applications/', views.admin_applications_list, name='admin_applications'),
    path('applications/<int:application_id>/approve/', views.admin_approve_application, name='admin_approve_application'),
    path('applications/<int:application_id>/reject/', views.admin_reject_application, name='admin_reject_application'),
] 