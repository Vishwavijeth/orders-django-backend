from django.db import models

# Create your models here.

COMMON_CHAR_FIELD_MAX_LENGTH = 512

COMMON_NULLABLE_FIELD_CONFIG = {
    "default": None,
    "null": True,
}

COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG = {
    **COMMON_NULLABLE_FIELD_CONFIG,
    "blank": True, 
}

class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    
