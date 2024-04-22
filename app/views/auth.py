from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render

from app.models import User, Invoice
from app.forms.auth import SignInUpForm


def logout_view(request: WSGIRequest):
    msg = f"Logged out. See you soon {request.user}"
    logout(request)
    messages.info(request, msg)
    return HttpResponseRedirect(request.GET.get("next", "/"))


def login_view(request: WSGIRequest):
    if request.method == "POST":
        data = request.POST
        user = authenticate(request, email=data.get(
            "email"), password=data.get("password"))
        if user:
            login(request, user)
            session_active_invoice = request.session.get("active_invoice")
            if session_active_invoice:
                Invoice.objects.filter(
                    customer=None,
                    session_id=session_active_invoice
                ).update(customer=user)
            messages.info(request, f"Logged in. Welcome {user}")
            return HttpResponseRedirect(request.GET.get("next", "/"))
        messages.warning(request, f"User not found.")
        current = request.GET.get("current")
        if current:
            return HttpResponseRedirect(current)
    return render(request, "website/auth/login.html")


def sign_in_up_view(request: WSGIRequest):
    form = SignInUpForm(data=request.POST or request.GET)
    if request.method == "POST":
        data = request.POST
        email = data.get("email")
        password = data.get("password")
        hasaccount = data.get("hasaccount") == "on"
        # print(data.get("hasaccount"))
        # return
        next_page = request.GET.get("next", "/")
        current_page = request.GET.get("current", "/")
        user: User = None
        session_active_invoice = request.session.get("active_invoice")
        set_invoice = lambda u: session_active_invoice and Invoice.objects.filter(
            customer=None,
            session_id=session_active_invoice
        ).update(customer=user)

        if hasaccount:
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                if not user._active_invoice:
                    set_invoice(user)
                messages.info(request, f"Logged in. Welcome {user}")
                return HttpResponseRedirect(next_page)
            messages.warning(request, f"User not found.")
            return HttpResponseRedirect(current_page)
        if User.objects.filter(email=email).exists():
            messages.error(
                request,
                f"User with email {email} alread exists, please sign in!"
            )
            return HttpResponseRedirect(current_page)
        user = User.objects.create(email=email, password=password)
        messages.info(request, f"Registered. Welcome {user}")
        login(request, user)
        set_invoice(user)
        return HttpResponseRedirect(next_page)
    return render(request, "website/auth/login.html")


def register_view(request: WSGIRequest):
    if request.method == "POST":
        data = request.POST
        user = User.objects.create(
            email=data.get("email"),
            password=data.get(
                "password") or User.objects.make_random_password(8)
        )
        if user:
            login(request, user)
            messages.info(request, f"Registered Welcome {user}")
            return HttpResponseRedirect(request.GET.get("next", "/"))
        messages.warning(request, f"User not found.")
    return render(request, "website/auth/login.html")
