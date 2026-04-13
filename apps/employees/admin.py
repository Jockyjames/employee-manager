from django.contrib import admin
from .models import Employee, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description']
    search_fields = ['name', 'code']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'last_name', 'first_name', 'email', 'department', 'position', 'status', 'hire_date']
    list_filter = ['status', 'contract_type', 'department']
    search_fields = ['first_name', 'last_name', 'email', 'employee_id']
    ordering = ['last_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Identité', {'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'photo')}),
        ('Professionnel', {'fields': ('employee_id', 'department', 'position', 'contract_type', 'status')}),
        ('Dates', {'fields': ('hire_date', 'end_date')}),
        ('Rémunération', {'fields': ('salary',), 'classes': ('collapse',)}),
        ('Système', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
