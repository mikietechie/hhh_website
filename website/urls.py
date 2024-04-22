from django.urls import path
from . import views as website_views

urlpatterns = [
    path("", website_views.index_view),
    path("shop/", website_views.shop_view),
    path("cart/", website_views.cart_view),
]
