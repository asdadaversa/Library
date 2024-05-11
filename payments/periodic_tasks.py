import datetime
import stripe

from celery import shared_task
from library_service import settings
from payments.models import Payment, PaymentStatus


@shared_task
def check_session_for_expiration():
    stripe.api_key = settings.STRIPE_API_KEY
    payments = Payment.objects.filter(status=PaymentStatus.PENDING.value)
    for payment in payments:
        try:
            session = stripe.checkout.Session.retrieve(payment.session)
            if session.status == "expired":
                payment.status = PaymentStatus.EXPIRED.value
                payment.save()
        except Exception as e:
            print(str(e))
            continue
