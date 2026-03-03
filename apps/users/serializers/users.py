from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..utils import generate_verification_link
from ..tasks import send_user_verify_mail

User = get_user_model()

class UserCUDModelSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "phone_number",
            "role"
        ]
        read_only_fields = ["id"]

    def validate_email(self, email):
        email = email.lower()

        if self.instance:
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError("email already exists")
        else:
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError("email already exists")
        return email
    
    def validate(self, attrs):
        if not self.instance:
            if not attrs.get("password"):
                raise serializers.ValidationError("password is required")
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop("password")

        request = self.context.get("request")

        user = self.context.create_user(
            **validated_data,
            is_active=False,
            is_email_verified=False
        )
        user.set_password(password)
        user.save()

        verification_link = generate_verification_link(user, request)
        send_user_verify_mail.delay(verification_link, user.email)
    
        return user