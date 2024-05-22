from django.urls import path

from borrowings.views import (
    ListCreateBorrowingView,
    DetailBorrowingView,
    ReturnBorrowingView
)

urlpatterns = [
    path("", ListCreateBorrowingView.as_view(), name="borrowings"),
    path(
        "<int:pk>/",
        DetailBorrowingView.as_view(),
        name="borrowings-detail"
    ),
    path(
        "<int:pk>/return/",
        ReturnBorrowingView.as_view(),
        name="borrowings-return"
    )
]

app_name = "borrowings"
