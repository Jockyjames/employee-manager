from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminUser(BasePermission):
    """Réservé aux ADMIN uniquement."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrRH(BasePermission):
    """ADMIN et RH peuvent écrire ; UTILISATEUR peut lire."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.can_edit_employees


class CanViewLogs(BasePermission):
    """Seuls ADMIN et RH voient les logs."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_view_logs
