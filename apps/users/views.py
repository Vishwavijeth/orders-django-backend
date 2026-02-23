from django.shortcuts import render
from rest_framework import  permissions
from django.http import HttpResponse
from rest_framework import viewsets
from .serializers import UserSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from django.contrib.auth import get_user_model
    
User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ["create", "list"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "User deleted successfully"},
            status=204
        )

def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        return HttpResponse("Invalid link", status=400)

    if default_token_generator.check_token(user, token):
        user.is_email_verified = True
        user.is_active = True
        user.save()
        return HttpResponse("Email verification successful")

    return HttpResponse("Invalid or expired link", status=400)