from decimal import Decimal as D
# import typing
# import datetime


from django.db import models
# from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.functional import cached_property
from django.core.exceptions import ValidationError

from .base import Base
from .fields import ImageField


class User(AbstractUser, Base):
    str_prefix = "U"
    GENDERS = ("M", "F", "O")
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    email = models.EmailField("Email Address", blank=True, unique=True)
    image = ImageField(upload_to="user_images", blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    gender = models.CharField(
        max_length=1, choices=Base.iter_as_choices(*GENDERS), blank=True, null=True
    )
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.get_full_name() or self.get_username()

    @property
    def initials_picture_url(self):
        return f"https://ui-avatars.com/api/?name={self}"

    @cached_property
    def invoices(self):
        return Invoice.objects.filter(customer=self.user)

    @property
    def active_invoice(self):
        return Invoice.objects.get_or_create(customer_id=self.pk, checked_out=False)[0]

    def __str__(self):
        return f"{self.str_id} - {self.user.get_full_name()}"

    def after_save(self, is_creation: bool):
        self.active_invoice
        return super().after_save(is_creation)


class Category(Base):
    class Meta(Base.Meta):
        verbose_name_plural = "Categories"

    name = models.CharField(max_length=256)
    image = ImageField()
    description = models.TextField()

    def __str__(self):
        return self.name

    @cached_property
    def products(self):
        return Product.objects.filter(category=self)


class Product(Base):
    name = models.CharField(max_length=256)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = ImageField()
    design_image = ImageField(blank=True, null=True)
    image_1 = ImageField(blank=True, null=True)
    image_2 = ImageField(blank=True, null=True)
    image_3 = ImageField(blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=32, decimal_places=2)
    stock_qty = models.IntegerField(default=0)
    similar = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return f"{self.str_id} - {self.name}"


class Invoice(Base):
    customer = models.ForeignKey(User, on_delete=models.PROTECT)
    checked_out = models.BooleanField(default=False)
    items_count = models.PositiveSmallIntegerField(default=0)
    total = models.DecimalField(max_digits=32, decimal_places=2, default=D("0.00"))

    def __str__(self):
        return f"{self.str_id} - {self.customer}"

    @cached_property
    def invoice_items(self):
        return InvoiceItem.objects.filter(invoice=self)

    @cached_property
    def invoice_items_total(self):
        return self.invoice_items.aggregate(sm=models.Sum("line_total"))["sm"] or D("0.00")

    @cached_property
    def invoice_items_count(self):
        return self.invoice_items.count()

    def sync_total_and_count(self):
        Invoice.objects.filter(id=self.pk).update(
            total=self.invoice_items_total, items_count=self.invoice_items_count
        )

    def after_save(self, is_creation: bool):
        super_after_save = super().after_save(is_creation)
        self.sync_total_and_count()
        return super_after_save

    def update_invoice_items(self, product: Product, qty: int, action: str|None = None):
        item_in_invoice = self.invoice_items.filter(product=product).first()
        if item_in_invoice:
            if qty:
                item_in_invoice.qty = qty
                item_in_invoice.save()
                return item_in_invoice
            else:
                item_in_invoice.delete()
        else:
            return InvoiceItem.objects.create(invoice=self, product=product, qty=qty)


class InvoiceItem(Base):
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.PositiveSmallIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=32, decimal_places=2, blank=True)
    line_total = models.DecimalField(max_digits=32, decimal_places=2, blank=True)

    def __str__(self):
        return f"{self.str_id} - {self.product}"

    def set_unit_price(self):
        self.unit_price = self.unit_price or self.product.price

    def set_line_total(self):
        self.line_total = self.unit_price * self.qty

    def save(self, *args, **kwargs):
        self.set_unit_price()
        self.set_line_total()
        return super().save(*args, **kwargs)

    def validate_invoice_checked_out(self):
        if self.invoice.checked_out:
            raise ValidationError(
                f"Invoice has already been checkout out, you can't edit items anymore!"
            )

    def after_save(self, is_creation: bool):
        super_after_save = super().after_save(is_creation)
        self.invoice.sync_total_and_count()
        return super_after_save


class Settings(Base):
    featured_products = models.ManyToManyField(Product, blank=True)

    @cached_property
    def categories(self):
        return Category.objects.all()
