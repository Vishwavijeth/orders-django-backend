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
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        carts = Cart.objects.filter(
            id__in=serializer.validated_data["cart_ids"],
            user=request.user
        ).prefetch_related("items__menu_items")

        if not carts.exists():
            return Response({"detail": "No valid carts found"}, status=400)

        # Calculate total amount
        total = 0
        for cart in carts:
            for item in cart.items.all():
                total += item.menu_items.price * item.quantity

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        # Create Razorpay payment link
        link = client.payment_link.create({
            "amount": int(total * 100),
            "currency": "INR",
            "description": "Food Order Payment",
            "customer": {
                "name": request.user.username,
                "email": request.user.email
            }
        })

        # Save Payment
        payment = Payment.objects.create(
            provider="razorpay",
            razorpay_payment_link_id=link["id"],
            payment_link=link["short_url"],
            amount=total
        )
        payment.carts.set(carts)

        return Response({
            "payment_id": payment.id,
            "payment_link": link["short_url"],
            "amount": total
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
    received_signature = request.headers.get("X-Razorpay-Signature")

    print("=== Razorpay Webhook Received ===")
    print("Payload:", payload.decode())
    print("Signature:", received_signature)

    secret = settings.RAZORPAY_WEBHOOK_SECRET.encode()

    expected_signature = hmac.new(
        secret,
        payload,
        hashlib.sha256
    ).hexdigest()

    if not received_signature or not hmac.compare_digest(
        received_signature, expected_signature
    ):
        print("Signature verification FAILED")
        return HttpResponse(status=400)

    print("Signature verification PASSED")

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        print("Invalid JSON")
        return HttpResponse(status=400)

    event = data.get("event")
    print("Event:", event)

    if event == "payment_link.paid":
        link_entity = data["payload"]["payment_link"]["entity"]
        link_id = link_entity["id"]

        # safer extraction
        razorpay_payment_id = (
            data.get("payload", {})
                .get("payment", {})
                .get("entity", {})
                .get("id")
        )

        try:
            payment = Payment.objects.prefetch_related(
                "carts__items__menu_items"
            ).get(razorpay_payment_link_id=link_id)
        except Payment.DoesNotExist:
            return HttpResponse(status=404)

        if payment.status == Payment.Status.SUCCESS:
            return HttpResponse(status=200)

        with transaction.atomic():
            payment.status = Payment.Status.SUCCESS
            payment.razorpay_payment_id = razorpay_payment_id
            payment.save()

        create_orders_from_payment.delay(payment.id)

        print("Payment SUCCESS → Orders created → Cart cleared")

    else:
        print("Event ignored:", event)

    print("=== Webhook Processing Complete ===\n")
    return HttpResponse(status=200)