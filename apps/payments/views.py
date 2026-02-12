from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.db import transaction
import razorpay

from apps.payments.models import Payment
from .seriallizers import  CreatePaymentSerializer

from apps.orders.models import Cart, Order
from .tasks import create_orders_from_payment

import json
import hmac
import hashlib
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

class CreatePaymentLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart_ids = request.data.get("cart_ids", [])

        carts = Cart.objects.filter(
            id__in=cart_ids,
            user=request.user,
            status=Cart.Status.ACTIVE
        ).prefetch_related("items")

        if not carts.exists():
            return Response({"detail": "No valid carts selected"}, status=400)

        total_amount = sum(
            item.price_snapshot * item.quantity
            for cart in carts
            for item in cart.items.all()
        )

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        link = client.payment_link.create({
            "amount": int(total_amount * 100),  # amount in paise
            "currency": "INR",
            "description": "Food Order Payment",
            "customer": {"email": request.user.email},
        })

        payment = Payment.objects.create(
            amount=total_amount,
            payment_id=link["id"],
            payment_link=link["short_url"]
        )
        payment.carts.set(carts)  # attach all selected carts

        return Response({
            "payment_id": payment.id,
            "payment_link": payment.payment_link,
            "amount": float(payment.amount)
        })

    
class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        payment = Payment.objects.filter(id=payment_id).first()

        if not payment:
            return Response({"detail": "Payment not found"}, status=404)

        # Authorization via Order (not cart)
        if not Order.objects.filter(payment=payment, user=request.user).exists():
            return Response({"detail": "Unauthorized"}, status=403)

        return Response({
            "payment_id": payment.id,
            "status": payment.status,
            "amount": payment.amount
        })


@csrf_exempt
def razorpay_webhook(request):
    payload = request.body
    signature = request.headers.get("X-Razorpay-Signature")
    expected = hmac.new(settings.RAZORPAY_WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature or "", expected):
        return HttpResponse(status=400)

    data = json.loads(payload)
    if data.get("event") != "payment_link.paid":
        return HttpResponse(status=200)

    link_id = data["payload"]["payment_link"]["entity"]["id"]

    with transaction.atomic():
        payment = Payment.objects.select_for_update().get(payment_id=link_id)
        if payment.status != Payment.Status.SUCCESS:
            payment.status = Payment.Status.SUCCESS
            payment.save(update_fields=["status"])

    # Trigger async task to create orders and mark carts as paid
    create_orders_from_payment.delay(payment.id)
    return HttpResponse(status=200)
