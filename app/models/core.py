from __future__ import annotations
from decimal import Decimal as D
import time
from enum import Enum
import logging

from django.db import models
# from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from django.utils.functional import cached_property
from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest

from .base import Base
from .fields import ImageField


class User(AbstractUser, Base):
    _password: str = None
    str_prefix = "U"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Genders(str, Enum):
        male, female, other = "M", "F", "O"

    email = models.EmailField("Email Address", blank=True, unique=True)
    image = ImageField(upload_to="user_images", blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    gender = models.CharField(
        max_length=1,
        choices=Base.iter_as_choices(*Genders, f=Base.get_enum_value),
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True, max_length=1024)
    username = None

    def __str__(self):
        return self.get_full_name() or self.get_username()

    @property
    def initials_picture_url(self):
        return f"https://ui-avatars.com/api/?name={self}"

    @cached_property
    def invoices(self):
        return Invoice.objects.filter(customer=self.user)

    @property
    def _active_invoice(self):
        return Invoice.objects.filter(
            customer_id=self.pk, checked_out=False
        ).first()

    @property
    def active_invoice(self):
        return self._active_invoice or Invoice.objects.create(customer=self)

    def save(self, *args, **kwargs) -> None:
        if self.password and (len(self.password) != 88):
            self._password = self.password
            self.password = make_password(self.password)
        return super().save(*args, **kwargs)

    def after_save(self, is_creation: bool):
        self.active_invoice
        if self._password:
            try:
                self.email_user(
                    subject="HHH Password",
                    message=f"Your new password is {self._password}."
                )
            except:
                logging.error(f"Failed to send password email to {self.email}")
        return super().after_save(is_creation)


class Customer(User):
    class Meta:
        proxy = True


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
    str_prefix = "INV"
    customer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    session_id = models.CharField(max_length=256, blank=True, null=True)
    checked_out = models.BooleanField(default=False)
    # paid = models.BooleanField(default=False)
    items_count = models.PositiveSmallIntegerField(default=0)
    total = models.DecimalField(
        max_digits=32,
        decimal_places=2,
        default=D("0.00")
    )
    amount_paid = models.DecimalField(
        max_digits=32,
        decimal_places=2,
        default=D("0.00")
    )
    checkout_email = models.EmailField(max_length=256, blank=True, null=True)
    checkout_password = models.CharField(max_length=32, blank=True, null=True)
    checkout_address = models.TextField(blank=True, null=True, max_length=1024)

    @cached_property
    def invoice_email(self):
        return self.checkout_email or (
            self.customer.email if self.customer else None
        )

    @cached_property
    def invoice_address(self):
        return self.checkout_address or (
            self.customer.address if self.customer else ""
        )

    @cached_property
    def invoice_items(self):
        return InvoiceItem.objects.filter(invoice=self)

    @cached_property
    def items(self):
        return self.invoice_items.select_related("product")

    @cached_property
    def payments(self):
        return Payment.objects.filter(invoice=self)

    @cached_property
    def items_total(self):
        return self.invoice_items.aggregate(
            sm=models.Sum("line_total")
        )["sm"] or D("0.00")

    def get_items_count(self):
        return self.invoice_items.count()

    def sync_amount_paid(self):
        Invoice.objects.filter(id=self.pk).update(
            amount_paid=self.payments.filter(status=Payment.Statuses.completed).aggregate(
                sm=models.Sum("amount"))["sm"] or D("0.00")
        )

    def sync_total_and_count(self):
        Invoice.objects.filter(id=self.pk).update(
            total=self.items_total, items_count=self.get_items_count()
        )

    def set_checkout_values(self):
        if self.customer:
            self.checkout_email = self.checkout_email or self.customer.email
            self.checkout_address = self.checkout_address or self.customer.address

    def set_customer_values(self):
        if not self.customer and self.checkout_email:
            if not User.objects.filter(email=self.checkout_email).exists():
                u = User(
                    email=self.checkout_email,
                    address=self.checkout_address,
                    password=(
                        self.checkout_password or
                        User.objects.make_random_password(8)
                    )
                )
                u.save()
                self.checkout_password = u._password
                self.customer = u
                logging.info(f"Created customer {u} from invoice {self}")

    def save(self, *args, **kwargs) -> None:
        self.set_checkout_values()
        self.set_customer_values()
        return super().save(*args)

    def after_save(self, is_creation: bool):
        super_after_save = super().after_save(is_creation)
        self.sync_total_and_count()
        self.sync_amount_paid()
        return super_after_save
    
    def checkout(self, checkout_email: str, checkout_password: str, checkout_address: str):
        if not self.customer:
            self.checkout_address = checkout_address
            self.checkout_password = checkout_password
            self.checkout_email = checkout_email
        self.checked_out = True
        return self.save()
    
    def cancel_checkout(self, **kwargs):
        self.checked_out = False
        return self.save()

    @classmethod
    def create_active_invoice_session_id(cls):
        session_id = f"{User.objects.make_random_password(8)}-{time.time()}"
        while Invoice.objects.filter(session_id=session_id).exists():
            return cls.create_active_invoice_session_id()
        return session_id

    @classmethod
    def get_active_invoice(cls, request: WSGIRequest) -> Invoice:
        if request.user.is_authenticated:
            return request.user.active_invoice
        try:
            return Invoice.objects.get(
                session_id=request.session["active_invoice"],
                checked_out=False
            )
        except:
            session_id = cls.create_active_invoice_session_id()
            request.session["active_invoice"] = session_id
            return Invoice.objects.create(session_id=session_id)
        


class InvoiceItem(Base):
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.PositiveSmallIntegerField(default=1)
    unit_price = models.DecimalField(
        max_digits=32, decimal_places=2, blank=True)
    line_total = models.DecimalField(
        max_digits=32, decimal_places=2, blank=True)

    def __str__(self):
        return f"{self.str_id} - {self.product}"

    def set_unit_price(self):
        self.unit_price = self.unit_price or self.product.price

    def set_line_total(self):
        self.line_total = self.unit_price * self.qty

    def clean_invoice(self):
        if self.invoice.checked_out:
            raise ValidationError(
                "You cannot add or update items to a checkout out invoice!")

    def clean(self) -> None:
        super().clean()
        self.clean_invoice()

    def get_existing(self):
        if not self.id:
            item = self.invoice.invoice_items.filter(
                product=self.product).first()
            if item:
                item.qty = self.qty
                return item

    def save(self, *args, **kwargs):
        self.set_unit_price()
        self.set_line_total()
        item = self.get_existing()
        if item:
            return item.save()
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

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        super_delete = super().delete(*args, **kwargs)
        self.invoice.sync_total_and_count()
        return super_delete


class Payment(Base):
    str_prefix = "Payment"

    class Statuses(str, Enum):
        pending, cancelled, completed = "Pending", "Cancelled", "Completed"

    class Methods(str, Enum):
        cash, stripe = "Cash", "Stripe"

    amount = models.DecimalField(
        max_digits=32, decimal_places=2, default=D("0.00")
    )
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT)
    method = models.CharField(
        max_length=64,
        choices=Base.iter_as_choices(*Methods, f=Base.get_enum_value)
    )
    status = models.CharField(
        max_length=64,
        choices=Base.iter_as_choices(*Statuses)
    )
    gateway_id = models.CharField(max_length=256, blank=True, null=True)
    gateway_url = models.URLField(max_length=512, blank=True, null=True)

    def after_save(self, is_creation: bool):
        super_after_save = super().after_save(is_creation)
        self.invoice.sync_amount_paid()
        return super_after_save

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        super_delete = super().delete(*args, **kwargs)
        self.invoice.sync_amount_paid()
        return super_delete


class Settings(Base):
    class Currencies(str, Enum):
        euro, usd = "eur", "usd"

    featured_products = models.ManyToManyField(Product, blank=True)
    currency = models.CharField(
        max_length=16,
        default=Currencies.euro,
        choices=Base.iter_as_choices(*Currencies, f=Base.get_enum_value)
    )

    @cached_property
    def currency_symbol(self):
        if self.currency == self.Currencies.euro:
            return "€"
        return "$"

    @cached_property
    def categories(self):
        return Category.objects.all()

    def clean_id(self):
        if not self.id and Settings.objects.exists():
            raise ValidationError("You can only have one settings.")

    def save(self, *args, **kwargs) -> None:
        self.clean_id()
        return super().save(*args, **kwargs)
