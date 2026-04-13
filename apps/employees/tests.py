from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.employees.models import Employee, Department


class EmployeeModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name='IT', code='IT')
        from datetime import date
        self.emp = Employee.objects.create(
            first_name='Jean', last_name='Dupont',
            email='jean@test.com', employee_id='EMP-001',
            department=self.dept, position='Développeur',
            contract_type='CDI', status='ACTIF',
            hire_date=date(2022, 1, 1)
        )

    def test_full_name(self):
        self.assertEqual(self.emp.get_full_name(), 'Jean Dupont')

    def test_is_active(self):
        self.assertTrue(self.emp.is_active)

    def test_seniority(self):
        self.assertGreater(self.emp.get_seniority_years(), 0)

    def test_str(self):
        self.assertIn('EMP-001', str(self.emp))


class EmployeeViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(name='IT', code='IT')
        from datetime import date

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
            first_name='Paul', last_name='Martin',
            email='paul@test.com', employee_id='EMP-002',
            department=self.dept, position='Manager',
            contract_type='CDI', status='ACTIF',
            hire_date=date(2021, 6, 1), salary=500000
        )

    def test_list_requires_login(self):
        response = self.client.get(reverse('employees_list'))
        self.assertRedirects(response, '/accounts/login/?next=/employees/')

    def test_list_accessible_to_all_roles(self):
        for user in [self.admin, self.rh, self.basic]:
            self.client.force_login(user)
            response = self.client.get(reverse('employees_list'))
            self.assertEqual(response.status_code, 200)

    def test_detail_accessible_to_all_roles(self):
        for user in [self.admin, self.rh, self.basic]:
            self.client.force_login(user)
            response = self.client.get(reverse('employee_detail', args=[self.emp.pk]))
            self.assertEqual(response.status_code, 200)

    def test_salary_hidden_for_basic_user(self):
        self.client.force_login(self.basic)
        response = self.client.get(reverse('employee_detail', args=[self.emp.pk]))
        self.assertNotContains(response, '500')

    def test_salary_visible_for_rh(self):
        self.client.force_login(self.rh)
        response = self.client.get(reverse('employee_detail', args=[self.emp.pk]))
        self.assertContains(response, '500')

    def test_create_blocked_for_basic_user(self):
        self.client.force_login(self.basic)
        response = self.client.get(reverse('employee_create'))
        self.assertRedirects(response, reverse('employees_list'))

    def test_create_accessible_for_rh(self):
        self.client.force_login(self.rh)
        response = self.client.get(reverse('employee_create'))
        self.assertEqual(response.status_code, 200)

    def test_delete_blocked_for_rh(self):
        self.client.force_login(self.rh)
        response = self.client.get(reverse('employee_delete', args=[self.emp.pk]))
        self.assertRedirects(response, reverse('employees_list'))

    def test_delete_accessible_for_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('employee_delete', args=[self.emp.pk]))
        self.assertEqual(response.status_code, 200)

    def test_search_filter(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('employees_list') + '?search=Paul')
        self.assertContains(response, 'Martin')

    def test_search_no_results(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('employees_list') + '?search=zzzimaginary')
        self.assertContains(response, '0')
