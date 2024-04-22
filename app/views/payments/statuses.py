from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, HttpResponseRedirect
from django.contrib import messages

from app.models import Invoice


def cancelled_view(request: WSGIRequest, invoice_id: int):
    invoice = Invoice.objects.get(id=invoice_id)
    invoice.cancel_checkout()
    messages.success(request, f"You may proceed to update your cart items")
    return HttpResponseRedirect("/cart/")


def success_view(request: WSGIRequest, invoice_id: int):
    invoice = Invoice.objects.get(id=invoice_id)
    messages.success(request, f"Thank you for your purchase, we are processing your order. You may keep shopping")
    return HttpResponseRedirect("/shop/")
