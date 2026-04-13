from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from .models import Employee, Department
from .forms import EmployeeForm, EmployeeFilterForm
from apps.audit.utils import log_action


def require_can_edit(view_func):
    """Décorateur : réserve aux ADMIN et RH."""
    @login_required
    def wrapped(request, *args, **kwargs):
        if not request.user.can_edit_employees:
            messages.error(request, "Vous n'avez pas les droits pour effectuer cette action.")
            return redirect('employees_list')
        return view_func(request, *args, **kwargs)
    return wrapped


@login_required
def employees_list(request):
    queryset = Employee.objects.select_related('department').all()
    form = EmployeeFilterForm(request.GET or None)

    if form.is_valid():
        search = form.cleaned_data.get('search')
        department = form.cleaned_data.get('department')
        status = form.cleaned_data.get('status')
        contract = form.cleaned_data.get('contract_type')

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(position__icontains=search)
            )
        if department:
            queryset = queryset.filter(department=department)
        if status:
            queryset = queryset.filter(status=status)
        if contract:
            queryset = queryset.filter(contract_type=contract)

    context = {
        'employees': queryset,
        'form': form,
        'total': queryset.count(),
    }
    return render(request, 'employees/list.html', context)


@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee.objects.select_related('department'), pk=pk)
    show_salary = request.user.can_edit_employees
    return render(request, 'employees/detail.html', {
        'employee': employee,
        'show_salary': show_salary,
    })


@require_can_edit
def employee_create(request):
    form = EmployeeForm(request.POST or None, request.FILES or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        employee = form.save()
        log_action(request, request.user, 'CREATE', 'employees', 'Employee',
                   employee.id, f"Création employé {employee.get_full_name()}")
        messages.success(request, f"Employé {employee.get_full_name()} créé avec succès.")
        return redirect('employee_detail', pk=employee.pk)
    return render(request, 'employees/form.html', {'form': form, 'action': 'Ajouter un employé'})


@require_can_edit
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    form = EmployeeForm(request.POST or None, request.FILES or None, instance=employee, user=request.user)
    if request.method == 'POST' and form.is_valid():
        employee = form.save()
        log_action(request, request.user, 'UPDATE', 'employees', 'Employee',
                   employee.id, f"Modification employé {employee.get_full_name()}")
        messages.success(request, "Employé mis à jour avec succès.")
        return redirect('employee_detail', pk=employee.pk)
    return render(request, 'employees/form.html', {'form': form, 'action': 'Modifier', 'employee': employee})


@require_can_edit
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        name = employee.get_full_name()
        emp_id = employee.employee_id
        log_action(request, request.user, 'DELETE', 'employees', 'Employee',
                   employee.id, f"Suppression employé {name} ({emp_id})")
        employee.delete()
        messages.success(request, f"Employé {name} supprimé.")
        return redirect('employees_list')
    return render(request, 'employees/confirm_delete.html', {'employee': employee})
