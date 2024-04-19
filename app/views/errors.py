from django.shortcuts import HttpResponse
from django.core.handlers.wsgi import WSGIRequest


def http_404_view(request: WSGIRequest, exception: Exception):
    return HttpResponse("404")


def http_403_view(request: WSGIRequest, exception: Exception):
    return HttpResponse("403")


def http_500_view(request: WSGIRequest):
    return HttpResponse("500")
