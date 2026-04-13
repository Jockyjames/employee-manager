from django.db import models
from django.utils import timezone


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    code = models.CharField(max_length=10, unique=True, verbose_name="Code")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"
        ordering = ['name']

    def __str__(self):
        return f"[{self.code}] {self.name}"


class Employee(models.Model):
    STATUS_ACTIVE = 'ACTIF'
    STATUS_INACTIVE = 'INACTIF'
    STATUS_LEAVE = 'CONGE'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Actif'),
        (STATUS_INACTIVE, 'Inactif'),
        (STATUS_LEAVE, 'En congé'),
    ]

    CONTRACT_CDI = 'CDI'
    CONTRACT_CDD = 'CDD'
    CONTRACT_STAGE = 'STAGE'
    CONTRACT_FREELANCE = 'FREELANCE'

    CONTRACT_CHOICES = [
        (CONTRACT_CDI, 'CDI'),
        (CONTRACT_CDD, 'CDD'),
        (CONTRACT_STAGE, 'Stage'),
        (CONTRACT_FREELANCE, 'Freelance'),
    ]

    # Informations personnelles
    first_name = models.CharField(max_length=150, verbose_name="Prénom")
    last_name = models.CharField(max_length=150, verbose_name="Nom")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    address = models.TextField(blank=True, verbose_name="Adresse")
    photo = models.ImageField(upload_to='employees/photos/', null=True, blank=True, verbose_name="Photo")

    # Informations professionnelles
    employee_id = models.CharField(max_length=20, unique=True, verbose_name="Matricule")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees', verbose_name="Département")
    position = models.CharField(max_length=200, verbose_name="Poste")
    contract_type = models.CharField(max_length=20, choices=CONTRACT_CHOICES, default=CONTRACT_CDI, verbose_name="Type de contrat")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE, verbose_name="Statut")
    hire_date = models.DateField(verbose_name="Date d'embauche")
    end_date = models.DateField(null=True, blank=True, verbose_name="Date de fin")

    # Informations sensibles (masquées selon rôle)
    salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Salaire")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['employee_id']),
            models.Index(fields=['department']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.employee_id})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    def get_seniority_years(self):
        from datetime import date
        delta = date.today() - self.hire_date
        return round(delta.days / 365, 1)
