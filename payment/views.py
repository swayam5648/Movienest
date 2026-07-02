import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Payment
from bookings.models import Booking
from razorpay.errors import SignatureVerificationError

# Razorpay client init
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def payment_page(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    # Razorpay order create if not exists
    if not payment.razorpay_order_id:
        amount_paise = int(float(payment.amount) * 100)  # Rs → Paise
        razorpay_order = razorpay_client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "payment_capture": 1
        })
        payment.razorpay_order_id = razorpay_order["id"]
        payment.save()

    context = {
        "payment": payment,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "amount": int(float(payment.amount) * 100),
        "currency": "INR",
        "order_id": payment.razorpay_order_id,
        "prefill_name": request.user.get_full_name() or request.user.username,
        "prefill_email": request.user.email or "test@example.com",
        "prefill_contact": "9876543210",  # Test number
    }
    return render(request, "payment/payment_page.html", context)


@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        data = request.POST.dict()
        print("RAZORPAY SUCCESS DATA:", data)

        try:
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': data.get('razorpay_order_id', ''),
                'razorpay_payment_id': data.get('razorpay_payment_id', ''),
                'razorpay_signature': data.get('razorpay_signature', '')
            })
        except SignatureVerificationError:
            messages.error(request, "Payment verification failed.")
            return redirect("user_dashboard")

        payment = Payment.objects.filter(razorpay_order_id=data.get('razorpay_order_id')).first()
        if payment:
            payment.razorpay_payment_id = data.get('razorpay_payment_id')
            payment.razorpay_signature = data.get('razorpay_signature')
            payment.status = "success"
            payment.save()

            # Update booking status
            try:
                booking = payment.booking
                booking.status = "confirmed"
                booking.save()
            except Exception as e:
                print("Booking update error:", e)

            messages.success(request, "Payment successful! Booking confirmed.")
        else:
            messages.warning(request, "⚠ Payment record not found.")

        return redirect("user_dashboard")
    return redirect("user_dashboard")


@csrf_exempt
def payment_failed(request):
    print("RAZORPAY FAILED DATA:", request.POST.dict())
    messages.error(request, "Payment failed or cancelled.")
    return redirect("user_dashboard")
