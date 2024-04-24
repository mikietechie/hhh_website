from django.http.response import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import stripe

from app.models import Payment, Invoice, Settings


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(request, invoice_id: int):
    try:
        # Create new Checkout Session for the order
        # Other optional params include:
        # [billing_address_collection] - to display billing address details on the page
        # [customer] - if you have an existing Stripe Customer ID
        # [payment_intent_data] - capture the payment later
        # [customer_email] - prefill the email input in the form
        # For full details see https://stripe.com/docs/api/checkout/sessions/create
        # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
        app_settings = Settings.objects.first()
        invoice = Invoice.objects.get(id=invoice_id)
        success_url = f"{settings.SITE_URL}/payments/statuses/success/{invoice.pk}/"
        cancel_url = f"{settings.SITE_URL}/payments/statuses/cancelled/{invoice.pk}/"
        checkout_session: dict = stripe.checkout.Session.create(
            customer_email=invoice.invoice_email,
            success_url=success_url,
            cancel_url=cancel_url,
            payment_method_types=['card'],
            mode='payment',
            line_items=[
                {
                    'quantity': i.qty,
                    'price_data': {
                        'currency': app_settings.currency,
                        'unit_amount': int(i.product.price*100),
                        'product_data': {
                            'name': i.product.name,
                            'description': i.product.description,
                            'images': [f"{settings.SITE_URL}{i.product.image.url}"],
                        },
                    },
                } for i in invoice.items
            ],
            metadata={
                "invoice_id": invoice.pk
            }
        )
        print(checkout_session)
        Payment.objects.create(
            amount=checkout_session["amount_total"],
            invoice=invoice,
            method="stripe",
            status=Payment.Statuses.pending,
            gateway_id=checkout_session.payment_intent.id,
            gateway_url=checkout_session["url"],
        )
        return HttpResponseRedirect(checkout_session.url)
    except Exception as e:
        raise e
        return JsonResponse({'error': str(e)})


@csrf_exempt
def stripe_webhook(request):
    print(request.body)
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_ENDPOINT_SECRET
        )
        print(event)
    except ValueError as e:
        print(e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(e)
        return HttpResponse(status=400)
    payment = Payment.objects.get(gateway_id=event.data.object.payment_intent)
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        payment.status = Payment.completed
        payment.amount = event["amount_total"]
        payment.save()
    else:
        payment.status = Payment.cancelled
        payment.save()
    return HttpResponse(status=200)
