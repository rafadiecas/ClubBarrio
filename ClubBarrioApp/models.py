from django.db import models

# Create your models here.

class Usuario(models.Model):
    nombre = models.CharField(max_length=250)
    apellidos = models.CharField(max_length=250)
    password = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    fecha_nacimiento = models.DateField(default='1900-01-01')

    def __str__(self):
        return self.nombre + " " + self.apellidos
class categoria(models.Model):
    tipo = models.CharField(max_length=250)

    def __str__(self):
        return self.tipo


class Pedido(models.Model):
    numPedido = models.IntegerField()
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha = models.DateField(default='1900-01-01')
    direccion = models.CharField(max_length=500, default= 'sin dirección')
    def __str__(self):
        return str(self.numPedido) + " " + self.usuario.nombre + " " + self.usuario.apellidos

class Talla(models.Model):
    nombre = models.CharField(max_length=250)
    def __str__(self):
        return self.nombre
class Tipo(models.Model):
    nombre = models.CharField(max_length=250)
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=250)
    precio = models.FloatField()
    stock = models.IntegerField(default=0)
    pedidos = models.ManyToManyField(Pedido)
    tipo = models.ForeignKey(Tipo, on_delete=models.DO_NOTHING, null=True)
    talla = models.ForeignKey(Talla, on_delete=models.DO_NOTHING, null=True)
    def __str__(self):
        return self.nombre

class Administrador(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    def __str__(self):
        return self.usuario.nombre + " " + self.usuario.apellidos

class Entrenador(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    def __str__(self):
        return self.usuario.nombre + " " + self.usuario.apellidos

class TutorLegal(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    def __str__(self):
        return self.usuario.nombre + " " + self.usuario.apellidos

class Noticias(models.Model):
    titulo = models.CharField(max_length=250)
    articulo = models.TextField()
    url_imagen = models.CharField(max_length=500)
    administrador = models.ForeignKey(Administrador, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

class LugarEntrenamiento(models.Model):
    nombre = models.CharField(max_length=250)
    direccion = models.CharField(max_length=500, default= 'sin dirección')
class Entrenamiento(models.Model):
    fecha = models.DateField()
    hora = models.TimeField()
    entrenador = models.ForeignKey(Entrenador, on_delete=models.DO_NOTHING)
    lugarEntrenamiento = models.ForeignKey(LugarEntrenamiento, on_delete=models.DO_NOTHING, null=True)
    def __str__(self):
        return str(self.fecha) + " " + str(self.hora) + " " + self.lugarEntrenamiento.nombre

class Equipo(models.Model):
    nombre = models.CharField(max_length=250)
    escudo = models.CharField(max_length=500)
    categoria = models.ForeignKey(categoria, on_delete=models.DO_NOTHING)
    entrenadores = models.ManyToManyField(Entrenador)

    def __str__(self):
        return self.nombre

class Jugador(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipo, on_delete=models.DO_NOTHING)
    tutorLegal = models.ForeignKey(TutorLegal, on_delete=models.CASCADE)

    def __str__(self):
        return self.usuario.nombre + " " + self.usuario.apellidos

class Temporada(models.Model):

    anyo = models.CharField(max_length=250)

    def __str__(self):
        return self.anyo

class Partido(models.Model):
    fecha = models.DateField()
    hora = models.TimeField()
    lugar = models.CharField(max_length=500)
    puntos_equipo1 = models.IntegerField()
    puntos_equipo2 = models.IntegerField()
    equipo1 = models.ForeignKey(Equipo, on_delete=models.DO_NOTHING, related_name='equipo_local')
    equipo2 = models.ForeignKey(Equipo, on_delete=models.DO_NOTHING, related_name='equipo_visitante')
    temporada = models.ForeignKey(Temporada, on_delete=models.DO_NOTHING)

    def __str__(self):
        return str(self.fecha) + " " + str(self.hora) + " " + self.lugar + self.equipo1.nombre + " vs " + self.equipo2.nombre

class EstadisticasJugador(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE)
    puntos = models.IntegerField()
    minutos = models.IntegerField()
    rebotes = models.IntegerField()
    asistencias = models.IntegerField()
    faltas = models.IntegerField()

    def __str__(self):
        return self.jugador.usuario.nombre + " " + self.jugador.usuario.apellidos + " " + self.partido.equipo1.nombre + " vs " + self.partido.equipo2.nombre + " " + str(self.puntos) + " puntos"

