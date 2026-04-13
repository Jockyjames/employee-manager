from django.test import TestCase, RequestFactory
from apps.accounts.models import User
from apps.audit.models import AuditLog
from apps.audit.utils import log_action


class AuditLogTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email='admin@test.com', password='TestPass123!',
            first_name='Admin', last_name='Test', role=User.ADMIN
        )

    def test_log_action_creates_entry(self):
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'TestBrowser'
        log_action(request, self.user, 'CREATE', 'employees', 'Employee', 1, 'Test creation')
        self.assertEqual(AuditLog.objects.count(), 1)
        log = AuditLog.objects.first()
        self.assertEqual(log.action, 'CREATE')
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.ip_address, '127.0.0.1')

    def test_log_str(self):
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'TestBrowser'
        log_action(request, self.user, 'LOGIN', 'accounts', 'User', self.user.pk, 'Connexion')
        log = AuditLog.objects.first()
        self.assertIn('LOGIN', str(log))

    def test_audit_view_requires_admin_or_rh(self):
        from django.test import Client
        from django.urls import reverse
        client = Client()
        basic = User.objects.create_user(
            email='basic@test.com', password='TestPass123!',
            first_name='Basic', last_name='User', role=User.UTILISATEUR
        )
        client.force_login(basic)
        response = client.get(reverse('audit_logs'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_audit_view_accessible_for_rh(self):
        from django.test import Client
        from django.urls import reverse
        client = Client()
        rh = User.objects.create_user(
            email='rh@test.com', password='TestPass123!',
            first_name='RH', last_name='User', role=User.RH
        )
        client.force_login(rh)
        response = client.get(reverse('audit_logs'))
        self.assertEqual(response.status_code, 200)
