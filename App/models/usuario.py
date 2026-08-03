from django.db import models

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    usuario = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    contraseña = models.CharField(max_length=255)
    rol = models.CharField(max_length=20)

    class Meta:
        db_table = "usuario"
        managed = False

    def __str__(self):
        return self.nombre