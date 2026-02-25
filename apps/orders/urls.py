from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.cart import CartViewSet
from .views.order import OrderListView
from .views.report import GenerateOrderReportAPIView

router = DefaultRouter()
router.register('cart', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
    path("orders/", OrderListView.as_view()),
    path("orders/report/", GenerateOrderReportAPIView.as_view()),
]