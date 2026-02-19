from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet, MenuViewSet

router = DefaultRouter()
router.register('restaurants', RestaurantViewSet, basename='restaurant')
router.register('menu', MenuViewSet, basename='menu')

urlpatterns = [
    path('', include(router.urls)),
]