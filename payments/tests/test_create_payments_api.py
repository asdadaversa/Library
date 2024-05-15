import datetime
import uuid

from datetime import timedelta
from unittest.mock import MagicMock
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from books.models import Book, CoverType
from borrowings.models import Borrowing
from payments.models import Payment, PaymentStatus, PaymentType
from payments.serializers import PaymentSerializer
from payments.views import PaymentViewSet


def sample_book(**params):
    defaults = {
        "title": "Psarnya",
        "author": "Pinokio",
        "cover": CoverType.SOFT.value,
        "inventory": 100,
        "daily_fee": 2
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


def sample_borrowing(**params):
    book = sample_book()
    user = get_user_model().objects.create_user(
        email="test-{}@test.com".format(uuid.uuid4().hex[:8]),
        password="testpass",
        first_name="Anton",
        last_name="Pes"
    )
    time_now = datetime.datetime.now().date()
    expected_days = time_now + timedelta(days=3)
    defaults = {
        "borrow_date": time_now,
        "expected_return_date": expected_days,
        "book": book,
        "user": user
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)


PAYMENTS_URL = reverse("payments:payments-list")


def detail_url(payment_id):
    return reverse("payments:payments-detail", args=[payment_id])


def sample_payment(**params):
    borrowing = sample_borrowing()
    defaults = {
            "borrowing": borrowing,
            "status": PaymentStatus.PENDING.value,
            "type": PaymentType.PAYMENT.value,
            "session_url": "example.com/session-url",
            "session": "example-session-id",
            "money_to_pay": 100
        }
    defaults.update(params)
    return Payment.objects.create(**defaults)


class PaymentsNoAdminApiTests(TestCase):
    def setUp(self) -> None:
        email = "test-{}@test.com".format(uuid.uuid4().hex[:8])
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            f"{email}", "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_get_payments_list(self):
        borrowing1 = sample_borrowing(user=self.user)
        borrowing2 = sample_borrowing(user=self.user)
        sample_payment(borrowing=borrowing1)
        sample_payment(borrowing=borrowing2)

        res = self.client.get(PAYMENTS_URL)

        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(serializer.data))

    def test_retrieve_payments_detail(self):
        borrowing = sample_borrowing(user=self.user)
        payment = sample_payment(borrowing=borrowing)

        url = detail_url(payment.id)
        res = self.client.get(url)

        serializer = PaymentSerializer(payment, context={"request": None})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_payment_method_not_allowed(self):
        borrowing = sample_borrowing()
        payload = {
            "borrowing": borrowing,
            "status": PaymentStatus.PENDING.value,
            "type": PaymentType.PAYMENT.value,
            "session_url": "example.com/session-url",
            "session": "example-session-id",
            "money_to_pay": 100
        }
        res = self.client.post(PAYMENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_payment_method_not_allowed(self):
        borrowing = sample_borrowing(user=self.user)
        payment = sample_payment(borrowing=borrowing)
        payload = {
            "borrowing": borrowing,
            "status": PaymentStatus.PENDING.value,
            "type": PaymentType.PAYMENT.value,
            "session_url": "example.com/session-url",
            "session": "example-session-id",
            "money_to_pay": 200
        }

        url = detail_url(payment.id)

        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_payment_method_not_allowed(self):
        borrowing = sample_borrowing(user=self.user)
        payment = sample_payment(borrowing=borrowing)
        url = detail_url(payment.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class AdminPaymentApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_admin_user_can_see_all_queryset(self):
        borrowing1 = sample_borrowing()
        sample_payment(borrowing=borrowing1)
        borrowing2 = sample_borrowing()
        sample_payment(borrowing=borrowing2)

        res = self.client.get(PAYMENTS_URL)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        self.assertEqual(res.data, serializer.data)


class CreatePaymentSessionTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.borrowing = sample_borrowing()

    def test_create_payment_session(self):
        request = MagicMock()
        borrowing = MagicMock()
        payment_viewset = PaymentViewSet()
        response = payment_viewset.create_payment_session(request, borrowing)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
