from django.urls import path

from borrowings.views import GetBorrowingView


urlpatterns = [
    path("", GetBorrowingView.as_view(), name="borrowings"),
    path("<int:pk>/", GetBorrowingView.as_view(), name="borrowings-detail")
]

app_name = "borrowings"
