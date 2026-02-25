from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework.views import APIView
from django.conf import settings

from apps.orders.models.order import Order
from apps.orders.serializers.order import OrderSerializer
from ..tasks import generate_order_report_task

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