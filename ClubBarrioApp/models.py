from django.db import models

# Create your models here.
class Productos(models.Model):
    cod_producto = models.IntegerField()
    nombre = models.CharField(max_length=250)
    precio = models.FloatField()

    def __str__(self):
        return self.nombre