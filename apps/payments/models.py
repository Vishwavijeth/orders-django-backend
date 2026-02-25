from django.db import models

class Payment(models.Model):
    class Status(models.TextChoices):
        INITIATED = "INITIATED", "Initiated"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="payments", null=True, blank=True)
    carts = models.ManyToManyField("orders.Cart", related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIATED, db_index=True)
    provider = models.CharField(max_length=50, default="razorpay")
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    payment_link = models.URLField(null=True, blank=True)
    coupon = models.ForeignKey("restaurants.Coupon", null=True, blank=True, on_delete=models.SET_NULL, related_name="payments")
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        cart_ids = ", ".join(str(c.id) for c in self.carts.all())
        return f"Payment {self.id} (Carts: {cart_ids}) - {self.status}"

