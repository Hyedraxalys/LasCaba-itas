from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('without_role', 'Sin rol asignado'),
        ('admin', 'Administrador'),
        ('manager', 'Encargado de preparación de cabañas'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='Sin rol asignado',
        verbose_name='Rol'
    )