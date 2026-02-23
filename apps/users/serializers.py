from rest_framework import serializers
from django.contrib.auth import get_user_model
from .utils import generate_verification_link
from .tasks import send_user_verify_mail

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