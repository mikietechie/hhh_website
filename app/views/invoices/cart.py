from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages

from app.models import Product, Invoice, InvoiceItem


def create_cart_item(request: WSGIRequest, product_id: int):
    invoice = Invoice.get_active_invoice(request)
    product = Product.objects.get(id=product_id)
    invoice_item = InvoiceItem(invoice=invoice, product=product)
    invoice_item.save()
    messages.success(request, f"Successfully added {product.name} to your shopping cart {invoice}!")
    next_page = request.GET.get("next")
    if next_page:
        return HttpResponseRedirect(next_page)
    return HttpResponse(status=200)


def update_cart_item(request: WSGIRequest, invoice_item_id: int):
    invoice = Invoice.get_active_invoice(request)
    invoice_item = InvoiceItem.objects.get(id=invoice_item_id, invoice=invoice)
    invoice_item.qty = int(request.GET.get("qty"))
    invoice_item.save()
    messages.success(request, f"Successfully updated {invoice_item.product.name} in your shopping cart!")
    next_page = request.GET.get("next")
    if next_page:
        return HttpResponseRedirect(next_page)
    return HttpResponse(status=200)


def remove_cart_item(request: WSGIRequest, invoice_item_id: int):
    invoice = Invoice.get_active_invoice(request)
    invoice_item = invoice.items.get(id=invoice_item_id)
    invoice_item.delete()
    messages.success(request, f"Successfully removed {invoice_item.product.name} from your shopping cart!")
    next_page = request.GET.get("next")
    if next_page:
        return HttpResponseRedirect(next_page)
    return HttpResponse(status=200)
