from django.urls import path, include
from .views import verify_email
from rest_framework_simplejwt.views import(
    TokenRefreshView, 
    TokenObtainPairView,
)
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, verify_email


router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("verify-email/<uidb64>/<token>/", verify_email, name="verify-email"),
]