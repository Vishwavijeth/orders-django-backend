from django.contrib import admin
from .models import Payment

# Register your models here.
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "amount",
        "status",
        "provider",
        "payment_id",
        "created_at",
    )
    list_filter = ("status", "provider", "created_at")
    search_fields = ("payment_id", "user__email", "user__phone")
    filter_horizontal = ("carts",)
    readonly_fields = ("created_at",)