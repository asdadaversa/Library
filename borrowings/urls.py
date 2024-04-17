from django.urls import path

from borrowings.views import ListCreateBorrowingView, DetailBorrowingView


urlpatterns = [
    path("", ListCreateBorrowingView.as_view(), name="borrowings"),
    path("<int:pk>/", DetailBorrowingView.as_view(), name="borrowings-detail")
]

app_name = "borrowings"
