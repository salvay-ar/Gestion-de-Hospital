from django.db import models
from .diagnostico import Diagnostico


class Tratamiento(models.Model):
    id_tratamiento = models.AutoField(primary_key=True)

    id_diagnostico = models.ForeignKey(
        Diagnostico,
        on_delete=models.DO_NOTHING,
        db_column="id_diagnostico"
    )

    descripcion = models.TextField()
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "tratamiento"
        managed = False

    def __str__(self):
        return f"Tratamiento {self.id_tratamiento}"