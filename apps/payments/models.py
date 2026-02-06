from django.db import models

class Payment(models.Model):
    class Status(models.TextChoices):
        INITIATED = "INITIATED"
        SUCCESS = "SUCCESS"
        FAILED = "FAILED"

    carts = models.ManyToManyField(
        "orders.Cart",
        related_name="payment"
    )

    provider = models.CharField(max_length=20, default="razorpay")
    razorpay_payment_link_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    payment_link = models.URLField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INITIATED
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
