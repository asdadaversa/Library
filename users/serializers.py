from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password",  "first_name", "last_name", "is_staff")
        read_only_fields = ("id", "is_staff")
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        if password:
            if instance.check_password(password):
                user = super().update(instance, validated_data)
                return user
            else:
                raise ValidationError(
                    {
                        "message": "Please enter correct password. Password doesn't match stored data"
                    }
                )
        else:
            return super().update(instance, validated_data)
