from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import User
from apps.employees.models import Employee, Department
from datetime import date


class JWTAuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='api@test.com', password='TestPass123!',
            first_name='Api', last_name='User', role=User.ADMIN
        )

    def test_obtain_token(self):
        response = self.client.post('/api/auth/token/', {
            'email': 'api@test.com',
            'password': 'TestPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['role'], 'ADMIN')

    def test_obtain_token_bad_credentials(self):
        response = self.client.post('/api/auth/token/', {
            'email': 'api@test.com',
            'password': 'wrong'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_without_token(self):
        response = self.client.get('/api/employees/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_with_token(self):
        token_response = self.client.post('/api/auth/token/', {
            'email': 'api@test.com', 'password': 'TestPass123!'
        })
        token = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/employees/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EmployeeAPIPermissionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.dept = Department.objects.create(name='IT', code='IT')
        self.admin = User.objects.create_user(
            email='admin@test.com', password='TestPass123!',
            first_name='Admin', last_name='U', role=User.ADMIN
        )
        self.rh = User.objects.create_user(
            email='rh@test.com', password='TestPass123!',
            first_name='RH', last_name='U', role=User.RH
        )
        self.basic = User.objects.create_user(
            email='basic@test.com', password='TestPass123!',
            first_name='Basic', last_name='U', role=User.UTILISATEUR
        )
        self.emp = Employee.objects.create(
            first_name='Test', last_name='Emp', email='emp@test.com',
            employee_id='EMP-999', department=self.dept, position='Dev',
            contract_type='CDI', status='ACTIF', hire_date=date(2022, 1, 1),
            salary=300000
        )

    def _get_token(self, email, password):
        r = self.client.post('/api/auth/token/', {'email': email, 'password': password})
        return r.data['access']

    def test_basic_user_can_read(self):
        token = self._get_token('basic@test.com', 'TestPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/employees/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_basic_user_salary_hidden(self):
        token = self._get_token('basic@test.com', 'TestPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(f'/api/employees/{self.emp.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('salary', response.data)

    def test_rh_salary_visible(self):
        token = self._get_token('rh@test.com', 'TestPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(f'/api/employees/{self.emp.pk}/')
        self.assertIn('salary', response.data)

    def test_basic_user_cannot_create(self):
        token = self._get_token('basic@test.com', 'TestPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/employees/', {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rh_can_create(self):
        token = self._get_token('rh@test.com', 'TestPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/employees/', {
            'first_name': 'New', 'last_name': 'Emp', 'email': 'new@test.com',
            'employee_id': 'EMP-100', 'department': self.dept.pk,
            'position': 'Dev', 'contract_type': 'CDI',
            'status': 'ACTIF', 'hire_date': '2024-01-01'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_audit_endpoint_blocked_for_basic(self):
        token = self._get_token('basic@test.com', 'TestPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/audit/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_audit_endpoint_accessible_for_rh(self):
        token = self._get_token('rh@test.com', 'TestPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/audit/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
