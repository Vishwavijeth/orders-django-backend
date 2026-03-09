from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.restaurant import RestaurantViewSet, MenuViewSet, MenuListAPIViewSet
from .views.coupon import CouponViewSet

router = DefaultRouter()
router.register('restaurants', RestaurantViewSet, basename='restaurant')
router.register('menu', MenuViewSet, basename='menu')
router.register(r"coupons", CouponViewSet, basename="coupon")
router.register("menus/listapi", MenuListAPIViewSet, basename="menuslist")

urlpatterns = [
    path('', include(router.urls)),
]