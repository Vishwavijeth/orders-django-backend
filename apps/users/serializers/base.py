from rest_framework.serializers import ModelSerializer
from apps.users.models import User

class BaseUserModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "phone_number"
        ]

class SimpleUserReadOnlyModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            'email',
            "phone_number"
        ]