from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from apps.employees.models import Employee, Department
from apps.audit.models import AuditLog


@login_required
def dashboard(request):
    # Stats globales
    total = Employee.objects.count()
    actifs = Employee.objects.filter(status='ACTIF').count()
    inactifs = Employee.objects.filter(status='INACTIF').count()
    conges = Employee.objects.filter(status='CONGE').count()

    # Répartition par département
    dept_stats = Department.objects.annotate(
        count=Count('employees', filter=Q(employees__status='ACTIF'))
    ).order_by('-count')[:6]

    # Répartition par contrat
    contract_stats = Employee.objects.values('contract_type').annotate(count=Count('id')).order_by('-count')

    # Derniers employés ajoutés
    recent_employees = Employee.objects.select_related('department').order_by('-created_at')[:5]

    # Dernières actions (si autorisé)
    recent_logs = None
    if request.user.can_view_logs:
        recent_logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:8]

    context = {
        'stats': {
            'total': total,
            'actifs': actifs,
            'inactifs': inactifs,
            'conges': conges,
        },
        'dept_stats': dept_stats,
        'contract_stats': contract_stats,
        'recent_employees': recent_employees,
        'recent_logs': recent_logs,
    }
    return render(request, 'dashboard/index.html', context)
