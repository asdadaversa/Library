import stripe
import datetime
from library_service import settings

from borrowings.models import Borrowing
from payments.models import Payment, PaymentStatus, PaymentType


def create_payment_session(borrowing: Borrowing):
    today = datetime.date.today()

    stripe.api_key = settings.STRIPE_API_KEY
    total_bill = (
            (borrowing.expected_return_date - today).days
            * borrowing.book.daily_fee
    )

    product = stripe.Product.create(
        name=borrowing
    )

    price = stripe.Price.create(
        unit_amount=int(total_bill * 100),
        currency="usd",
        product=product.id,
        recurring=None,
        metadata={"description": "Price entered by customer (USD)"},
    )

    session = stripe.checkout.Session.create(
        success_url="https://google.com/success",
        cancel_url="https://example.com/cancel",
        line_items=[{"price": price.id, "quantity": 1}],
        mode="payment",
    )
    payment = Payment.objects.create(
        borrowing=borrowing,
        status=PaymentStatus.PENDING.value,
        type=PaymentType.PAYMENT.value,
        session_url=session.url,
        session=session.id,
        money_to_pay=total_bill
    )
    return payment
