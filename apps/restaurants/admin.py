from django.contrib import admin
from .models.coupon import Coupon

# Register your models here.

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_type",
        "discount_value",
        "is_active",
        "valid_from",
        "valid_to",
    )
    list_filter = ("is_active", "discount_type")
    search_fields = ("code",)
    filter_horizontal = ("restaurant_specific",)
