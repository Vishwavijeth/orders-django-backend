from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins
from django.db import transaction
from django.db.models.functions import Coalesce
from django.db.models import Sum, F, DecimalField, ExpressionWrapper, Value
from django.conf import settings
from apps.orders.models.cart import Cart, CartItem
from apps.restaurants.models.restaurant import Menu
from apps.orders.serializers.carts import CartSerializer

class CartViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def get_queryset(self):
        line_total = ExpressionWrapper(
            F("items__menu_item__price") * F("items__quantity"),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        )

        return (
            Cart.objects.filter(
                user=self.request.user,
                status=Cart.Status.ACTIVE,
            )
            .prefetch_related("items__menu_item", "restaurant")
            .annotate(
                subtotal=Coalesce(
                    Sum(line_total),
                    Value(0, output_field=DecimalField(max_digits=10, decimal_places=2)),
                )
            )
        )
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):

        items = request.data.get("items", [])

        if not items:
            return Response({"detail" : "items required"}, status=400)
        
        for entry in items:
            menu_id = entry.get("menu_id")
            action = entry.get("action")

            menu = (
                Menu.objects.select_related("restaurant")
                .filter(id=menu_id, is_available=True)
                .first()
            )

            if not menu:
                return Response({"detail" : "invalid menu"}, status=400)
            
            cart, _ = Cart.objects.get_or_create(
                user=request.user,
                restaurant = menu.restaurant,
                status=Cart.Status.ACTIVE
            )

            cart_item = CartItem.objects.filter(
                cart=cart,
                menu_item=menu
            ).first()

            # INCREASE
            if action == "increase":
                if cart_item:
                    cart_item.quantity += 1
                    cart_item.save(update_fields=["quantity"])
                else:
                    CartItem.objects.create(
                        cart=cart,
                        menu_item=menu,
                        menu_name_snapshot=menu.name,
                        price_snapshot=menu.price,
                        quantity=1,
                    )

            # DECREASE
            elif action == "decrease":
                if not cart_item:
                    continue

                if cart_item.quantity <= 1:
                    cart_item.delete()
                else:
                    cart_item.quantity -= 1
                    cart_item.save(update_fields=["quantity"])

        carts = self.get_queryset()
        return Response(self.get_serializer(carts, many=True).data)