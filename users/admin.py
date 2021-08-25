# -*- coding: utf-8 -*-
# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse

from users.models import APIUser, Invoice


class APIUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = APIUser
        fields = ("email", "first_name")


class APIUserChangeForm(UserChangeForm):
    class Meta:
        model = APIUser
        fields = ("email", "first_name")


class APIUserAdmin(UserAdmin):
    add_form = APIUserCreationForm
    form = APIUserChangeForm
    model = APIUser
    list_display = (
        "email",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "email",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": ("email", "password", "first_name")}),
        ("Permissions", {"fields": ("is_staff", "is_active")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(APIUser, APIUserAdmin)


class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "total_price",
        "tax_amount",
        "discount_amount",
    )

    def changelist_view(self, request, extra_context=None):
        extra = {}
        extra["url_loaddata_general"] = reverse(
            "loaddata_general", args=[self.model.__name__]
        )
        extra["url_dumpdata_general"] = reverse(
            "dumpdata_general", args=[self.model.__name__]
        )
        return super().changelist_view(request, extra_context=extra)


admin.site.register(Invoice, InvoiceAdmin)
