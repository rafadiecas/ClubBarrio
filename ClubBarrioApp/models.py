from django.db import models

# Create your models here.
class categoria(models.Model):
    tipo = models.CharField(max_length=250)

    def __str__(self):
        return self.tipo