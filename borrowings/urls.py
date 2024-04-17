from django.urls import path

from borrowings.views import ListCreateBorrowingView, DetailBorrowingView


urlpatterns = [
    path("", ListCreateBorrowingView.as_view(), name="borrowings"),
    path("<int:pk>/", DetailBorrowingView.as_view(), name="borrowings-detail"),
    path(
        "<int:pk>/return",
        DetailBorrowingView.as_view(),
        name="borrowings-return"
    )
]

app_name = "borrowings"
