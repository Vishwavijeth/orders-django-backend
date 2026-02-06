from django.urls import path
from .views import CreatePaymentLinkView, razorpay_webhook, PaymentStatusView

urlpatterns = [
    path('create-link/', CreatePaymentLinkView.as_view()),
    path('status/<int:payment_id>/', PaymentStatusView.as_view()),
    path('webhook/', razorpay_webhook),
]