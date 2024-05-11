from enum import Enum

from django.db import models
from borrowings.models import Borrowing


class PaymentStatus(Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    EXPIRED = "EXPIRED"


class PaymentType(Enum):
    PAYMENT = "PAYMENT"
    FINE = "FINE"


class Payment(models.Model):
    borrowing = models.ForeignKey(
        Borrowing,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    status = models.CharField(
        max_length=10,
        choices=[(payment.value, payment.name) for payment in PaymentStatus]
    )
    type = models.CharField(
        max_length=10,
        choices=[(tag.value, tag.name) for tag in PaymentType]
    )
    session_url = models.CharField(max_length=500, blank=True, null=True)
    session = models.CharField(max_length=100)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["borrowing"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self) -> str:
        return (
            f"{self.borrowing}, "
            f"status: {self.status}, "
            f"total: {self.money_to_pay}"
        )
