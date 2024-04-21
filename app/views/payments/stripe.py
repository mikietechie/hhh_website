from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import stripe

from app.models import Payment, Invoice, Settings

PAYMENTS_URL = f"{settings.SITE_URL}payments/"
STRIPE_PAYMENTS_URL = f"{PAYMENTS_URL}stripe/"


stripe.api_key = settings.STRIPE_SECRET_KEY

def init_stripe():
    return
    stripe.WebhookEndpoint.create(
        enabled_events=["charge.succeeded", "charge.failed"],
        url=f"{STRIPE_PAYMENTS_URL}webhook/",
    )

init_stripe()


@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        stripe.api_key = settings.STRIPE_SECRET_KEY
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
            invoice = Invoice.objects.get(pk=0)
            checkout_session: dict = stripe.checkout.Session.create(
                success_url=f"{PAYMENTS_URL}statuses/success/{invoice.pk}/?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{PAYMENTS_URL}statuses/cancelled/{invoice.pk}/?session_id={{CHECKOUT_SESSION_ID}}",
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'name': i.product.name,
                        'quantity': i.qty,
                        'currency': app_settings.currency,
                        'amount': i.line_total,
                    } for i in invoice.items
                ],
                metadata={
                    "invoice_id": invoice.pk
                }
            )
            Payment.objects.create(
                amount=checkout_session["amount_total"],
                invoice=invoice,
                method="stripe",
                status=Payment.Statuses.pending,
                gateway_id=checkout_session["id"],
                gateway_url=checkout_session["url"],
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    payment = Payment.objects.get(id=event["data"]["payment_id"])
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        payment.status = Payment.completed
        payment.amount = event["amount_total"]
        payment.save()
    else:
        payment.status = Payment.cancelled
        payment.save()
    return HttpResponse(status=200)
