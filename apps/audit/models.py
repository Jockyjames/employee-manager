from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    ACTION_LOGIN = 'LOGIN'
    ACTION_LOGOUT = 'LOGOUT'
    ACTION_CREATE = 'CREATE'
    ACTION_UPDATE = 'UPDATE'
    ACTION_DELETE = 'DELETE'
    ACTION_VIEW = 'VIEW'
    ACTION_EXPORT = 'EXPORT'

    ACTION_CHOICES = [
        (ACTION_LOGIN, 'Connexion'),
        (ACTION_LOGOUT, 'Déconnexion'),
        (ACTION_CREATE, 'Création'),
        (ACTION_UPDATE, 'Modification'),
        (ACTION_DELETE, 'Suppression'),
        (ACTION_VIEW, 'Consultation'),
        (ACTION_EXPORT, 'Export'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_logs',
        verbose_name="Utilisateur"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Action")
    app_label = models.CharField(max_length=50, verbose_name="Application")
    model_name = models.CharField(max_length=100, verbose_name="Modèle")
    object_id = models.CharField(max_length=50, null=True, blank=True, verbose_name="ID objet")
    description = models.TextField(verbose_name="Description")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Date/heure", db_index=True)

    class Meta:
        verbose_name = "Journal d'audit"
        verbose_name_plural = "Journaux d'audit"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['app_label', 'model_name']),
        ]

    def __str__(self):
        user_str = self.user.email if self.user else "Anonyme"
        return f"[{self.timestamp.strftime('%d/%m/%Y %H:%M')}] {user_str} - {self.action} {self.model_name}"
