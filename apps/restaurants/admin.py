from django.contrib import admin
from .models.coupon import Coupon, CouponUsage
from django.db import models

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

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "coupon",
        "order",
        "user_coupon_usage_count",  # ✅ NEW
        "used_at",
    )

    list_filter = (
        "coupon",
        "used_at",
    )

    search_fields = (
        "user__email",
        "user__phone",
        "coupon__code",
        "order__id",
    )

    readonly_fields = ("used_at",)

    # 🔥 annotate counts efficiently
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            user_coupon_count=models.Count(
                "user__coupon_usages",
                filter=models.Q(
                    user__coupon_usages__coupon=models.F("coupon")
                ),
            )
        )

    # ✅ display column
    def user_coupon_usage_count(self, obj):
        return obj.user_coupon_count

    user_coupon_usage_count.short_description = "User Usage Count"