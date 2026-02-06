import razorpay
from django.conf import settings

client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

def create_razorpay_order(amount):
    return client.order.create({
        "amount" : int(amount * 100),
        "currency" : "INR",
        "payment_capture" : 1
    })