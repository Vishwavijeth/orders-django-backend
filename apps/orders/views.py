from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, mixins, generics
from rest_framework.views import APIView
from django.db import transaction
from django.conf import settings
from apps.orders.models import Cart, CartItem
from apps.restaurants.models import Menu
from apps.orders.serializers.carts import CartSerializer, CartListSerializer

from apps.orders.models import Order
from apps.orders.serializers.order import OrderSerializer
from .tasks import generate_order_report_task


#create cart
class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request):
        items = request.data.get("items")

        for entry in items:
            menu_id = entry["menu_id"]
            action = entry["action"]

            menu = Menu.objects.select_related("restaurant").filter(
                id=menu_id,
                is_available=True
            ).first()

            if not menu:
                return Response({"detail": "Invalid menu"}, status=400)

            cart, _ = Cart.objects.get_or_create(
                user=request.user,
                restaurant=menu.restaurant,
                status=Cart.Status.ACTIVE
            )

            cart_item = CartItem.objects.filter(
                cart=cart,
                menu_item=menu
            ).first()

            if action == "increase":
                if cart_item:
                    cart_item.quantity += 1
                    cart_item.save()
                else:
                    CartItem.objects.create(
                        cart=cart,
                        menu_item=menu,
                        menu_name_snapshot=menu.name,
                        price_snapshot=menu.price,
                        quantity=1
                    )

            elif action == "decrease":
                if not cart_item:
                    continue
                if cart_item.quantity <= 1:
                    cart_item.delete()
                else:
                    cart_item.quantity -= 1
                    cart_item.save()

        carts = Cart.objects.filter(
            user=request.user,
            status=Cart.Status.ACTIVE
        ).prefetch_related("items")

        return Response(CartSerializer(carts, many=True).data)

    
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
        # cache_key = cart_list_cache_key(request.user.id)

        # cached_data = cache.get(cache_key)
        # if cached_data:
        #     return Response(cached_data)

        queryset = Cart.objects.filter(
            user=request.user,
            status=Cart.Status.ACTIVE 
        ).prefetch_related(
            "items__menu_item",
            "restaurant"
        )

        data = self.get_serializer(queryset, many=True).data
        # cache.set(cache_key, data, timeout=300)

        return Response(data)

    
#list all orders
class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .select_related("restaurant", "payment")   # FK → select_related
            .prefetch_related("items__menu_item")      # Reverse FK → prefetch
            .order_by("-created_at")
        )
    
class GenerateOrderReportAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        task = generate_order_report_task.delay()

        file_url = request.build_absolute_uri(
            settings.MEDIA_URL + "order_details_report.xlsx"
        )

        return Response({
            "message": "report generation started",
            "task id": task.id,
            "file_url": file_url
        })