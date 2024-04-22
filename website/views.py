from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.handlers.wsgi import WSGIRequest
from django.contrib import messages

from app.utils import get_cached
from app.models import Product, Settings, Invoice

def get_cached_settings() -> Settings:
    return get_cached(
        "app_settings",
        lambda: Settings.objects.first(),
        timeout=60*60
    )

# Create your views here.
def index_view(request: WSGIRequest):
    app_settings = get_cached_settings()
    featured_products = get_cached(
        "featured_products",
        lambda: app_settings.featured_products.all(),
        timeout=60
    )
    return render(request, "website/index.html", {"featured_products": featured_products})


def shop_view(request: WSGIRequest):
    products = get_cached(
        "website_products",
        lambda: Product.objects.all(),
        timeout=60
    )
    return render(request, "website/shop.html", {"products": products})


def cart_view(request: WSGIRequest):
    app_settings = get_cached_settings()
    cart = Invoice.get_active_invoice(request)
    if not cart.items_count:
        messages.warning(request, f"Your cart is empty, please add some items!")
        return HttpResponseRedirect("/shop/")
    return render(request, "website/cart.html", {"cart": cart, "app_settings": app_settings})
