from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        RESTAURANT_ADMIN = "RESTAURANT_ADMIN", "Restaurant Admin"
        ADMIN = "ADMIN", "Admin"
    
    role = models.CharField(
        max_length=40,
        choices=Role.choices,
        default=Role.CUSTOMER,
        db_index=True
    )
    phone_number = models.CharField(max_length=15, blank=True)
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"