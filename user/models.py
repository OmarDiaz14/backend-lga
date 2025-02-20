from django.db import models
from django.contrib.auth.models import AbstractUser


class Permiso(models.Model):
    nombre = models.CharField(max_length=100, unique= True)
    descripcion = models.TextField(blank=True)

class Roles (models.Model):
    nombre = models.CharField(max_length=100, unique= True)
    descripcion = models.TextField(blank=True)
    permisos = models.ManyToManyField(Permiso)


class User(AbstractUser):
    cargo = models.CharField(max_length=150, null= True, blank= True)
    unidad_admi = models.CharField(max_length=150, null= True, blank= True)
    roles = models.ManyToManyField(Roles)
    id_seccion = models.ForeignKey('cuadro.Seccion', models.DO_NOTHING,  null=True, blank=False)

    @property
    def name_seccion(self):
        if self.id_seccion:
            return self.id_seccion.seccion
        else:
            return None