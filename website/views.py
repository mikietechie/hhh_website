from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.core.handlers.wsgi import WSGIRequest
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from app.utils import get_cached
from app.models import Product, Settings, Invoice


def get_cached_settings() -> Settings:
    return get_cached("app_settings", lambda: Settings.objects.first(), timeout=60 * 60)


def index_view(request: WSGIRequest):
    app_settings = get_cached_settings()
    featured_products = get_cached(
        "featured_products", lambda: app_settings.featured_products.all(), timeout=60
    )
    return render(
        request,
        "website/index.html",
        {"featured_products": featured_products, "app_settings": app_settings},
    )


def shop_view(request: WSGIRequest):
    app_settings = get_cached_settings()
    products = get_cached("website_products", lambda: Product.objects.all(), timeout=60)
    return render(
        request,
        "website/shop.html",
        {"products": products, "app_settings": app_settings},
    )


def cart_view(request: WSGIRequest):
    app_settings = get_cached_settings()
    cart = Invoice.get_active_invoice(request)
    if not cart.items_count:
        messages.warning(request, f"Your cart is empty, please add some items!")
        return HttpResponseRedirect("/shop/")
    return render(
        request, "website/cart.html", {"cart": cart, "app_settings": app_settings}
    )

@csrf_exempt
@require_http_methods(["POST"])
def contact(request: WSGIRequest):
    send_mail(
        subject="",
        message="",
        from_email="",
        fail_silently=False,
        recipient_list=[settings.DEFAULT_TO_EMAIL]
    )
    return JsonResponse({"msg": "Your email was sent successfully."})
