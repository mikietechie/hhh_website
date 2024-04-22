from django.urls import path
from app.views.payments import statuses, stripe

urlpatterns = [
    path("statuses/success/<int:invoice_id>/", statuses.success_view),
    path("statuses/cancelled/<int:invoice_id>/", statuses.cancelled_view),
    path("stripe/webhook/", stripe.stripe_webhook),
    path("stripe/checkout/<int:invoice_id>/", stripe.create_checkout_session),
]