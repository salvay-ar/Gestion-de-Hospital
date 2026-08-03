from django.db import models
from .paciente import Paciente


class HistorialMedico(models.Model):
    id_historial = models.AutoField(primary_key=True)

    id_paciente = models.ForeignKey(
        Paciente,
        on_delete=models.DO_NOTHING,
        db_column="id_paciente"
    )

    fecha_registro = models.DateField()
    observaciones = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "historial_medico"
        managed = False

    def __str__(self):
        return f"Historial {self.id_historial}"