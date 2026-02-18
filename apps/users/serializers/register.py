from rest_framework.serializers import ModelSerializer
from apps.users.models import User


class UserRegisterModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "role"
        ]