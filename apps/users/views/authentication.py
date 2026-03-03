from django.shortcuts import render
from rest_framework import  permissions, status, serializers
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.views import APIView
from ..serializers.authentication import UserSerializer, LoginSerializer, LoginResponseSerializer
from ..helpers import OAuth2TokenHelper
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework.response import Response


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

class LoginAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        response_serializer = LoginResponseSerializer(user)

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )
    
class RefreshTokenAPIView(APIView):
    permission_classes = []
    
    class _Serializer(serializers.Serializer):
        refresh_token = serializers.CharField()

    serializer_class = _Serializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh_token"]

        try:
            token_response = OAuth2TokenHelper().refresh_access_token(
                refresh_token_str=refresh_token
            )
        except Exception:
            return Response(
                {"detail" : "invalid or expired refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(token_response, status=status.HTTP_200_OK)