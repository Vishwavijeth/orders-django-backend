from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet, ListRestaurantsView, MenuViewSet, ListAllAvailableMenuView

router = DefaultRouter()
router.register('restaurants', RestaurantViewSet, basename='restaurant')
router.register('add-menu', MenuViewSet, basename='menu')

urlpatterns = [
    path('', include(router.urls)),
    path('list-restaurants/', ListRestaurantsView.as_view(), name='restaurantslist'),
    path('menus/', ListAllAvailableMenuView.as_view(), name='menus')
]