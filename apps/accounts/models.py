import random
import string
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


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


class EmailVerification(models.Model):
    MAX_INTENTOS = 5
    EXPIRY_MINUTES = 15

    user       = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verificaciones')
    code       = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    intentos   = models.PositiveSmallIntegerField(default=0)
    usado      = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    @classmethod
    def crear_para(cls, user):
        cls.objects.filter(user=user, usado=False).update(usado=True)
        code = ''.join(random.choices(string.digits, k=6))
        return cls.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + timezone.timedelta(minutes=cls.EXPIRY_MINUTES),
        )

    @property
    def expirado(self):
        return timezone.now() > self.expires_at

    @property
    def invalido(self):
        return self.usado or self.expirado or self.intentos >= self.MAX_INTENTOS

    def verificar(self, code_input):
        if self.invalido:
            return False, 'expirado'
        self.intentos += 1
        if self.code != code_input.strip():
            self.save(update_fields=['intentos'])
            restantes = self.MAX_INTENTOS - self.intentos
            return False, f'incorrecto:{restantes}'
        self.usado = True
        self.save(update_fields=['usado', 'intentos'])
        return True, 'ok'
