from rest_framework.serializers import Serializer, ModelSerializer
from apps.common.helpers import unpack_dj_choices
from rest_framework.fields import SkipField

class AppSerializer(Serializer):
    def get_initial_data(self, key, expected_type):
        _data = self.initial_data.get(key)

        if type(_data) != expected_type:
            raise SkipField()
        return _data
    
    def get_user(self):
        return self.get_request().user
    
    def get_request(self):
        return self.context.get("request", None)
    
class AppModelSerializer(AppSerializer, ModelSerializer):

    class Meta:
        pass

    def serialize_choices(self, choices: list):

        from apps.common.helpers import get_display_name_for_slug

        return [{"id": _, "identity": get_display_name_for_slug(_)} for _ in choices]

    def serialize_dj_choices(self, choices):

        return unpack_dj_choices(choices)

def simple_serialize_queryset(fields, queryset):

    if "id" in fields:
        return [{**_, "id": str(_["id"])} for _ in queryset.only(*fields).values(*fields)]
    
    return queryset.only(*fields).values(*fields)

class AppReadOnlyModelSerializer(AppModelSerializer):
    class Meta(AppModelSerializer.Meta):
        pass
    
    def create(self, validated_data):
        raise NotImplementedError
    
    def update(self, instance, validated_data):
        raise NotImplementedError

def get_app_read_only_serializer(meta_model, meta_fields=None, init_fields_config=None, queryset=None):

    if meta_fields is None:
        meta_fields = ["id", "identity"]
    
    class _Serializer(AppReadOnlyModelSerializer):
        class Meta(AppReadOnlyModelSerializer.Meta):
            model = meta_model
            fields = meta_fields

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if init_fields_config:
                for field, value in init_fields_config.items():
                    self.fields[field] = value
    
    return _Serializer
    


        