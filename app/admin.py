from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from app import models


class InvoiceItemInlineAdmin(admin.TabularInline):
    model = models.InvoiceItem


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "checked_out", "items_count", "total", "paid",)
    inlines = (InvoiceItemInlineAdmin, )


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


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

