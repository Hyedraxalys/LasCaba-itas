from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group
from django.dispatch import receiver

@receiver(post_migrate)
def crear_grupos(sender, **kwargs):
    Group.objects.get_or_create(name="Administrador")
    Group.objects.get_or_create(name="Encargado de preparación de cabañas")
