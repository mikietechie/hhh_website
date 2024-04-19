from django.urls import path, include
from django.conf import settings
from . import views as website_views

urlpatterns = [
    path("", website_views.index_view)
]
