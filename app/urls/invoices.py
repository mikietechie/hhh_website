from django.urls import path
from app.views.invoices import cart, checkout

urlpatterns = [
    path("cart/add/<int:product_id>/", cart.create_cart_item),
    path("cart/update/<int:invoice_item_id>/", cart.update_cart_item),
    path("cart/remove/<int:invoice_item_id>/", cart.remove_cart_item),
    path("checkout/<int:invoice_id>/", checkout.checkout_view),
]
