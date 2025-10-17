from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate

class User(AbstractUser):
    names = models.CharField('Nombres', max_length=100, blank=False, null=False)
    email = models.EmailField('Correo', max_length=254, unique=True, blank=False, null=False)
    phone_number = models.CharField('Teléfono', max_length=10, blank=True, null=True, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # mantenemos username como principal (como hace Django por defecto)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'names']

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='security_user_set',
        related_query_name='security_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='security_user_set',
        related_query_name='security_user',
    )

    class Meta:
        db_table = 'security_user'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.names} ({self.username})"

    def get_full_name(self):
        return self.names

    def get_short_name(self):
        return self.names.split()[0] if self.names else self.username

    # método para autenticación flexible
    @classmethod
    def authenticate(cls, username_or_email=None, password=None):
        """Permite login con username o email"""
        user = authenticate(username=username_or_email, password=password)
        if user is None:
            try:
                user_obj = cls.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except cls.DoesNotExist:
                pass
        return user
