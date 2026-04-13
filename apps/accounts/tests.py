from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User


class UserModelTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@test.com', password='TestPass123!',
            first_name='Admin', last_name='User', role=User.ADMIN
        )
        self.rh = User.objects.create_user(
            email='rh@test.com', password='TestPass123!',
            first_name='RH', last_name='User', role=User.RH
        )
        self.user = User.objects.create_user(
            email='user@test.com', password='TestPass123!',
            first_name='Basic', last_name='User', role=User.UTILISATEUR
        )

    def test_admin_permissions(self):
        self.assertTrue(self.admin.is_admin)
        self.assertTrue(self.admin.can_edit_employees)
        self.assertTrue(self.admin.can_view_logs)

    def test_rh_permissions(self):
        self.assertFalse(self.rh.is_admin)
        self.assertTrue(self.rh.is_rh)
        self.assertTrue(self.rh.can_edit_employees)
        self.assertTrue(self.rh.can_view_logs)

    def test_user_permissions(self):
        self.assertFalse(self.user.is_admin)
        self.assertFalse(self.user.is_rh)
        self.assertFalse(self.user.can_edit_employees)
        self.assertFalse(self.user.can_view_logs)

    def test_full_name(self):
        self.assertEqual(self.admin.get_full_name(), 'Admin User')

    def test_str(self):
        self.assertIn('admin@test.com', str(self.admin))


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role=User.UTILISATEUR
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'email': 'test@test.com',
            'password': 'TestPass123!'
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_bad_password(self):
        response = self.client.post(reverse('login'), {
            'email': 'test@test.com',
            'password': 'wrong'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'incorrect')

    def test_redirect_if_authenticated(self):
        self.client.login(username='test@test.com', password='TestPass123!')
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('dashboard'))
