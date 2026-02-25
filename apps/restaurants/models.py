from django.db import models
from apps.users.models import User

class Restaurant(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="restaurants")
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="menu_items")
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['restaurant', 'is_available'])
        ]

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"
    
class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        FLAT = "FLAT", "Flat"
        PERCENTAGE = "PERCENTAGE", "Percentage"

    code = models.CharField(max_length=20, unique=True, db_index=True)
    description = models.CharField(max_length=100, blank=True)

    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)

    max_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    restaurant_specific = models.ManyToManyField(
        Restaurant, 
        blank=True,
        related_name="specific_coupons"
    )

    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True, db_index=True)

    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)

    created_at = models.DateField(auto_now_add=True)

    def is_global(self):
        return not self.restaurant_specific.exists()
    
    def __str__(self):
        return self.code