from rest_framework import serializers
from django.db import IntegrityError

from borrowings.tasks import send_borrowing_notification

from borrowings.models import Borrowing
from books.serializers import BookSerializer
from books.models import Book
from users.models import User


class BorrowingReadSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True, many=False)

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

        if book.inventory > 0:
            try:
                book.inventory -= 1
                book.save()
                borrowing = Borrowing.objects.create(
                    expected_return_date=expected_return_date,
                    book=book,
                    user=user
                )
                send_borrowing_notification.apply_async(args=[borrowing.id])

                return borrowing

            except IntegrityError as msg:
                raise serializers.ValidationError(f"error: {msg}")
        else:
            raise serializers.ValidationError(
                "There are no free books now, inventory is 0"
            )
