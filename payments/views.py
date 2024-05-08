import stripe
import datetime

from django.http import JsonResponse
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.reverse import reverse
from rest_framework_simplejwt.authentication import JWTAuthentication

from library_service import settings
from payments.serializers import PaymentSerializer
from borrowings.models import Borrowing
from payments.models import Payment, PaymentStatus, PaymentType


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        else:
            return Payment.objects.filter(borrowing__user=self.request.user)

    def create_payment_session(self, request, borrowing: Borrowing):
        try:
            stripe.api_key = settings.STRIPE_API_KEY
            today = datetime.date.today()
            overdue = (
                    borrowing.actual_return_date
                    and borrowing.actual_return_date
                    > borrowing.expected_return_date
            )
            overdue_days = (
                (
                        borrowing.actual_return_date
                        - borrowing.expected_return_date
                ).days
            )

            fine_multiplier = 2
            if overdue:
                total_bill = (
                        (
                                borrowing.actual_return_date
                                - borrowing.expected_return_date
                        ).days
                        * borrowing.book.daily_fee * fine_multiplier
                )
                type = PaymentType.FINE.value

            else:
                total_bill = (
                        (borrowing.expected_return_date - today).days
                        * borrowing.book.daily_fee
                )
                type = PaymentType.PAYMENT.value

            product = stripe.Product.create(
                name=borrowing,
                description=f"As you are overdue your "
                            f"return it is a fine pyment, "
                            f"$overdue days*2 (days: {overdue_days})"
            )

            price = stripe.Price.create(
                unit_amount=int(total_bill * 100),
                currency="usd",
                product=product.id,
                recurring=None,
                metadata={"description": "Price entered by customer (USD)"},
            )

            success_url = request.build_absolute_uri(
                reverse("payments:success")
            ) + "?session_id={CHECKOUT_SESSION_ID}"

            cancel_url = request.build_absolute_uri(reverse("payments:cancel"))

            session = stripe.checkout.Session.create(
                success_url=success_url,
                cancel_url=cancel_url,
                line_items=[{"price": price.id, "quantity": 1}],
                mode="payment",
            )

            payment = Payment.objects.create(
                borrowing=borrowing,
                status=PaymentStatus.PENDING.value,
                type=type,
                session_url=session.url,
                session=session.id,
                money_to_pay=total_bill
            )
            return payment
        except Exception as e:
            return JsonResponse({"error": str(e)}, safe=False)


@api_view(["GET"])
def success_payment(request,  pk=None):
    stripe.api_key = settings.STRIPE_API_KEY

    session_id = request.GET.get('session_id')
    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status == "paid":
        payment = Payment.objects.get(session=session_id)
        payment.status = PaymentStatus.PAID.value
        payment.save()
        return JsonResponse(
            {"message": f"Thank for your order! Session id: {session_id}"}
        )
    else:
        return JsonResponse({"message": "Payment failed"})


@api_view(["GET"])
def cancel_payment(request):
    return JsonResponse(
        {"message": "Payment can be paid later, "
                    "session available for 24 hours"}
    )
