from django.db import models
from apps.users.models import User

class Restaurant(models.Model):
    name = models.CharField(max_length=40, db_index=True)
    description = models.CharField(max_length=50, blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="restaurants"
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Menu(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="menu_items"
    )

    name = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['restaurant', 'is_available'])
        ]
    
    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"