from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.orders.views import CartViewSet, OrderListView, GenerateOrderReportAPIView

router = DefaultRouter()
router.register('cart', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
    path("orders/", OrderListView.as_view()),
    path("orders/report/", GenerateOrderReportAPIView.as_view()),
]