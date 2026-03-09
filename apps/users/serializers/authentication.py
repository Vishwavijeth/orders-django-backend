from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework import serializers
from ..utils import generate_verification_link
from ..tasks import send_user_verify_mail
from ..helpers import OAuth2TokenHelper

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "phone_number", "role"]

    def create(self, validated_data):
        # Default role
        role = validated_data.pop('role', 'CUSTOMER')
        password = validated_data.pop('password', None)
        
        user = User.objects.create_user(
            **validated_data,
            role=role,
            is_active=False
        )
        if password:
            user.set_password(password)
            user.save()

        # Send email verification
        request = self.context.get("request")
        verification_link = generate_verification_link(user, request)
        send_user_verify_mail.delay(verification_link, user.email)

        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email").lower()
        password = attrs.get("password")

        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError({"email": "Email not found"})

        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Invalid password"})

        if not user.is_active:
            raise serializers.ValidationError({"email": "Account inactive"})

        if not user.is_email_verified:
            raise serializers.ValidationError({"email": "Email not verified"})

        attrs["user"] = user
        return attrs
    
class LoginResponseSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "phone_number",
            "is_email_verified",
            "token",
        ]

    def get_token(self, obj):
        helper = OAuth2TokenHelper()
        token_response = helper.generate_token(user=obj)
        return token_response