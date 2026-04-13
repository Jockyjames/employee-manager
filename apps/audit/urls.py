from django.urls import path
from .views import audit_log_view

urlpatterns = [
    path('logs/', audit_log_view, name='audit_logs'),
]
