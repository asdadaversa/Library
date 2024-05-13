import stripe
import datetime

from django.http import JsonResponse
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from library_service import settings
from payments.serializers import PaymentSerializer, PaymentRenewSerializer
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
                    and borrowing.actual_return_date > borrowing.expected_return_date
            )

            fine_multiplier = 2
            if overdue:
                overdue_days = (
                        borrowing.actual_return_date - borrowing.expected_return_date
                ).days
                total_bill = (
                        overdue_days * borrowing.book.daily_fee * fine_multiplier
                )
                type = PaymentType.FINE.value
                product_description = (
                    f"As you are overdue your "
                    f"return it is a fine pyment, "
                    f"$overdue days*2 (days: {overdue_days})"
                )
            else:
                total_bill = (
                        borrowing.expected_days * borrowing.book.daily_fee
                )
                type = PaymentType.PAYMENT.value
                product_description = "regular borrowing payment"

            product = stripe.Product.create(
                name=borrowing,
                description=product_description
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


class RenewPayment(APIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    stripe.api_key = settings.STRIPE_API_KEY

    def get(self, request, pk):
        payment = Payment.objects.get(id=pk)
        serializer = PaymentRenewSerializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk, format=None):
        payment = Payment.objects.get(id=pk)
        if payment.status != PaymentStatus.EXPIRED.value:
            return Response({"message": "payment is not expired"})
        try:
            product = stripe.Product.create(
                name=payment.borrowing,
                description="payment renew"
            )
            price = stripe.Price.create(
                unit_amount=int(payment.money_to_pay * 100),
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
            payment.status = PaymentStatus.PENDING.value
            payment.session_url = session.url
            payment.session = session.id
            payment.save()
            return Response({"message": "Payment renewed successfully"})
        except Exception as e:
            return Response({"error": str(e)})
