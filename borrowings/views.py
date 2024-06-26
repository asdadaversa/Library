import datetime

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError

from borrowings.models import Borrowing
from books.models import Book
from borrowings.serializers import (
    BorrowingReadSerializer,
    BorrowingCreateSerializer
)
from payments.views import PaymentViewSet


class ListCreateBorrowingView(APIView):
    serializer_class = BorrowingReadSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "is_active",
                type=OpenApiTypes.STR,
                description="Filter borrowings by actual_return_date__isnull=True (ex. ?is_active=True)",
            ),
            OpenApiParameter(
                "user_id",
                type=OpenApiTypes.STR,
                description="Filter borrowings by user_id, only for admin (ex. ?user_id=1)",
            ),
        ]
    )
    def get(self, request, format=None):
        is_active = request.query_params.get("is_active")
        user_id = request.query_params.get("user_id")
        queryset = Borrowing.objects.select_related(
            "book", "user"
        ).prefetch_related("payments")

        if request.user.is_staff:
            borrowings = queryset
        else:
            borrowings = Borrowing.objects.filter(user=self.request.user)

        if is_active:
            borrowings = borrowings.filter(actual_return_date__isnull=True)

        if request.user.is_staff and user_id:
            borrowings = borrowings.filter(user__id=user_id)

        serializer = BorrowingReadSerializer(
            borrowings, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = BorrowingCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DetailBorrowingView(APIView):
    """ APIVIEW for detail endpoint for Borrowing """
    permission_classes = [IsAuthenticated]
    serializer_class = BorrowingReadSerializer

    def get(self, request, pk, format=None):
        borrowings = get_object_or_404(Borrowing, pk=pk)
        serializer = BorrowingReadSerializer(borrowings)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReturnBorrowingView(APIView):
    """ APIVIEW for list and detail endpoint for Borrowing """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        borrowings = get_object_or_404(Borrowing, pk=pk)
        serializer = BorrowingReadSerializer(borrowings)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        today_date = datetime.date.today()
        pk = self.kwargs.get("pk")
        try:
            borrowings = get_object_or_404(Borrowing, pk=pk)
            if not borrowings.actual_return_date:
                borrowings.actual_return_date = today_date
                borrowings.save()
                book = get_object_or_404(Book, pk=borrowings.book.id)
                book.inventory += 1
                book.save()
                if (
                        borrowings.actual_return_date
                        > borrowings.expected_return_date
                ):
                    payment = PaymentViewSet()
                    payment.create_payment_session(request, borrowings)
                return Response(
                    f"The book: {book.title} returned, now actual return day "
                    f"is {borrowings.actual_return_date}, "
                    f"book inventory {book.inventory}"
                )
            else:
                return Response("The book already returned")
        except IntegrityError as msg:
            return Response(f"error: {msg}")
