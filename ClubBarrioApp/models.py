from django.contrib.auth.models import UserManager
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager


# Create your models here.
class Role(models.TextChoices):
    USUARIO = 'USUARIO', 'Usuario'
    JUGADOR = 'JUG', 'Jugador'
    TUTOR = 'TUTOR', 'Tutor'
    ENTRENADOR = 'ENTRENADOR', 'Entrenador'
    ADMIN = 'ADMIN', 'Administrador'

    def value_for_label(label):
        rol = None
        for choice in Role.choices:
            if choice[1] == label:
                rol = choice.__getitem__(1)
        return rol

class tarifa(models.TextChoices):
    BASE = 'BASE', 'Base'
    PLUS = 'PLUS', 'Plus'
    PREMIUM = 'PREMIUM', 'Premium'

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, )
    rol = models.CharField(max_length=50, choices=Role.choices, default=Role.USUARIO)
    fecha_nacimiento = models.DateField(default='1900-01-01')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password', 'email']

    def __str__(self):
        return self.username


class categoria(models.Model):
    tipo = models.CharField(max_length=250)

    def __str__(self):
        return self.tipo


class Pedido(models.Model):
    numPedido = models.IntegerField()
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateField(default='1900-01-01')
    direccion = models.CharField(max_length=500, default='sin dirección')

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
    url_imagen = models.CharField(max_length=500 , default='sin imagen')
    tipo = models.ForeignKey(Tipo, on_delete=models.DO_NOTHING, null=True)
    talla = models.ForeignKey(Talla, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.nombre


class Administrador(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=250, default='sin nombre')
    apellidos = models.CharField(max_length=250,default='sin apellidos')

    def __str__(self):
        return self.nombre + " " + self.apellidos


class Entrenador(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=250, default='sin nombre')
    apellidos = models.CharField(max_length=250, default='sin apellidos')

    def __str__(self):
        return self.nombre + " " + self.apellidos


class TutorLegal(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=250, default='sin nombre')
    apellidos = models.CharField(max_length=250, default='sin apellidos')
    es_activo = models.BooleanField(default=True)
    tarifa = models.CharField(max_length=50, choices=tarifa.choices, default=tarifa.BASE)

    def __str__(self):
        return self.nombre + " " + self.apellidos


class Noticias(models.Model):
    titulo = models.CharField(max_length=250)
    articulo = models.TextField()
    url_imagen = models.CharField(max_length=500)
    administrador = models.ForeignKey(Administrador, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo


class LugarEntrenamiento(models.Model):
    nombre = models.CharField(max_length=250)
    direccion = models.CharField(max_length=500, default='sin dirección')


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
    nombre = models.CharField(max_length=250, default='sin nombre')
    apellidos = models.CharField(max_length=250, default='sin apellidos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipo, on_delete=models.DO_NOTHING)
    tutorLegal = models.ForeignKey(TutorLegal, on_delete=models.CASCADE)
    es_activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre + " " + self.apellidos


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
        return str(self.fecha) + " " + str(
            self.hora) + " " + self.lugar + self.equipo1.nombre + " vs " + self.equipo2.nombre


class EstadisticasJugador(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE)
    puntos = models.IntegerField()
    minutos = models.IntegerField()
    rebotes = models.IntegerField()
    asistencias = models.IntegerField()
    faltas = models.IntegerField()

    def __str__(self):
        return self.jugador.usuario.nombre + " " + self.jugador.usuario.apellidos + " " + self.partido.equipo1.nombre + " vs " + self.partido.equipo2.nombre + " " + str(
            self.puntos) + " puntos"
