from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER", "customer"
        RESTAURANT_ADMIN = "RESTAURANT_ADMIN", "restaurant_admin"
        ADMIN = "ADMIN", "admin"
    
    role = models.CharField(
        max_length=40,
        choices=Role.choices,
        default=Role.CUSTOMER,
        db_index=True
    )

    phone_number = models.CharField(max_length=10, blank=True)
    is_email_verified = models.BooleanField(default=False)
    
    # slug = models.SlugField(max_length=50, blank=True) 

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         # Generate slug from username
    #         self.slug = slugify(self.username)
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"

