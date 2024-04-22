from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


admin.site.site_title = "HHH Website"
admin.site.site_header = "HHH Website"
# admin.site.index_template = "website/index.html"


urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    path('tinymce/', include('tinymce.urls')),
    path("__debug__/", include("debug_toolbar.urls")),
    path('narrowroad/', admin.site.urls),
    path(f'auth/', include("app.urls.auth")),
    path(f'payments/', include("app.urls.payments")),
    path(f'invoices/', include("app.urls.invoices")),
    path(f'', include("website.urls")),
]

handler404 = 'app.views.errors.http_404_view'
handler403 = 'app.views.errors.http_403_view'
handler500 = 'app.views.errors.http_500_view'
