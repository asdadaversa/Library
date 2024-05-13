from rest_framework import serializers
from django.db import IntegrityError

from borrowings.tasks import send_borrowing_notification
from borrowings.models import Borrowing
from books.serializers import BookSerializer
from books.models import Book
from payments.serializers import PaymentSerializer
from payments.views import PaymentViewSet
from users.models import User
from payments.models import PaymentStatus


class BorrowingReadSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True, many=False)
    payments = PaymentSerializer(read_only=True, many=True)

    class Meta:
        model = Borrowing
        fields = "__all__"


class BorrowingCreateSerializer(serializers.ModelSerializer):
    book_detail_info = BookSerializer(
        source="book", read_only=True, many=False
    )

    class Meta:
        model = Borrowing
        fields = "__all__"
        read_only_fields = ("actual_return_date", "user", "book_detail_info", )

    def create(self, validated_data):
        expected_return_date = validated_data["expected_return_date"]

        book_id = validated_data["book"].id
        book = Book.objects.get(id=book_id)
        user_id = self.context["request"].user.id
        user = User.objects.get(id=user_id)

        user_pending_payments = user.borrowings.select_related(
            "book", "user").filter(
            payments__status=PaymentStatus.PENDING.value
        ).first()
        if user_pending_payments:
            raise serializers.ValidationError(
                "Can't create an order. You already have pending payment.")

        if book.inventory > 0:
            try:
                book.inventory -= 1
                book.save()
                borrowing = Borrowing.objects.create(
                    expected_return_date=expected_return_date,
                    book=book,
                    user=user
                )

                request = self.context["request"]
                payment = PaymentViewSet()
                payment.create_payment_session(request, borrowing)
                send_borrowing_notification.apply_async(args=[borrowing.id])

                return borrowing

            except IntegrityError as msg:
                raise serializers.ValidationError(f"error: {msg}")
        else:
            raise serializers.ValidationError(
                "There are no free books now, inventory is 0"
            )
