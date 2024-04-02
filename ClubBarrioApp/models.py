from django.db import models

# Create your models here.
class Productos(models.Model):
    cod_producto = models.IntegerField()
    nombre = models.CharField(max_length=250)
    precio = models.FloatField()

    def __str__(self):
        return self.nombre
class Usuario(models.Model):
    nombre = models.CharField(max_length=250)
    apellidos = models.CharField(max_length=250)
    password = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)

    def __str__(self):
        return self.nombre + " " + self.apellidos
class categoria(models.Model):
    tipo = models.CharField(max_length=250)

    def __str__(self):
        return self.tipo