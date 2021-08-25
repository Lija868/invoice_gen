# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.models import Invoice


class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=200)
    last_name = serializers.CharField(max_length=200)
    username = serializers.CharField(max_length=200)
    phone_number = serializers.CharField(max_length=200)

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "username",
        )


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=200)
    username = serializers.CharField(max_length=200)

    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "password",
        )


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        exclude = (
            "created_at",
            "updated_at",
        )
