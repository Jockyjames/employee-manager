from rest_framework import generics, serializers
from .models import AuditLog
from apps.employees.permissions import CanViewLogs


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'user_email', 'action', 'app_label', 'model_name',
                  'object_id', 'description', 'ip_address', 'timestamp']


class AuditLogListAPIView(generics.ListAPIView):
    permission_classes = [CanViewLogs]
    serializer_class = AuditLogSerializer

    def get_queryset(self):
        return AuditLog.objects.select_related('user').all()[:500]
