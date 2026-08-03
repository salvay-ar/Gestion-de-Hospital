from django.db import models
from .historial_medico import HistorialMedico
from .medico import Medico


class Diagnostico(models.Model):
    id_diagnostico = models.AutoField(primary_key=True)

    id_historial = models.ForeignKey(
        HistorialMedico,
        on_delete=models.DO_NOTHING,
        db_column="id_historial"
    )

    id_medico = models.ForeignKey(
        Medico,
        on_delete=models.DO_NOTHING,
        db_column="id_medico"
    )

    fecha = models.DateField()
    sintomas = models.TextField(null=True, blank=True)
    diagnostico = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "diagnostico"
        managed = False

    def __str__(self):
        return f"Diagnóstico {self.id_diagnostico}"