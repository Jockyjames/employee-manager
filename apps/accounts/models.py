from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ADMIN = 'ADMIN'
    RH = 'RH'
    UTILISATEUR = 'UTILISATEUR'

    ROLE_CHOICES = [
        (ADMIN, 'Administrateur'),
        (RH, 'Ressources Humaines'),
        (UTILISATEUR, 'Utilisateur'),
    ]

    email = models.EmailField(unique=True, verbose_name="Adresse email")
    first_name = models.CharField(max_length=150, verbose_name="Prénom")
    last_name = models.CharField(max_length=150, verbose_name="Nom")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=UTILISATEUR, verbose_name="Rôle")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    is_staff = models.BooleanField(default=False, verbose_name="Staff")
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="Date d'inscription")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="Dernière connexion")

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_rh(self):
        return self.role == self.RH

    @property
    def can_edit_employees(self):
        return self.role in [self.ADMIN, self.RH]

    @property
    def can_view_logs(self):
        return self.role in [self.ADMIN, self.RH]
