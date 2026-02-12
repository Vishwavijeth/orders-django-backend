from django.contrib import admin

# Register your models here.

# apps/orders/admin.py
from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem

# Inline for Cart Items inside Cart
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('menu_name_snapshot', 'price_snapshot')
    can_delete = True

# Cart admin
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'restaurant', 'status', 'created_at')
    list_filter = ('status', 'restaurant')
    search_fields = ('user__username', 'restaurant__name')
    inlines = [CartItemInline]
    readonly_fields = ('created_at',)


# Inline for Order Items inside Order
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('menu_name_snapshot', 'price_snapshot')
    can_delete = True

# Order admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'restaurant', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'restaurant')
    search_fields = ('user__username', 'restaurant__name')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'total_amount')

