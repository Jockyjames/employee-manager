from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from .models import AuditLog


@login_required
def audit_log_view(request):
    if not request.user.can_view_logs:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')

    logs = AuditLog.objects.select_related('user').all()

    # Filtres
    action_filter = request.GET.get('action', '')
    user_filter = request.GET.get('user', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if action_filter:
        logs = logs.filter(action=action_filter)
    if user_filter:
        logs = logs.filter(user__email__icontains=user_filter)
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)

    context = {
        'logs': logs[:200],
        'action_choices': AuditLog.ACTION_CHOICES,
        'filters': {
            'action': action_filter,
            'user': user_filter,
            'date_from': date_from,
            'date_to': date_to,
        }
    }
    return render(request, 'audit/logs.html', context)
