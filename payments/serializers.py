from rest_framework import serializers

from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    type = serializers.CharField()

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ("session_url", "session")


class PaymentRenewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = (
            "borrowing",
            "status",
            "type",
            "session_url",
            "session",
            "money_to_pay"
        )
