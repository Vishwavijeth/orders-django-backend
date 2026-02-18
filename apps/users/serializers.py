from rest_framework import serializers
from django.contrib.auth import get_user_model
from .utils import generate_verification_link
from .tasks import send_user_verify_mail

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "phone_number", "role"]

    def create(self, validated_data):
        role = validated_data.pop('role', 'CUSTOMER')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number', ''),
            role=role,
            is_active=False
        )

        request = self.context.get("request")

        verification_link = generate_verification_link(user, request)

        send_user_verify_mail.delay(verification_link, user.email)

        return user
    
class UsersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]

class DeleteUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def validate_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User not found")
        return value

    def delete(self):
        user = User.objects.get(id=self.validated_data["id"])
        user.delete()
        return user