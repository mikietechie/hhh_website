from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render

from app.models import Invoice


def cancelled_view(request: WSGIRequest, invoice_id: int):
    invoice = Invoice.objects.get(id=invoice_id)
    return render(request, "website/payments/cancelled.html", {"invoice": invoice})


def success_view(request: WSGIRequest, invoice_id: int):
    invoice = Invoice.objects.get(id=invoice_id)
    return render(request, "website/payments/success.html", {"invoice": invoice})
