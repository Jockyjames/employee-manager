from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.accounts.api_views import TokenObtainView, LogoutView
from apps.employees.api_views import EmployeeListCreateAPIView, EmployeeDetailAPIView, DepartmentListAPIView
from apps.audit.api_views import AuditLogListAPIView

urlpatterns = [
    path('auth/token/', TokenObtainView.as_view(), name='token_obtain'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('employees/', EmployeeListCreateAPIView.as_view(), name='api_employees'),
    path('employees/<int:pk>/', EmployeeDetailAPIView.as_view(), name='api_employee_detail'),
    path('departments/', DepartmentListAPIView.as_view(), name='api_departments'),
    path('audit/', AuditLogListAPIView.as_view(), name='api_audit'),
]
