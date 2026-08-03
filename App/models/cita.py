from django.db import models
from .paciente import Paciente
from .medico import Medico


class Cita(models.Model):
    id_cita = models.AutoField(primary_key=True)

    id_paciente = models.ForeignKey(
        Paciente,
        on_delete=models.DO_NOTHING,
        db_column="id_paciente"
    )

    id_medico = models.ForeignKey(
        Medico,
        on_delete=models.DO_NOTHING,
        db_column="id_medico"
    )

    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = "cita"
        managed = False

    def __str__(self):
        return f"Cita {self.id_cita}"