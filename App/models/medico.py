from django.db import models
from .usuario import Usuario


class Medico(models.Model):
    id_medico = models.AutoField(primary_key=True)

    id_usuario = models.OneToOneField(
        Usuario,
        on_delete=models.DO_NOTHING,
        db_column="id_usuario"
    )

    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    matricula = models.CharField(max_length=30, unique=True)
    especialidad = models.CharField(max_length=50, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "medico"
        managed = False

    def __str__(self):
        return f"Dr. {self.apellido}, {self.nombre}"