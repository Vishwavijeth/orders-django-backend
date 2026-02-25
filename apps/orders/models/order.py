from django.db import models
from apps.users.models import User
from apps.restaurants.models.restaurant import Restaurant, Menu
from .cart import Cart
from apps.payments.models import Payment
from apps.restaurants.models.coupon import Coupon

class Order(models.Model):
    class Status(models.TextChoices):
        PLACED = "PLACED", "Placed"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT, related_name="orders", null=True)
    cart = models.OneToOneField(Cart, on_delete=models.SET_NULL, null=True, related_name="order")
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, related_name="order")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_applied = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLACED, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Order {self.id} ({self.user}) - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(Menu, on_delete=models.PROTECT)
    
    # Snapshots
    menu_name_snapshot = models.CharField(max_length=100, null=True)
    price_snapshot = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.menu_name_snapshot} x {self.quantity}"