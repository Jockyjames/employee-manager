from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('employees/', include('apps.employees.urls')),
    path('audit/', include('apps.audit.urls')),
    path('dashboard/', include('apps.employees.dashboard_urls')),
    path('api/', include('config.api_urls')),
    path('', include('apps.accounts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
