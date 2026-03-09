from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework import filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from apps.common.views.base import SortingMixin
from apps.common.serializers import AppModelSerializer, simple_serialize_queryset

class AppGenericViewSet(GenericViewSet):

    allowed_roles = []
    allow_all = False

    def get_allowed_roles(self):
        return self.allowed_roles

class AppModelListAPIViewSet(
    SortingMixin,
    ListModelMixin,
    AppGenericViewSet
):
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = []
    search_fields = []
    ordering_fields = "__all__"

    all_table_columns = {}

    @action(
        methods=["GET"],
        url_path="table-meta",
        detail=False,
    )
    def get_meta_for_table_handlers(self, *args, **kwargs):
        return self.send_response(data=self.get_meta_for_table())
    
    def get_meta_for_table(self) -> dict:
        serializer_class = self.get_serializer_class()
        return {
            "columns": self.get_table_columns(),
            "filter_data": (
                serializer_class(context=self.get_serializer_context()).get_filter_meta() if serializer_class else {}
            ),
            "sort_by": self.get_sorting_options(),
        }
    
    def get_table_columns(self) -> dict:
        return self.all_table_columns
    
    def serializer_for_filter(self, queryset, fields=None):
        if not fields:
            fields = ["id", "identity"]

        return simple_serialize_queryset(queryset=queryset, fields=fields)
    
    def serializer_choices(self, choices: list):
        from apps.common.helpers import get_display_name_for_slug

        return [{"id": _, "identity": get_display_name_for_slug(_)} for _ in choices]