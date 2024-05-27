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

    @classmethod
    def value_for_label(cls, label):
        tarifa = None
        for choice in cls.choices:
            if choice[1] == label:
                tarifa = choice[0]
        return tarifa


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
    foto = models.ImageField(upload_to='foto_perfil', default='foto_perfil/default.png')
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=50, null=True, blank=True)
    email_verification_token_expiration = models.DateTimeField(null=True, blank=True)
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password', 'email']

    def __str__(self):
        return self.username
class Notificaciones(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    password_change = models.BooleanField(default=False)
    weekly_newsletter = models.BooleanField(default=False)
    new_training = models.BooleanField(default=False)

    def __str__(self):
        return f'Notificaciones para {self.usuario.username}'

class Presidente(models.Model):
    nombre = models.CharField(max_length=250, default='sin nombre')
    apellidos = models.CharField(max_length=250, default='sin apellidos')
    equipo = models.ForeignKey('Equipo', on_delete=models.DO_NOTHING)

class Arbitro(models.Model):
    nombre = models.CharField(max_length=250, default='sin nombre')
    apellidos = models.CharField(max_length=250, default='sin apellidos')

    def __str__(self):
        return self.nombre + " " + self.apellidos






class Categoria(models.Model):
    tipo = models.CharField(max_length=250)

    def __str__(self):
        return self.tipo

class metodoEnvio(models.TextChoices):
    DOMICILIO = 'DOMICILIO', 'Domicilio'
    CLUB = 'CLUB', 'Club'
class Pedido(models.Model):
    numPedido = models.IntegerField()
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateField(default='1900-01-01')
    direccion = models.CharField(max_length=500, default='sin dirección')
    metodoEnvio = models.CharField(max_length=50, choices=metodoEnvio.choices, default=metodoEnvio.CLUB)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

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
    descripcion = models.TextField(default='sin descripción')
    url_imagen = models.CharField(max_length=500, default='sin imagen')
    tipo = models.ForeignKey(Tipo, on_delete=models.DO_NOTHING, null=True)
    tallas = models.ManyToManyField(Talla, through='ProductoTalla')


    def __str__(self):
        return self.nombre

class ProductoTalla(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    talla = models.ForeignKey(Talla, on_delete=models.DO_NOTHING, null=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.producto.nombre + " " + self.talla.nombre + " " + str(self.stock)
class LineaPedido(models.Model):
    prductoTalla = models.ForeignKey(ProductoTalla, on_delete=models.DO_NOTHING)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=0)
    def __str__(self):
        return self.prductoTalla + self.pedido + self.cantidad

class Administrador(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=250, default='sin nombre')
    apellidos = models.CharField(max_length=250, default='sin apellidos')
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
    equipo = models.ForeignKey('Equipo', on_delete=models.DO_NOTHING,default=1)

    def __str__(self):
        return str(self.fecha) + " " + str(self.hora) + " " + self.lugarEntrenamiento.nombre


class Equipo(models.Model):
    nombre = models.CharField(max_length=250)
    escudo = models.CharField(max_length=500)
    categoria = models.ForeignKey(Categoria, on_delete=models.DO_NOTHING)
    entrenadores = models.ManyToManyField(Entrenador)
    es_safa = models.BooleanField(default=False)

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
    puntos_equipo1 = models.IntegerField(default=0)
    puntos_equipo2 = models.IntegerField(default=0)
    equipo1 = models.ForeignKey(Equipo, on_delete=models.DO_NOTHING, related_name='equipo_local')
    equipo2 = models.ForeignKey(Equipo, on_delete=models.DO_NOTHING, related_name='equipo_visitante')
    temporada = models.ForeignKey(Temporada, on_delete=models.DO_NOTHING)
    jornada = models.IntegerField(default=0)
    arbitro = models.ForeignKey(Arbitro, on_delete=models.DO_NOTHING, null=True)

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
        return self.jugador.nombre + " " + self.jugador.apellidos + " " + self.partido.equipo1.nombre + " vs " + self.partido.equipo2.nombre + " " + str(
            self.puntos) + " puntos"

class Convocatoria(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE)

    def __str__(self):
        return self.jugador.nombre + " " + self.jugador.apellidos + " " + self.partido.equipo1.nombre + " vs " + self.partido.equipo2.nombre


class Evento(models.Model):
    nombre = models.CharField(max_length=250)
    descripcion = models.TextField(default='sin descripción')
    fecha = models.DateField(default='1900-01-01')
    usuarios = models.ManyToManyField(User)

    def __str__(self):
        return self.nombre + " " + str(self.fecha)

class Valoraciones(models.Model):
    producto= models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    puntuacion = models.IntegerField()
    comentario = models.TextField(default='sin comentario')

    def __str__(self):
        return self.producto.nombre + " " + self.usuario.username + " " + str(self.puntuacion) + " " + self.comentario

