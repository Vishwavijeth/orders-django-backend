from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from django.db import transaction
import razorpay

from apps.payments.models import Payment

from apps.orders.models import Cart, Order
from apps.restaurants.models import Coupon
from .tasks import create_orders_from_payment
from .utils import get_carts_total

import json
import hmac
import hashlib
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

class CreatePaymentLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart_ids = request.data.get("cart_ids", [])
        coupon_id = request.data.get("coupon_id")

        # ✅ Fetch carts
        carts = Cart.objects.filter(
            id__in=cart_ids,
            user=request.user,
            status=Cart.Status.ACTIVE,
        ).prefetch_related("items", "restaurant")

        if not carts.exists():
            return Response({"detail": "No valid carts selected"}, status=400)

        # ✅ original total
        total_amount = get_carts_total(carts)

        # defaults
        final_payable_amount = total_amount
        discount_applied = Decimal("0.00")
        coupon = None

        # ------------------------------------------------
        # ✅ APPLY COUPON (ONLY HERE)
        # ------------------------------------------------
        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id, is_active=True)
            except Coupon.DoesNotExist:
                return Response({"detail": "Invalid coupon"}, status=400)

            now = timezone.now()

            if coupon.valid_from and coupon.valid_from > now:
                return Response({"detail": "Coupon not yet valid"}, status=400)

            if coupon.valid_to and coupon.valid_to < now:
                return Response({"detail": "Coupon expired"}, status=400)

            # FLAT
            if coupon.discount_type == Coupon.DiscountType.FLAT:
                discount_applied = min(coupon.discount_value, total_amount)
                final_payable_amount = total_amount - discount_applied

            # PERCENTAGE
            elif coupon.discount_type == Coupon.DiscountType.PERCENTAGE:
                total_discount = Decimal("0.00")

                for cart in carts:
                    for item in cart.items.all():
                        item_total = item.price_snapshot * item.quantity
                        item_discount = (
                            item_total * coupon.discount_value / Decimal("100.00")
                        ).quantize(Decimal("0.01"))
                        total_discount += item_discount

                discount_applied = min(
                    total_discount,
                    coupon.max_discount_amount or total_amount,
                )
                final_payable_amount = total_amount - discount_applied

        # ------------------------------------------------
        # ✅ CREATE RAZORPAY LINK (PAY WHAT USER SEES)
        # ------------------------------------------------
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        link = client.payment_link.create(
            {
                "amount": int(final_payable_amount * 100),
                "currency": "INR",
                "description": "Food Order Payment",
                "customer": {"email": request.user.email},
            }
        )

        # ------------------------------------------------
        # ✅ SAVE PAYMENT (WITH COUPON REFERENCE)
        # ------------------------------------------------
        payment = Payment.objects.create(
            amount=final_payable_amount,
            coupon=coupon if coupon else None,
            payment_id=link["id"],
            payment_link=link["short_url"],
        )
        payment.carts.set(carts)

        # ------------------------------------------------
        # ✅ RESPONSE (debug friendly)
        # ------------------------------------------------
        return Response(
            {
                "payment_id": payment.id,
                "payment_link": payment.payment_link,
                "original_amount": float(total_amount),
                "discounted_amount": float(final_payable_amount),
                "final_payable_amount": float(final_payable_amount),
                "discount_applied": float(discount_applied),
                "coupon_code": coupon.code if coupon else None,
            }
        )

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

    expected = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature or "", expected):
        return HttpResponse(status=400)

    data = json.loads(payload)

    if data.get("event") != "payment_link.paid":
        return HttpResponse(status=200)

    link_id = data["payload"]["payment_link"]["entity"]["id"]

    with transaction.atomic():
        payment = Payment.objects.select_for_update().get(payment_id=link_id)

        # ✅ idempotent protection
        if payment.status != Payment.Status.SUCCESS:
            payment.status = Payment.Status.SUCCESS
            payment.save(update_fields=["status"])

            # trigger ONLY once
            create_orders_from_payment.delay(payment.id)

    return HttpResponse(status=200)
