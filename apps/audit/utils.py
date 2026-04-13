from .models import AuditLog


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_action(request, user, action, app_label, model_name, object_id=None, description=''):
    """Enregistre une action dans le journal d'audit."""
    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            app_label=app_label,
            model_name=model_name,
            object_id=str(object_id) if object_id is not None else None,
            description=description,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        )
    except Exception:
        pass  # Ne jamais bloquer une requête à cause des logs
