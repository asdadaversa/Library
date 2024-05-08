from django.urls import path

from borrowings.views import ListCreateBorrowingView, DetailReturnBorrowingView

urlpatterns = [
    path("", ListCreateBorrowingView.as_view(), name="borrowings"),
    path("<int:pk>/", DetailReturnBorrowingView.as_view(), name="borrowings-detail"),
    path(
        "<int:pk>/return",
        DetailReturnBorrowingView.as_view(),
        name="borrowings-return"
    )
]

app_name = "borrowings"
