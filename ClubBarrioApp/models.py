from django.db import models



# Create your models here.

def Usuario():
    nombre = models.CharField(max_length=250)
    apellidos = models.CharField(max_length=250)
    password = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
class categoria(models.Model):
    tipo = models.CharField(max_length=250)

    def __str__(self):
        return self.tipo