from rest_framework.serializers import Serializer, ModelSerializer
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
    
# class AppModelSerializer(AppSerializer, ModelSerializer):
#     class Meta:
#         pass

# class AppWriteOnlyModelSerializer(AppModelSerializer):
#     def create(self, validated_data):
#         instance = super().create(validated_data=validated_data)

#         if hasattr(instance, 'created_by') and not instance.created_by:
#             user = self.get_user()
#             instance.created_by = user if user and user.is_authenticated else None
#             instance.save()
#         return instance
    
#     def get_validated_data(self, key=None):
#         if not key:
#             return self.validated_data
#         return self.validated_data[key]
    
#     def __init__(self, *args, **kwargs):
#         for field in self.Meta.fields:

        