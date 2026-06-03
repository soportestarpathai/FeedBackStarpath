from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USUARIO    = 'USUARIO'
    TESTER     = 'TESTER'
    ADMIN      = 'ADMIN'
    SUPERADMIN = 'SUPERADMIN'
    ROL_CHOICES = [
        (USUARIO,    'Usuario'),
        (TESTER,     'Tester'),
        (ADMIN,      'Admin'),
        (SUPERADMIN, 'SuperAdmin'),
    ]

    email                = models.EmailField(unique=True)
    rol                  = models.CharField(max_length=10, choices=ROL_CHOICES, default=USUARIO)
    plataformas_asignadas = models.ManyToManyField(
        'platforms.Platform',
        blank=True,
        related_name='usuarios_asignados',
    )

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def is_superadmin(self):
        return self.rol == self.SUPERADMIN

    @property
    def is_admin(self):
        return self.rol == self.ADMIN

    @property
    def is_tester(self):
        return self.rol == self.TESTER

    @property
    def is_usuario(self):
        return self.rol == self.USUARIO

    def __str__(self):
        return self.email
