from django.urls import path, include
from rest_framework import routers

from payments.views import (
    PaymentViewSet,
    RenewPayment,
    cancel_payment,
    success_payment
)

router = routers.DefaultRouter()
router.register("", PaymentViewSet, basename="payments")

urlpatterns = [
    path("success/", success_payment, name="success"),
    path("cancel/", cancel_payment, name="cancel"),
    path("<int:pk>/renew/", RenewPayment.as_view(), name="renew"),
    path("", include(router.urls))
]

app_name = "payments"
