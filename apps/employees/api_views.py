from rest_framework import generics, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Employee, Department
from .serializers import EmployeeSerializer, EmployeeListSerializer, DepartmentSerializer
from .permissions import IsAdminOrRH
from apps.audit.utils import log_action


class EmployeeListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrRH]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'status', 'contract_type']
    search_fields = ['first_name', 'last_name', 'email', 'employee_id', 'position']
    ordering_fields = ['last_name', 'hire_date', 'department__name']
    ordering = ['last_name']

    def get_queryset(self):
        return Employee.objects.select_related('department').all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EmployeeListSerializer
        return EmployeeSerializer

    def perform_create(self, serializer):
        employee = serializer.save()
        log_action(self.request, self.request.user, 'CREATE', 'employees', 'Employee',
                   employee.id, f"Création employé {employee.get_full_name()} ({employee.employee_id})")


class EmployeeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrRH]
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        return Employee.objects.select_related('department').all()

    def perform_update(self, serializer):
        employee = serializer.save()
        log_action(self.request, self.request.user, 'UPDATE', 'employees', 'Employee',
                   employee.id, f"Modification employé {employee.get_full_name()}")

    def perform_destroy(self, instance):
        log_action(self.request, self.request.user, 'DELETE', 'employees', 'Employee',
                   instance.id, f"Suppression employé {instance.get_full_name()} ({instance.employee_id})")
        instance.delete()


class DepartmentListAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrRH]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
