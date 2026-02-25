from django.db import models
from apps.users.models import User
from apps.restaurants.models.restaurant import Restaurant, Menu

class Cart(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CHECKED_OUT = "CHECKED_OUT", "Checked Out"
        ABANDONED = "ABANDONED", "Abandoned"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts", null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="carts", null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.restaurant} - {self.status}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(Menu, on_delete=models.PROTECT, null=True)
    
    # Snapshots
    menu_name_snapshot = models.CharField(max_length=100, null=True)
    price_snapshot = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.menu_name_snapshot} x {self.quantity}"