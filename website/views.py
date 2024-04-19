from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest

# Create your views here.
def index_view(request: WSGIRequest):
    return render(request, "website/index.html")
