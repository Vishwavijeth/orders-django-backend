from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.authentication import verify_email, LoginAPIView, RefreshTokenAPIView, LogoutAPIView


router = DefaultRouter()
# router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path("login/", LoginAPIView.as_view(), name="token_obtain_pair"),
    path("refresh/", RefreshTokenAPIView.as_view(), name="token_refresh"),
    path("logout/", LogoutAPIView.as_view(), name="token_logout"),
    path("verify-email/<uidb64>/<token>/", verify_email, name="verify-email"),
]