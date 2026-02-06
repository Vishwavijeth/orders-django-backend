from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets, mixins
from django.db import transaction
from django.core.cache import cache
from rest_framework.generics import ListAPIView
from apps.orders.models import Cart, CartItem
from apps.restaurants.models import Menu
from apps.orders.serializers.carts import CartSerializer, CartListSerializer

from apps.orders.models import Order
from apps.orders.serializers.order import OrderSerializer
from .cache_keys import cart_list_cache_key


#create cart
class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request):
        items = request.data.get("items")

        if not items or not isinstance(items, list):
            return Response(
                {"detail": "items list required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        for entry in items:
            menu_id = entry.get("menu_id")
            action = entry.get("action")

            if not menu_id or action not in ("increase", "decrease"):
                return Response(
                    {"detail": "menu_id and valid action required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            menu = Menu.objects.select_related("restaurant").filter(
                id=menu_id,
                is_available=True
            ).first()

            if not menu:
                return Response(
                    {"detail": f"Invalid or unavailable menu_id {menu_id}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart, _ = Cart.objects.get_or_create(
                user=request.user,
                restaurant=menu.restaurant
            )

            cart_item = CartItem.objects.filter(
                cart=cart,
                menu_items=menu
            ).first()

            if action == "increase":
                if cart_item:
                    cart_item.quantity += 1
                    cart_item.save()
                else:
                    CartItem.objects.create(
                        cart=cart,
                        menu_items=menu,
                        quantity=1
                    )

            elif action == "decrease":
                if not cart_item:
                    return Response(
                        {"detail": "Cannot decrease item not in cart"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if cart_item.quantity <= 1:
                    cart_item.delete()  # remove item entirely
                else:
                    cart_item.quantity -= 1
                    cart_item.save()

        carts = Cart.objects.filter(
            user=request.user
        ).prefetch_related("items__menu_items", "restaurant")

        return Response(
            CartSerializer(carts, many=True).data,
            status=status.HTTP_200_OK
        )
    
#delete cart
class CartManageViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

#list cart
class CartListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartListSerializer

    def list(self, request, *args, **kwargs):
        cache_key = cart_list_cache_key(request.user.id)

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        queryset = Cart.objects.filter(
            user=request.user
        ).prefetch_related(
            "items__menu_items",
            "restaurant"
        )

        data = self.get_serializer(queryset, many=True).data
        cache.set(cache_key, data, timeout=300)  # 5 min

        return Response(data)
    
#list all orders
class OrderListView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related("items__menu_item", "items__restaurant")
            .order_by("-created_at")
        )