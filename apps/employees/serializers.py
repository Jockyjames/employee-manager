from rest_framework import serializers
from .models import Employee, Department


class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'description', 'employee_count']

    def get_employee_count(self, obj):
        return obj.employees.filter(status='ACTIF').count()


class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    seniority = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'address', 'photo',
            'department', 'department_name', 'position',
            'contract_type', 'status', 'hire_date', 'end_date',
            'salary', 'seniority', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_seniority(self, obj):
        return obj.get_seniority_years()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        # Masquer le salaire pour les UTILISATEURS
        if request and hasattr(request, 'user'):
            user = request.user
            if not user.can_edit_employees:
                data.pop('salary', None)
        return data


class EmployeeListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'full_name', 'email', 'department_name', 'position', 'status', 'contract_type']

    def get_full_name(self, obj):
        return obj.get_full_name()
