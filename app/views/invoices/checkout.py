from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.contrib.auth import login
from django.contrib import messages

from app.models import Invoice


def checkout_view(request: WSGIRequest, invoice_id: int):
    invoice = Invoice.objects.get(id=invoice_id)
    invoice.checkout(
        checkout_email=request.GET.get("checkout_email"),
        checkout_password=request.GET.get("checkout_password"),
        checkout_address=request.GET.get("checkout_address"),
    )
    if not request.user.is_authenticated and invoice.customer:
        login(request, invoice.customer)
        messages.info(
            request,
            f"Welcome {invoice.customer}, please find your password in your email."
        )
    # TODO: maybe add multiple payment methods handler
    return HttpResponseRedirect(f"/payments/stripe/checkout/{invoice.pk}/")
