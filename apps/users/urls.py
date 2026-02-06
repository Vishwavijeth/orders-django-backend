from django.urls import path
from .views import UsersListView, verify_email, DeleteUserView

urlpatterns = [
    path('userslist/', UsersListView.as_view(), name='userslist'),
    path("delete-user/<int:id>/", DeleteUserView.as_view(), name="delete-user"),

    path('verify-email/<uidb64>/<token>/', verify_email),
]
