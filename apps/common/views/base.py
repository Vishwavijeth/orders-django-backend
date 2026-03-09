from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.status import is_success
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, NotFound

from ..config import API_RESPONSE_ACTION_CODES

class NonAuthenticatedAPIMixin:
    permission_classes = [permissions.AllowAny]

class AppViewMixin:
    def get_request(self):
        return self.request
    
    def get_user(self):
        return self.get_request().user
    
    def get_authenticated_user(self):
        user = self.get_user()
        return user if user.is_authenticated else None
    
    def send_error_response(self, data=None, status_code=None):
        return self.send_response(data=data, status_code=status_code or status.HTTP_400_BAD_REQUEST)
    
    @staticmethod
    def send_response(data=None, status_code=status.HTTP_200_OK, action_code="DO NOTHING", **other_response_data):
        return Response(
            data = {
                "data": data,
                "status": "success" if is_success(status_code) else "error",
                "action_code": action_code,
                **other_response_data
            },
            status=status_code
        )
    
    def get_app_response_schema(self, response: Response, **kwargs):
        return self.send_response(data=response.data, status_code=response.status_code, **kwargs)
    
    def handle_exception(self, exc):

        action_code = API_RESPONSE_ACTION_CODES["display_error_1"]
        if exc and hasattr(exc, "status_code") and exc.status_code in [401]:
            action_code = "AUTH_TOKEN_NOT_PROVIDED_OR_INVALID"
        return self.get_app_response_schema(super().handle_exception(exc), action_code=action_code)


class SortingMixin(AppViewMixin):
    def get_queryset(self):
        return self.get_sorted_queryset(super().get_queryset())
    
    def get_sorted_queryset(self, queryset):
        if sort_by := self.get_request().query_params.getlist("sort_by"):
            try:
                queryset = queryset.order_by(*sort_by)
            except Exception:
                raise ValidationError("invalid field name for sorting")
        return queryset
    
    def get_default_sorting_options(self):
        return {
            "-created" : "Created (newest first)",
            "created" : "Created (oldest first)"
        }
    
    def get_sorting_meta(self, sorting_options: dict):
        return [{"id": key, "identity": value} for key, value in sorting_options.items()]
    
    def get_sorting_options(self, specific_options={}):
        options = self.get_default_sorting_options().copy()
        options.update(specific_options)
        return self.get_sorting_meta(options)
    
class AppAPIView(SortingMixin, APIView):
    sync_action_class = None
    get_object_model = None
    serializer_class = None

    def get_serializer_class(self):
        return self.serializer_class
    
    def get_valid_serializer(self, instance=None, data=None, context=None, **kwargs):
        assert self.get_serializer_class()

        if not data:
            data = self.request.data
        if not context:
            context = self.get_serializer_context()

        serializer = self.get_serializer_class()(data=data, context=context, instance=instance, **kwargs)
        serializer.is_valid(raise_exception=True)
        return serializer
    
    def get_serializer_context(self):
        return {"request" : self.get_request(), "view" : self}
    
    def adopt_sync_action_class(self, instance):
        assert self.sync_action_class

        success, result = self.sync_action_class(instance=instance, request=self.get_request()).execute()

        if success:
            return self.send_response(data=result)
        return self.send_error_response(data=result)
    
    def get_object(self, exception=NotFound, identifier="pk"):
        if self.get_object_model:
            _object = self.get_object_model.objects.get_or_none(**{identifier: self.kwargs[identifier]})

            if not _object:
                raise exception
            return _object
        
    def choices_for_meta(self, choices: list):

        from apps.common.helpers import get_display_name_for_slug

        return [{"id": _, "identity": get_display_name_for_slug(_)} for _ in choices]