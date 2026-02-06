from django.shortcuts import render
from rest_framework import generics, permissions, status
from django.http import HttpResponse
from .serializers import RegisterSerializer, UsersListSerializer, DeleteUserSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

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
    
    return HttpResponse("invalid or expired link", status=400)


class UsersListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UsersListSerializer
    permission_classes = [permissions.AllowAny]

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        serializer = DeleteUserSerializer(data={"id": id})
        serializer.is_valid(raise_exception=True)
        serializer.delete()

        return Response(
            {"detail": "User deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
