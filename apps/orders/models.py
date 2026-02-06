from django.db import models
from apps.users.models import User
from apps.restaurants.models import Restaurant, Menu

class Cart(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='cart'
    )

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='carts'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'restaurant')

    def __str__(self):
        return f"cart of {self.user.username}"
    
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    menu_items = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
    )

    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "menu_items")
    
    def __str__(self):
        return f"{self.menu_items.name} x {self.quantity}"
    
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'pending'
        PAID = 'PAID', 'paid'
        FAILED = 'FAILED', 'failed'
        CANCELLED = 'CANCELLED', 'cancelled'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )

    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    razorpay_order_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        null=True
    )

    razorpay_payment_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"Order {self.id} | {self.user.username} | {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    menu_item = models.ForeignKey(
        Menu,
        on_delete=models.PROTECT
    )

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.PROTECT
    )

    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"