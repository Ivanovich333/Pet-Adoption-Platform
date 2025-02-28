from rest_framework.routers import DefaultRouter
from .api_views import (
    PetViewSet,
    BreedViewSet,
    AdoptionApplicationViewSet,
    UserRegistrationViewSet
)

router = DefaultRouter()
router.register(r'pets', PetViewSet, basename='pet')
router.register(r'breeds', BreedViewSet, basename='breed')
router.register(r'applications', AdoptionApplicationViewSet, basename='application')
router.register(r'users', UserRegistrationViewSet, basename='user')

urlpatterns = router.urls 