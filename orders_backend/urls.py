from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import(
    TokenRefreshView, 
    TokenObtainPairView,
)
from apps.users.views import RegisterView
from django.http import HttpResponse


def home(request):
    return HttpResponse("Django app is running!")

urlpatterns = [
    path("", home),  # <- root route
    path("admin/", admin.site.urls),

    path('api/register/', RegisterView.as_view()),
    path('api/login/', TokenObtainPairView.as_view()),
    path('api/refresh/', TokenRefreshView.as_view()),

    path('api/', include('apps.restaurants.urls')),
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.orders.urls')),
    path('api/', include('apps.payments.urls')),
]
