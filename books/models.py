from enum import Enum

from django.db import models


class CoverType(Enum):
    HARD = "HARD"
    SOFT = "SOFT"


class Book(models.Model):
    title = models.CharField(max_length=63)
    author = models.CharField(max_length=63)
    cover = models.CharField(
        max_length=4, choices=[(tag.value, tag.name) for tag in CoverType]
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ["inventory"]
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self) -> str:
        return f"{self.title}, author: {self.author}, {self.inventory} left"
