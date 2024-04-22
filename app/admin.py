from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from app import models


class InvoiceItemInlineAdmin(admin.TabularInline):
    fields = ("id", "product", "qty", "unit_price", "line_total")
    model = models.InvoiceItem


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "checked_out",
                    "items_count", "total", "amount_paid", "creation_timestamp")
    inlines = (InvoiceItemInlineAdmin, )
    fieldsets = [
        (
            None,
            {
                "fields": [("customer", "session_id"), ( "checked_out", "total", "amount_paid")],
            },
        ),
        (
            "More",
            {
                "classes": ["collapse"],
                "fields": ["checkout_email", "checkout_password", "checkout_address"],
            },
        ),
    ]


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "stock_qty")
    list_filter = ("category", )
    fieldsets = [
        (
            None,
            {
                "fields": ["name", "category", "image", "description", "price", "stock_qty"],
            },
        ),
        (
            "More",
            {
                "classes": ["collapse"],
                "fields": ["design_image", "image_1", "image_2", "image_3"],
            },
        ),
    ]


@admin.register(models.Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ("id", )


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ("is_staff",)
    list_display = ("id", "email", "phone", "last_login")
    fieldsets = [
        (
            None,
            {
                "fields": [("first_name", "last_name"), ("email", "phone", "password")],
            },
        ),
        (
            "More",
            {
                "classes": ["collapse"],
                "fields": ["image", "gender", "date_of_birth", "is_staff", "is_superuser"],
            },
        ),
    ]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).filter(is_staff=True)


@admin.register(models.Customer)
class CustomerAdmin(UserAdmin):
    list_display = ("id", "email", "phone", "last_login")

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super(admin.ModelAdmin, self).get_queryset(request).filter(is_staff=False)


# admin.site.register(models.User, UserAdmin)


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
