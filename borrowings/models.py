from django.db import models

from books.models import Book
from library_service import settings


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ("-borrow_date", )
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "borrow_date",
                    "expected_return_date",
                    "actual_return_date"
                ],
                name="post_like")
        ]

    def __str__(self) -> str:
        return (f"borrow date:{self.borrow_date},"
                f"expected return date: {self.expected_return_date},"
                )
