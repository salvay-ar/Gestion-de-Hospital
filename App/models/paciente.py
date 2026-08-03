from django.db import models


class Paciente(models.Model):
    id_paciente = models.AutoField(primary_key=True)
    dni = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    direccion = models.CharField(max_length=100, null=True, blank=True)
    grupo_sanguineo = models.CharField(max_length=10, null=True, blank=True)
    antecedentes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "paciente"
        managed = False

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"