from django.contrib import admin
from app import models

# Register your models here.
admin.site.register([
    models.User,
    models.Category,
    models.Product,
    models.Invoice,
    models.InvoiceItem,
    models.Settings,
])
