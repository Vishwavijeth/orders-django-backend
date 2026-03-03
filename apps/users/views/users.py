from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from ..serializers.users import UserCUDModelSerializer

User = get_user_model()


class UserCUDModelViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserCUDModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    http_method_names = ["post", "put", "patch", "delete"]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(
            {"detail": "User deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )