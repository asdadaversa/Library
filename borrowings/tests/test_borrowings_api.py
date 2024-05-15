import datetime
import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from books.models import Book, CoverType
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingReadSerializer

BORROWINGS_URL = reverse("borrowings:borrowings")

book_payload = {
        "title": "Psarnya",
        "author": "Pinokio",
        "cover": CoverType.SOFT.value,
        "inventory": 100,
        "daily_fee": 2
    }


def sample_book(**params):
    defaults = book_payload
    defaults.update(params)

    return Book.objects.create(**defaults)


def detail_url(borrowings_id):
    return reverse("borrowings:borrowings-detail", args=[borrowings_id])


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


class BorrowingNoAdminApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass",
            first_name="Anton",
            last_name="Pes",
        )
        self.client.force_authenticate(self.user)

    def test_list_borrowings(self):
        sample_borrowing(user=self.user)
        sample_borrowing(user=self.user)
        res = self.client.get(BORROWINGS_URL)

        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_borrowings_detail(self):
        borrowing = sample_borrowing()

        url = detail_url(borrowing.id)
        res = self.client.get(url)

        serializer = BorrowingReadSerializer(borrowing)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_borrowing(self):
        book = sample_book()
        time_now = datetime.datetime.now().date()
        expected_days = time_now + timedelta(days=3)
        payload = {
            "expected_return_date": expected_days,
            "book": book.id,
            "user": self.user
        }
        res = self.client.post(BORROWINGS_URL, payload)
        borrowing = Borrowing.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            if key == "book":
                self.assertEqual(payload[key], getattr(borrowing, key).id)
            else:
                self.assertEqual(payload[key], getattr(borrowing, key))

    def test_put_borrowing_not_allowed(self):
        borrowing = sample_borrowing()

        url = detail_url(borrowing.id)
        res = self.client.put(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_borrowing_not_allowed(self):
        borrowing = sample_borrowing()

        url = detail_url(borrowing.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class AdminBorrowingsApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_admin_user_can_see_all_queryset(self):
        sample_borrowing(user=self.user)
        sample_borrowing(user=self.user)
        sample_borrowing(user=self.user)

        res = self.client.get(BORROWINGS_URL)
        self.assertEqual(len(res.data), 3)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        payments = Borrowing.objects.all()
        serializer = BorrowingReadSerializer(payments, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_filter_by_is_active(self):
        time_now = datetime.datetime.now().date()
        actual_return_day = time_now + timedelta(days=5)
        expected_return_date = time_now + timedelta(days=10)

        sample_borrowing(
            user=self.user,
            expected_return_date=actual_return_day,
            actual_return_date=expected_return_date
        )
        sample_borrowing(
            user=self.user,
            expected_return_date=expected_return_date,
            actual_return_date=actual_return_day
        )
        sample_borrowing(user=self.user)
        sample_borrowing(user=self.user)

        response = self.client.get(BORROWINGS_URL, {"is_active": "True"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        response = self.client.get(BORROWINGS_URL, {"is_active": "False"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_user_id(self):
        other_user = get_user_model().objects.create_user(
            email="other@example.com",
            password="testpass"
        )
        sample_borrowing(user=self.user)
        sample_borrowing(user=self.user)
        sample_borrowing(user=self.user)
        sample_borrowing(user=other_user)
        sample_borrowing(user=other_user)

        response = self.client.get(BORROWINGS_URL, {"user_id": self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        response = self.client.get(BORROWINGS_URL, {"user_id": other_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
