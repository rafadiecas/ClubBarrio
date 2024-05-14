from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.sites import requests
from django.core.mail import EmailMessage
from django.db.models import Count, Q, When, Value
from django.db.models.functions import Coalesce
from django.forms import IntegerField
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage, send_mail
from django.db.models import Count, Q, Sum
from django.shortcuts import render, redirect
from django.utils.datetime_safe import datetime, date
import re
import requests
from collections import defaultdict
from .models import *
from django.core.paginator import Paginator
from django.http import Http404
from django.http import JsonResponse
from .decorator import user_required, rol_requerido
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.db.models import Count, F, ExpressionWrapper, FloatField, Sum, QuerySet
from itertools import chain

from .models import Partido
from django.conf import settings

from django.db.models import F, Count, Case, When, Value, IntegerField

# Create your views here.

def pagina_inicio(request):
    list_noticias = Noticias.objects.all().order_by('-id')
    list_noticias = list_noticias[0:3]
    #mail = EmailMessage('Asunto', 'Cuerpo del mensaje', to=['safaclubbasket@gmail.com'])
    #mail.send()
    return render(request, 'inicio.html', {'noticias': list_noticias})

def pagina_tienda(request):
    list_productos = Producto.objects.all()
    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(list_productos, 9) # Muestra la cantidad de productor por pagina
        list_productos = paginator.page(page)
    except:
        raise Http404

    data = {
        'entity': list_productos,
        'paginator': paginator
    }

    return render(request, 'tienda.html', data)

def pagina_noticias(request):
    list_noticias = Noticias.objects.all().order_by('-id')
    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(list_noticias, 3)
        list_noticias = paginator.page(page)
    except:
        raise Http404

    data = {
        'entity': list_noticias,
        'paginator': paginator
    }

    usuario = request.user
    envio_datos_barra(data, request, usuario)
    return render(request, 'Noticias.html', data)


def envio_datos_barra(data, request, usuario):
    if usuario.is_authenticated:
        if usuario.rol == 'Tutor':
            tutor = TutorLegal.objects.get(usuario_id=usuario.id)
            hijos = Jugador.objects.filter(tutorLegal_id=tutor.id)
            data['hijos'] = hijos
            if len(hijos) == 0:
                data['hijo_existe'] = True
        elif usuario.rol == 'Jugador':
            jugador = Jugador.objects.get(usuario_id=usuario.id)
            data['jugador'] = jugador
        elif usuario.rol == 'Entrenador':
            equipos = equipos_entrenador(request)
            data['equipos_entrenador'] = equipos




def pagina_contacto(request):
    usuario = request.user
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        asunto = request.POST.get('asunto') + " - Enviado por: " + nombre +"-"+ email
        mensaje = "Enviado por: " + nombre + "<br><br>" + "Email: " + email + "<br><br>"+ "Mensaje: " + request.POST.get('mensaje')
        correo = EmailMessage(
            asunto,
            mensaje,
            to=[settings.EMAIL_HOST_USER]
        )
        correo.content_subtype = "html"
        correo.send()
        return JsonResponse({'success': 'Mensaje enviado con éxito'})
    return render(request, 'contacto.html')


#@user_required
#@rol_requerido('Administrador')
def administrador(request):
    return render(request, 'administrador.html')

def usuarios(request):
    lista_usuarios = User.objects.all()
    return render(request, 'lista_usuarios.html', {'usuarios': lista_usuarios})

def validar_contraseña(usuario, contraseña_actual, nueva_contraseña, confirmacion_contraseña):
    errores = []
    if not usuario.check_password(contraseña_actual):
        errores.append("La contraseña actual es incorrecta")
    if nueva_contraseña != confirmacion_contraseña:
        errores.append("Las contraseñas no coinciden")
    largo = re.compile(r'.{8,}')
    digito = re.compile(r'\d+')
    letra_may = re.compile(r'[A-Z]+')
    letra_min = re.compile(r'[a-z]+')
    validaciones = [largo, digito, letra_may, letra_min]
    for v in validaciones:
        if not v.search(nueva_contraseña):
            errores.append(
                "La contraseña debe tener al menos 8 caracteres, una letra mayúscula, una minúscula y un número")
            break
    return errores

def perfil(request):
    usuario = User.objects.get(id=request.user.id)
    notificaciones = Notificaciones.objects.get(usuario=usuario)
    roles_map = {
        'Tutor': TutorLegal,
        'Jugador': Jugador,
        'Entrenador': Entrenador
    }

    usuario = request.user
    data={}
    envio_datos_barra(data,request,usuario)

    if usuario.rol in roles_map:
        perfil = roles_map[usuario.rol].objects.get(usuario_id=usuario.id)

        if request.method == 'POST':
            perfil.nombre = request.POST.get('nombre')
            perfil.apellidos = request.POST.get('apellidos')
            perfil.save()

        if usuario.rol == 'Jugador':
            equipo = perfil.equipo  # Obtén el equipo asociado al perfil si el usuario es un jugador
            jugador = Jugador.objects.get(usuario_id=usuario.id)
            return render(request, 'profile.html', {'perfil': perfil, 'equipo': equipo, 'jugador':jugador, 'notificaciones': notificaciones,"data":data})

        return render(request, 'profile.html', {'perfil': perfil, 'notificaciones': notificaciones,"data":data})

    return render(request, 'profile.html', {'notificaciones': notificaciones,"data":data})

def perfil_pass(request):
    usuario = request.user
    if request.method == 'POST':
        contraseña_actual = request.POST.get('password_actual')
        nueva_contraseña = request.POST.get('new_password')
        confirmacion_contraseña = request.POST.get('confirmacion_password')

        errores = validar_contraseña(usuario, contraseña_actual, nueva_contraseña, confirmacion_contraseña)
        if errores:
            return JsonResponse({'errores': errores}, status=400)

        usuario.password = make_password(nueva_contraseña)
        usuario.save()  # Guarda el usuario después de cambiar la contraseña
        update_session_auth_hash(request, usuario)  # Actualiza la sesión del usuario
        notificaciones = Notificaciones.objects.get(usuario=request.user)
        if notificaciones.password_change:
            send_mail(
                'Cambio de contraseña en ClubBarrioApp',
                'Has cambiado tu contraseña. Si no has realizado este cambio, por favor, contacta con nosotros.',
                'safaclubbasket@gmail.com',
                [request.user.email],
                fail_silently=False,
            )

        return JsonResponse({'success': 'Contraseña cambiada con éxito'})

    # Si el método no es POST, redirige al usuario a la página de perfil (o donde quieras)
    return redirect('perfil')

# @login_required
def notificaciones(request):
    if request.method == 'POST':

        notificaciones = Notificaciones.objects.get(usuario=request.user)

        # Actualiza los campos de notificación basándose en los valores de los checkbox
        notificaciones.password_change = 'passwordChange' in request.POST
        notificaciones.weekly_newsletter = 'weeklyNewsletter' in request.POST
        notificaciones.new_training = 'newTraining' in request.POST


        notificaciones.save()

        return JsonResponse({'success': 'Notificaciones actualizadas con éxito'})
        # return redirect('perfil')

    # Si el método no es POST, redirige al usuario a la página de perfil (o donde quieras)
    return redirect('perfil')



def new_user(request):
    Users = User.objects.all()
    Equipos = Equipo.objects.filter(es_safa=True)
    Tutores = TutorLegal.objects.all()
    roles = Role.labels[:-1]
    if request.method == 'GET':

        return render(request, "crear_usuario.html",
                      {'Users': Users, 'Equipos': Equipos, 'Tutores': Tutores, 'roles': roles})
    else:

        username = request.POST.get('username')
        rol = Role.value_for_label(request.POST.get('rol'))
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')

        errors = filtro(email, fecha_nacimiento,rol, username, password, password2)

        if len(errors) != 0:
            return render(request, "crear_usuario.html",
                          {"errores": errors, "username": username, "email": email, "roles": roles,
                           "fecha_nacimiento": fecha_nacimiento, "Equipos": Equipos, "Tutores": Tutores})
        else:
            new = User.objects.create(username=username, password=make_password(password), email=email, rol=rol,
                                      fecha_nacimiento=fecha_nacimiento)
            new.save()

    if request.POST.get('rol') == 'Tutor':
        new_padre = TutorLegal()
        new_padre.nombre = request.POST.get('nombre')
        new_padre.apellidos = request.POST.get('apellidos')
        new_padre.usuario_id = new.id
        new_padre.save()

    if request.POST.get('rol') == 'Entrenador':
        new_entrenador = Entrenador()
        new_entrenador.nombre = request.POST.get('nombre')
        new_entrenador.apellidos = request.POST.get('apellidos')
        new_entrenador.usuario_id = new.id
        new_entrenador.save()

        list_equipos = request.POST.getlist('equipos')

        for e in list_equipos:
            equipo = Equipo.objects.get(id=e)
            equipo.entrenadores.add(new_entrenador)

    if request.POST.get('rol') == 'Jugador':
        new_jugador = Jugador()
        new_jugador.nombre = request.POST.get('nombre')
        new_jugador.apellidos = request.POST.get('apellidos')
        new_jugador.usuario_id = new.id
        new_jugador.equipo_id = request.POST.get('equipo')
        new_jugador.tutorLegal_id = request.POST.get('tutor')
        new_jugador.save()

    return redirect('/ClubBarrioApp/administrador/usuarios/')


def filtro(email, fecha_nacimiento, rol, username, password = "Contrasena1", password2 = "Contrasena1"):
    errors = []
    if password != password2:
        errors.append("Las contraseñas no coinciden")
    existe_usuario = User.objects.filter(username=username).exists()
    if existe_usuario:
        errors.append("Ya existe un usuario con ese nombre")
    existe_mail = User.objects.filter(email=email).exists()
    if existe_mail:
        errors.append("Ya existe un usuario con ese email")
    fecha = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
    diferencia = datetime.now() - fecha
    if diferencia.days < 6570 and rol != 'Jugador':
        errors.append("El usuario debe ser mayor de edad")
    largo = re.compile(r'.{8,}')
    digito = re.compile(r'\d+')
    letra_may = re.compile(r'[A-Z]+')
    letra_min = re.compile(r'[a-z]+')
    validaciones = [largo, digito, letra_may, letra_min]
    for v in validaciones:
        if not v.search(password):
            errors.append(
                "La contraseña debe tener al menos 8 caracteres, una letra mayúscula, una minúscula y un número")
            break
    return errors


def elimina_usuario(request, id):
    usuario = User.objects.get(id=id)
    usuario.delete()
    return redirect('usuarios')

def registro(request):
    if request.method == 'GET':
        return render(request, 'registro.html')
    else:
        nombre_usuario = request.POST.get('nombre_usuario')
        email = request.POST.get('email')
        contrasenya = request.POST.get('contrasenya')
        repetirContrasenya = request.POST.get('repetirContrasenya')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        rol = "Usuario"

        errores = filtro(email, fecha_nacimiento, 'Usuario', nombre_usuario, contrasenya, repetirContrasenya)


        if len(errores) != 0:
            return render(request, 'registro.html', {"errores": errores, "nombre_usuraio": nombre_usuario, "email": email, "fecha_nacimiento": fecha_nacimiento})
        else:
            usuario = User.objects.create(username=nombre_usuario, password=make_password(contrasenya), email=email,
                                          fecha_nacimiento=fecha_nacimiento, rol=rol)
            usuario.save()

            # Crea un objeto Notificaciones para el nuevo usuario
            notificaciones = Notificaciones.objects.create(id=usuario.id, usuario=usuario, password_change=False,
                                                           weekly_newsletter=False, new_training=False)
            notificaciones.save()

            mensaje = ("Bienvenido a SafaClubBasket, " + nombre_usuario + ". Tu registro se ha completado con éxito."
                       + "<br><br>" + "Tus credenciales de acceso son: " + "<br>"
                       + "Usuario: " + nombre_usuario + "<br>" + "Contraseña: " + contrasenya + "<br><br>" + "Un saludo, SafaClubBasket.")
            correo = EmailMessage('Registro en SafaClubBasket', mensaje, to=[email])
            correo.content_subtype = "html"
            correo.send()
            return JsonResponse({'success': 'Usuario registrado con éxito'})
            # return redirect('login')

def logear(request):
    if request.method == 'POST':
        nombre_usuario = request.POST.get('nombre_usuario')
        contrasenya = request.POST.get('contrasenya')

        user = authenticate(request, username=nombre_usuario, password=contrasenya)

        if user is not None:
            login(request, user)

            if user.rol== "Administrador":
                return redirect('administrador')

            elif user.rol == "Usuario" or user.rol == "Tutor":
                return redirect('usuario')
            elif user.rol == "Jugador":
                return redirect('inicio_jugador')

            elif user.rol == "Entrenador":
                return redirect('entrenador')

            # Redirección tras un login exitoso
            return redirect('inicio')
        else:
            # Mensaje de error si la autenticación falla
            return render(request, 'login.html',{"error": "Usuario o contraseña incorrectos", "nombre_usuario": nombre_usuario})

    # Mostrar formulario de login para método GET
    return render(request, 'login.html')

def desloguear(request):
    logout(request)
    return redirect('login')


def edita_usuario(request, id):
    usuario = User.objects.get(id=id)
    Equipos = Equipo.objects.all()
    Tutores = TutorLegal.objects.all()
    roles = Role.labels[:-1]
    rol = usuario.rol

    if request.method == 'GET':
        if usuario.rol == 'Jugador':
            tutor = Jugador.objects.get(usuario_id=id).tutorLegal
            equipo = Jugador.objects.get(usuario_id=id).equipo
            jugador = Jugador.objects.get(usuario_id=id)
            return render(request, 'editar_usuarios.html',
                          {'usuario': usuario, 'Equipos': Equipos, 'Tutores': Tutores, 'roles': roles, 'tutor': tutor,
                           'equipo': equipo, 'datos': jugador})
        if usuario.rol == 'Entrenador':
            id_equipos = []
            total_equipos = Equipo.objects.all()
            for e in total_equipos:
                if e.entrenadores.filter(usuario_id=usuario.id).exists():
                    id_equipos.append(e.id)
            entrenador = Entrenador.objects.filter(usuario_id=usuario.id)
            return render(request, 'editar_usuarios.html',
                          {'usuario': usuario, 'Equipos': Equipos, 'roles': roles, 'id_equipos': id_equipos,
                           'Tutores': Tutores})
        if usuario.rol == 'Tutor':
            tutor = TutorLegal.objects.get(usuario_id=usuario.id)
            tarifas = tarifa.labels
            return render(request, 'editar_usuarios.html',
                          {'usuario': usuario, 'roles': roles, 'datos': tutor, 'Tutores': Tutores, 'Equipos': Equipos, 'tarifas': tarifas})

        return render(request, 'editar_usuarios.html',
                      {'usuario': usuario, 'roles': roles, 'Tutores': Tutores, 'Equipos': Equipos})
    else:

        usuario.username = request.POST.get('username')
        usuario.email = request.POST.get('email')
        usuario.fecha_nacimiento = request.POST.get('fecha_nacimiento')
        usuario.save()

        if usuario.rol == 'Tutor':
            tutor = TutorLegal.objects.get(usuario_id=id)
            tutor.nombre = request.POST.get('nombre')
            tutor.apellidos = request.POST.get('apellidos')
            tutor.tarifa = tarifa.value_for_label(request.POST.get('tarifa'))
            if request.POST.get('is_active') == 'on':
                tutor.es_activo = True
            else:
                tutor.es_activo = False
            tutor.save()
        if usuario.rol == 'Entrenador':
            entrenador = Entrenador.objects.get(usuario_id=id)
            entrenador.nombre = request.POST.get('nombre')
            entrenador.apellidos = request.POST.get('apellidos')
            entrenador.save()
            list_equipos = request.POST.getlist('equipos')
            for e in list_equipos:
                equipo = Equipo.objects.get(id=e)
                equipo.entrenadores.add(entrenador)
        if usuario.rol == 'Jugador':
            jugador = Jugador.objects.get(usuario_id=id)
            jugador.nombre = request.POST.get('nombre')
            jugador.apellidos = request.POST.get('apellidos')
            jugador.equipo_id = request.POST.get('equipo')
            jugador.tutorLegal_id = request.POST.get('tutor')
            if request.POST.get('is_active') == 'on':
                jugador.es_activo = True
            else:
                jugador.es_activo = False
            jugador.save()

        return redirect('usuarios')
def equipos_listado(request):
    lista_equipos = Equipo.objects.all()
    return render(request, 'lista_equipos.html', {"equipos":lista_equipos})

def crear_equipo(request):
    if request.method == 'GET':
        lista_categorias = Categoria.objects.all()
        entrenadores = Entrenador.objects.all()
        return render(request, 'crear_equipo.html', {'lista_categorias': lista_categorias, 'entrenadores': entrenadores})
    else:
        equipo_nuevo= Equipo()
        equipo_nuevo.nombre= request.POST.get('nombre')
        equipo_nuevo.escudo = request.POST.get('escudo')
        if request.POST.get('is_safa') == 'on':
            equipo_nuevo.es_safa = True
        else:
            equipo_nuevo.es_safa = False
        equipo_nuevo.categoria= Categoria.objects.get(id=int(request.POST.get('categoria')))
        equipo_nuevo.save()

        lista_entrenadores = request.POST.getlist('entrenadores')
        for e in lista_entrenadores:
            equipo_nuevo.entrenadores.add(e)

        return redirect('equipos')

def editar_equipo(request, id):
    equipo = Equipo.objects.get(id=id)
    if request.method == 'GET':
        lista_categorias = Categoria.objects.all()
        entrenadores = Entrenador.objects.all()
        id_entrenadores = equipo.entrenadores.values_list('id', flat=True)
        es_safa = equipo.es_safa
        return render(request, 'crear_equipo.html', {'equipo':equipo, 'id_entrenadores':id_entrenadores, 'lista_categorias': lista_categorias, 'entrenadores': entrenadores, 'es_safa': es_safa, 'modo_edicion': True})
    else:
        equipo.nombre = request.POST.get('nombre')
        equipo.escudo = request.POST.get('escudo')
        equipo.categoria = Categoria.objects.get(id=int(request.POST.get('categoria')))
        if request.POST.get('is_safa') == 'on':
            equipo.es_safa = True
        else:
            equipo.es_safa = False
        equipo.save()

        lista_entrenadores = request.POST.getlist('entrenadores')
        equipo.entrenadores.clear()
        for e in lista_entrenadores:
            equipo.entrenadores.add(e)

        return redirect('equipos')

def elimina_equipo(request, id):
    equipo = Equipo.objects.get(id=id)
    equipo.delete()
    return redirect('equipos')

def entrenamientos_listado(request):
    usuario = request.user
    if usuario.rol == 'Entrenador':
        entrenador = Entrenador.objects.get(usuario_id=usuario.id)
        lista_entrenamientos = Entrenamiento.objects.filter(
            Q(entrenador=entrenador) & Q(equipo__entrenadores=entrenador))
    else:
        lista_entrenamientos = Entrenamiento.objects.all()

    return render(request, 'lista_entrenamiento.html', {"lista_entrenamientos":lista_entrenamientos})

def entrenamientos_listado_entrenador(request):
    usuario = request.user
    # entrenador = Entrenador.objects.get(usuario_id=usuario.id)
    equipo = Equipo.objects.get(entrenadores__usuario__id=usuario.id)
    lista_entrenamientos = Entrenamiento.objects.filter(entrenador__equipo__id=equipo.id)
    return render(request, 'lista_entrenamiento.html', {"lista_entrenamientos":lista_entrenamientos})
def crear_entrenamiento(request):
    if request.method == 'GET':
        lista_entrenadores = Entrenador.objects.all()
        lista_lugares_entrenamiento = LugarEntrenamiento.objects.all()
        lista_equipos = Equipo.objects.filter(es_safa=True)
        return render(request, 'crear_entrenamiento.html',
                      {'lista_entrenadores': lista_entrenadores, 'lista_lugares_entrenamiento': lista_lugares_entrenamiento, 'lista_equipos': lista_equipos})
    else:
        entrenamiento_nuevo = Entrenamiento()
        entrenamiento_nuevo.fecha = request.POST.get('fecha')
        entrenamiento_nuevo.hora = request.POST.get('hora')
        entrenamiento_nuevo.entrenador = Entrenador.objects.get(id=int(request.POST.get('entrenador')))
        entrenamiento_nuevo.lugarEntrenamiento = LugarEntrenamiento.objects.get(id=int(request.POST.get('lugarEntrenamiento')))
        entrenamiento_nuevo.equipo = Equipo.objects.get(id=int(request.POST.get('equipo')))
        entrenamiento_nuevo.save()

        # Obtén todos los jugadores que pertenecen al equipo
        jugadores_equipo = Jugador.objects.filter(equipo=entrenamiento_nuevo.equipo).select_related('usuario')

        for jugador in jugadores_equipo:
            try:
                notificaciones = Notificaciones.objects.get(usuario=jugador.usuario)
                if notificaciones.new_training:  # Verifica si las notificaciones del jugador están activadas
                    send_mail(
                        'Nuevo entrenamiento en ClubBarrioApp',
                        'Se ha programado un nuevo entrenamiento para tu equipo. Inicia sesión para ver los detalles.',
                        'safaclubbasket@gmail.com',
                        [jugador.usuario.email],
                        fail_silently=False,
                    )
            except Notificaciones.DoesNotExist:
                pass

            # Obtén el tutor del jugador
            tutor = jugador.tutorLegal
            if tutor is not None:
                try:
                    notificaciones_tutor = Notificaciones.objects.get(usuario=tutor.usuario)
                    if notificaciones_tutor.new_training:  # Verifica si las notificaciones del tutor están activadas
                        send_mail(
                            'Nuevo entrenamiento en ClubBarrioApp',
                            'Se ha programado un nuevo entrenamiento para el equipo de tu hijo/a. Inicia sesión para ver los detalles.',
                            'safaclubbasket@gmail.com',
                            [tutor.usuario.email],
                            fail_silently=False,
                        )
                except Notificaciones.DoesNotExist:
                    pass

        return redirect('entrenamientos_listado')
def editar_entrenamiento(request, id):
    entrenamiento = Entrenamiento.objects.get(id=id)
    if request.method == 'GET':
        lista_entrenadores = Entrenador.objects.all()
        lista_lugares_entrenamiento = LugarEntrenamiento.objects.all()
        lista_equipos = Equipo.objects.filter(es_safa=True)
        return render(request, 'crear_entrenamiento.html',
                      {'entrenamiento': entrenamiento, 'lista_entrenadores': lista_entrenadores, 'lista_lugares_entrenamiento': lista_lugares_entrenamiento, 'modo_edicion': True,'lista_equipos': lista_equipos})
    else:
        entrenamiento.fecha = request.POST.get('fecha')
        entrenamiento.hora = request.POST.get('hora')
        entrenamiento.entrenador = Entrenador.objects.get(id=int(request.POST.get('entrenador')))
        entrenamiento.lugarEntrenamiento = LugarEntrenamiento.objects.get(id=int(request.POST.get('lugarEntrenamiento')))
        entrenamiento.equipo = Equipo.objects.get(id=int(request.POST.get('equipo')))
        entrenamiento.save()

        return redirect('entrenamientos_listado')

def elimina_entrenamiento(request, id):
    entrenamiento = Entrenamiento.objects.get(id=id)
    entrenamiento.delete()
    if request.user.rol == 'Entrenador':
        return redirect('entrenador')
    else:
        return redirect('entrenamientos_listado')




def lista_noticias(request):
    lista_noticias = Noticias.objects.all()
    return render(request, 'lista_noticias.html', {"noticias":lista_noticias})

def crear_noticia(request):
    if request.method == 'GET':
        return render(request, 'crear_noticias.html')
    else:
        noticia_nueva = Noticias()
        noticia_nueva.titulo = request.POST.get('titulo')
        noticia_nueva.articulo = request.POST.get('articulo')
        noticia_nueva.url_imagen = request.POST.get('url_imagen')
        noticia_nueva.administrador_id = 1
        noticia_nueva.save()

        # Obtén todos los usuarios que tienen habilitado el check de noticias
        usuarios_con_noticias = Notificaciones.objects.filter(weekly_newsletter=True).select_related('usuario')

        for notificacion in usuarios_con_noticias:
            try:
                if notificacion.new_training:  # Verifica si las notificaciones del usuario están activadas
                    send_mail(
                        'Nueva noticia en ClubBarrioApp',
                        'Se ha publicado una nueva noticia. Inicia sesión para verla.',
                        'safaclubbasket@gmail.com',
                        [notificacion.usuario.email],
                        fail_silently=False,
                    )
            except Notificaciones.DoesNotExist:
                pass

        return redirect('noticias_admin')

def elimina_noticia(request, id):
    noticia = Noticias.objects.get(id=id)
    noticia.delete()
    return redirect('noticias_admin')

def editar_noticia(request,id):
    noticia = Noticias.objects.get(id=id)
    if request.method == 'GET':
        return render(request, 'crear_noticias.html', {'noticia':noticia, 'modo_edicion': True})
    else:
        noticia.titulo = request.POST.get('titulo')
        noticia.articulo = request.POST.get('articulo')
        noticia.url_imagen = request.POST.get('url_imagen')
        noticia.save()
        return redirect('noticias_admin')

def estadisticas_jugador_listado(request):
    lista_estadisticas_jugador = EstadisticasJugador.objects.all()
    return render(request, 'lista_estadisticas_jugador.html', {"lista_estadisticas_jugador":lista_estadisticas_jugador})
def crear_estadisticas_jugador(request):
    if request.method == 'GET':
        lista_partidos = Partido.objects.filter(Q(equipo1__es_safa=True) | Q(equipo2__es_safa=True)).order_by('-fecha')
        lista_jugador = Jugador.objects.all()
        return render(request, 'crear_estadisticas_jugador.html',
                      {'lista_partidos': lista_partidos, 'lista_jugador': lista_jugador})
    else:
        estadisticas_jugador_nuevo = EstadisticasJugador()
        estadisticas_jugador_nuevo.puntos = request.POST.get('puntos')
        estadisticas_jugador_nuevo.minutos = request.POST.get('minutos')
        estadisticas_jugador_nuevo.rebotes = request.POST.get('rebotes')
        estadisticas_jugador_nuevo.faltas = request.POST.get('minutos')
        estadisticas_jugador_nuevo.asistencias = request.POST.get('asistencias')
        estadisticas_jugador_nuevo.jugador = Jugador.objects.get(id=int(request.POST.get('jugadores')))
        estadisticas_jugador_nuevo.partido = Partido.objects.get(id=int(request.POST.get('partido')))
        estadisticas_jugador_nuevo.save()

        return redirect('estadisticas_jugador_listado')
def editar_estadisticas_jugador(request, id):
    estadisticas_jugador = EstadisticasJugador.objects.get(id=id)
    if request.method == 'GET':
        lista_entrenadores = Entrenador.objects.all()
        lista_partidos = Partido.objects.all()
        return render(request, 'crear_estadisticas_jugador.html',
                      {'estadisticas_jugador': estadisticas_jugador, 'lista_entrenadores': lista_entrenadores, 'lista_partidos': lista_partidos, 'modo_edicion': True})
    else:
        estadisticas_jugador.puntos = request.POST.get('puntos')
        estadisticas_jugador.minutos = request.POST.get('minutos')
        estadisticas_jugador.rebotes = request.POST.get('rebotes')
        estadisticas_jugador.faltas = request.POST.get('minutos')
        estadisticas_jugador.asistencias = request.POST.get('asistencias')
        estadisticas_jugador.partido = Partido.objects.get(id=int(request.POST.get('partido')))
        estadisticas_jugador.save()

        return redirect('estadisticas_jugador_listado')

def elimina_estadisticas_jugador(request, id):
    estadistica_jugador = EstadisticasJugador.objects.get(id=id)
    estadistica_jugador.delete()
    return redirect('estadistica_jugador_listado')
def partidos_listado(request):
    lista_partidos = Partido.objects.all()
    return render(request, 'lista_partidos.html', {"lista_partidos":lista_partidos})

def crear_partido(request):
    if request.method == 'GET':
        lista_equipos = Equipo.objects.all()
        temporadas = Temporada.objects.all()
        return render(request, 'crear_partidos.html', {'lista_equipos': lista_equipos, 'temporadas': temporadas})
    else:
        partido_nuevo = Partido()
        partido_nuevo.fecha = request.POST.get('fecha')
        partido_nuevo.hora = request.POST.get('hora')
        partido_nuevo.lugar = request.POST.get('lugar')
        partido_nuevo.puntos_equipo1 = request.POST.get('puntos_equipo1')
        partido_nuevo.puntos_equipo2 = request.POST.get('puntos_equipo2')
        partido_nuevo.equipo1 = Equipo.objects.get(id=int(request.POST.get('equipo_local')))
        partido_nuevo.equipo2 = Equipo.objects.get(id=int(request.POST.get('equipo_visitante')))
        partido_nuevo.temporada = Temporada.objects.get(id=int(request.POST.get('temporada')))
        partido_nuevo.jornada = request.POST.get('jornada')
        if request.POST.get('equipo_local') == request.POST.get('equipo_visitante'):
            errores = ["Los equipos no pueden ser iguales"]
            return render(request, 'crear_partidos.html', {'errores': errores, 'lista_equipos': Equipo.objects.all(), 'temporadas': Temporada.objects.all()})
        else:
            partido_nuevo.save()
            return redirect('partidos_listado')

def elimina_partido(request, id):
    partido = Partido.objects.get(id=id)
    partido.delete()
    return redirect('partidos_listado')

def editar_partido(request, id):
    partido = Partido.objects.get(id=id)
    if request.method == 'GET':
        lista_equipos = Equipo.objects.all()
        temporadas = Temporada.objects.all()
        return render(request, 'crear_partidos.html', {'partido': partido, 'lista_equipos': lista_equipos, 'temporadas': temporadas, 'modo_edicion': True})
    else:
        partido.fecha = request.POST.get('fecha')
        partido.hora = request.POST.get('hora')
        partido.lugar = request.POST.get('lugar')
        partido.puntos_equipo1 = request.POST.get('puntos_equipo1')
        partido.puntos_equipo2 = request.POST.get('puntos_equipo2')
        partido.equipo1 = Equipo.objects.get(id=int(request.POST.get('equipo_local')))
        partido.equipo2 = Equipo.objects.get(id=int(request.POST.get('equipo_visitante')))
        partido.temporada = Temporada.objects.get(id=int(request.POST.get('temporada')))
        partido.jornada = request.POST.get('jornada')
        if request.POST.get('equipo_local') == request.POST.get('equipo_visitante'):
            errores = ["Los equipos no pueden ser iguales"]
            return render(request, 'crear_partidos.html', {'errores': errores, 'lista_equipos': Equipo.objects.all(), 'temporadas': Temporada.objects.all()})
        else:
            partido.save()
            return redirect('partidos_listado')


def lista_tienda(request):
    lista_productos = ProductoTalla.objects.all()
    return render(request, 'lista_productos.html', {"lista_productos":lista_productos})

def crear_producto(request):
    if request.method == 'GET':
        tallas = Talla.objects.all()
        tipos = Tipo.objects.all()
        return render(request, 'crear_productos.html', {'tallas': tallas, 'tipos': tipos})
    else:
        producto_nuevo = Producto()
        producto_nuevo.nombre = request.POST.get('nombre')
        producto_nuevo.precio = request.POST.get('precio')
        producto_nuevo.tipo = Tipo.objects.get(id=int(request.POST.get('tipo')))
        producto_nuevo.url_imagen = request.POST.get('url_imagen')
        producto_nuevo.descripcion = request.POST.get('descripcion')
        producto_nuevo.save()
        producto_talla_nuevo = ProductoTalla()
        producto_talla_nuevo.producto = producto_nuevo
        producto_talla_nuevo.talla = Talla.objects.get(id=int(request.POST.get('talla')))
        producto_talla_nuevo.stock = request.POST.get('stock')
        producto_talla_nuevo.save()
        return redirect('lista_tienda')

def crear_producto_talla(request):
    if request.method == 'GET':
        tallas = Talla.objects.all()
        productos = Producto.objects.all()
        return render(request, 'crear_talla.html', {'tallas': tallas, 'productos': productos})
    else:
        try:
            producto_talla = ProductoTalla.objects.get(producto_id=int(request.POST.get('producto')), talla=request.POST.get('talla'))
            errores = []
            errores.append("Ya existe ese producto con esa talla")
            return render(request, 'crear_talla.html', {'errores': errores, 'tallas': Talla.objects.all(), 'productos': Producto.objects.all()})
        except ObjectDoesNotExist:
            productoTalla_nuevo = ProductoTalla()
            productoTalla_nuevo.producto = Producto.objects.get(id=int(request.POST.get('producto')))
            productoTalla_nuevo.talla = Talla.objects.get(id=int(request.POST.get('talla')))
            productoTalla_nuevo.stock = request.POST.get('stock')
            productoTalla_nuevo.save()
            return redirect('lista_tienda')

def elimina_producto(request, id):
    producto = Producto.objects.get(id=id)
    producto.delete()
    return redirect('lista_tienda')

def edita_producto(request, id):
    productotalla = ProductoTalla.objects.get(id=id)
    producto = productotalla.producto
    if request.method == 'GET':
        tallas = Talla.objects.all()
        tipos = Tipo.objects.all()
        return render(request, 'crear_productos.html', {'producto': producto, 'tallas': tallas, 'tipos': tipos, 'modo_edicion': True, 'productotalla': productotalla})
    else:
        tallas = Talla.objects.all()
        tipos = Tipo.objects.all()
        producto.nombre = request.POST.get('nombre')
        producto.precio = float(request.POST.get('precio'))
        producto.tipo = Tipo.objects.get(id=int(request.POST.get('tipo')))
        producto.url_imagen = request.POST.get('url_imagen')
        producto.save()
        new_talla = Talla.objects.get(id=int(request.POST.get('talla')))
        if productotalla.talla == new_talla:
            productotalla.stock = request.POST.get('stock')
            productotalla.save()
        else:
            try:
                producto_talla = ProductoTalla.objects.get(producto_id=producto.id, talla=new_talla)
                errores = []
                errores.append("Ya existe ese producto con esa talla")
                return render(request, 'crear_productos.html', {'producto': producto, 'tallas': tallas, 'tipos': tipos, 'modo_edicion': True, 'productotalla': productotalla, 'errores': errores})
            except ObjectDoesNotExist:
                productotalla.talla = new_talla
                productotalla.stock = request.POST.get('stock')
                productotalla.save()

        return redirect('lista_tienda')


def pagina_usuario(request):
    list_noticias = Noticias.objects.all().order_by('-id')
    list_noticias = list_noticias[0:3]
    list_partidos = Partido.objects.all()
    usuario = request.user
    equipos_por_categoria = {}

    for equipo in Equipo.objects.all():
        if equipo.es_safa:
            plazas_libres = 20 - Jugador.objects.filter(equipo_id=equipo.id).count()
            if plazas_libres > 0:
                equipo_info = {'equipo': equipo, 'plazas_libres': plazas_libres}
                categoria_equipo = equipo.categoria.tipo
                if categoria_equipo in equipos_por_categoria:
                    equipos_por_categoria[categoria_equipo].append(equipo_info)
                else:
                    equipos_por_categoria[categoria_equipo] = [equipo_info]

    if usuario.rol == 'Tutor':
        tutor = TutorLegal.objects.get(usuario_id=usuario.id)
        hijos = Jugador.objects.filter(tutorLegal_id=tutor.id)
        list_partidos =[]
        for hijo in hijos:
            partidos = Partido.objects.filter(Q(equipo1=hijo.equipo) | Q(equipo2=hijo.equipo))
            for partido in partidos:
                if partido not in list_partidos:
                    list_partidos.append(partido)
        if len(hijos) == 0:
            return render(request, 'inicio_usuario_tutor.html', {'noticias': list_noticias, 'partidos': list_partidos, 'hijo_existe': True, 'equipos_por_categoria': equipos_por_categoria})
        return render(request, 'inicio_usuario_tutor.html', {'noticias': list_noticias, 'partidos': list_partidos, 'hijos': hijos, 'equipos_por_categoria': equipos_por_categoria})
    else:


        return render(request, 'inicio_usuario_tutor.html', {'noticias': list_noticias, 'partidos': list_partidos, 'equipos_por_categoria': equipos_por_categoria})

def tarifas(request):
    return render(request, 'tarifas.html')

def inscripciones(request):
    if request.method == 'GET':
        return render(request, 'inscripcion_tarifa.html')
    else:
        usuario = request.user
        usuario.rol = 'Tutor'
        usuario.save()
        tutor = TutorLegal()
        tutor.usuario = usuario
        tutor.nombre = request.POST.get('nombre')
        tutor.apellidos = request.POST.get('apellidos')
        tutor.tarifa = request.POST.get('tarifa_seleccionada')
        tutor.save()

        mensaje = ("Gracias por suscribirte, " + usuario.username + ". Tu suscripción se ha completado con éxito."
                   + "<br><br>" + "Algunos datos importantes: " + "<br>"
                   + "Tarifa selecionada: " + tutor.tarifa + "<br>" + "Pagos los dias " + str(datetime.now().day)+ " de cada mes." + "<br><br>" + "Un saludo, SafaClubBasket.")
        correo = EmailMessage('Suscripción en SafaClubBasket', mensaje, to=[usuario.email])
        correo.content_subtype = "html"
        correo.send()

        return redirect('usuario')
def terminos_y_servicios(request):
    return render(request, 'terminos_y_servicios.html')

def lista_hijos(request):
    usuario = request.user
    tutor = TutorLegal.objects.get(usuario_id=usuario.id)
    hijos = Jugador.objects.filter(tutorLegal_id=tutor.id)
    if len(hijos) == 0:
        return render(request, 'lista_hijos.html', {'hijo_existe': True})
    return render(request, 'lista_hijos.html', {'hijos': hijos})

def crea_hijos(request):
    usuario = request.user
    tutor = TutorLegal.objects.get(usuario_id=usuario.id)
    hijos = Jugador.objects.filter(tutorLegal_id=tutor.id)
    hijo = User()
    jugador = Jugador()
    if request.method == 'GET':
        return render(request, 'crear_hijo.html', {'modo_edicion': False})
    else:


        if 'boton' in request.POST and request.POST['boton'] == 'seleccion_datos':

            username = request.POST.get('username')
            rol = 'Jugador'
            email = request.POST.get('email')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')
            fecha_nacimiento = request.POST.get('fecha_nacimiento')
            fecha = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
            diferencia = datetime.now() - fecha
            lista_equipos=[]
            nombre = request.POST.get('nombre')
            apellidos = request.POST.get('apellidos')
            errors = filtro(email, fecha_nacimiento, rol, username, password, password2)

            if(len(errors) == 0):
                datos= {'username': username, 'rol': rol, 'email': email, 'password': password, 'fecha_nacimiento': fecha_nacimiento, 'nombre': nombre, 'apellidos': apellidos}
                request.session['datos'] = datos


            categoria = calculador_categoria(diferencia, errors)

            if (tutor.tarifa == 'BASE' and len(hijos) >= 1) or (tutor.tarifa == 'PLUS' and len(hijos) >= 3) or (
                    tutor.tarifa == 'PREMIUM' and len(hijos) >= 5):
                errors.append("No puedes añadir más hijos")

            filtro_equipos_plaza(categoria, errors, lista_equipos)

            if len(errors) != 0:
                return render(request, 'crear_hijo.html',
                              {'equipos': lista_equipos, 'edicion_equipo': False, 'fecha_nacimiento': fecha_nacimiento,
                               'password': password, 'email': email, 'username': username, 'errores': errors,
                               'hijos': hijos, 'nombre': nombre, 'apellidos': apellidos})



            return render(request, 'crear_hijo.html', {'equipos': lista_equipos, 'edicion_equipo': True, 'nombre': nombre, 'apellidos': apellidos, 'hijo': hijo})

        datos= request.session['datos']
        hijo.username= datos['username']
        hijo.email = datos['email']
        hijo.fecha_nacimiento = datos['fecha_nacimiento']
        hijo.rol = datos['rol']
        hijo.password = make_password(datos['password'])
        hijo.save()
        jugador.usuario = User.objects.get(id=hijo.id)
        jugador.nombre = datos['nombre']
        jugador.apellidos = datos['apellidos']
        jugador.tutorLegal = tutor
        jugador.equipo = Equipo.objects.get(id=int(request.POST.get('equipo_seleccionado')))
        jugador.save()
        return redirect('gestion_familia')


def filtro_equipos_plaza(categoria, errors, lista_equipos):
    # plazas_libres = 20 - Jugador.objects.filter(equipo_id=equipo.id).count()
    # equipos = Equipo.objects.filter(categoria=categoria)

    for equipo in Equipo.objects.all():
        if categoria == equipo.categoria.tipo and equipo.es_safa:
            plazas_libres = 20 - Jugador.objects.filter(equipo_id=equipo.id).count()
            if plazas_libres > 0:
                dict = {'equipo': equipo, 'plazas_libres': plazas_libres}
                lista_equipos.append(dict)
    if len(lista_equipos) == 0:
        errors.append("No hay plazas disponibles en ningún equipo")


def elimina_hijo(request, id):
    hijo = Jugador.objects.get(id=id)
    usuario_id = hijo.usuario_id
    usuario = User.objects.get(id=usuario_id)
    usuario.delete()

    return redirect('gestion_familia')

def edita_hijo(request, id):
    jugador = Jugador.objects.get(id=id)
    equipos = Equipo.objects.all()
    fecha_nacimiento = jugador.usuario.fecha_nacimiento
    errors = []
    if request.method == 'GET':
        return render(request, 'crear_hijo.html', {'jugador': jugador, 'equipos': equipos,'modo_edicion': True, 'fecha_nacimiento': fecha_nacimiento})
    else:
        if 'boton' in request.POST and request.POST['boton'] == 'seleccion_datos':

            jugador.nombre = (request.POST.get('nombre'))
            jugador.apellidos = request.POST.get('apellidos')
            jugador.usuario.fecha_nacimiento = request.POST.get('fecha_nacimiento')
            diferencia = datetime.now() - datetime.strptime(request.POST.get('fecha_nacimiento'), '%Y-%m-%d')
            lista_equipos = []

            categoria = calculador_categoria(diferencia, errors)

            filtro_equipos_plaza(categoria, errors, lista_equipos)

            if len(errors) != 0:
                return render(request, 'crear_hijo.html', {'jugador': jugador,'modo_edicion': True, 'fecha_nacimiento': fecha_nacimiento,'errores': errors, 'edicion_equipo': False})

            jugador.save()


            return render(request, 'crear_hijo.html',
                          {'equipos': lista_equipos, 'edicion_equipo': True,'jugador': jugador})

        jugador.equipo = Equipo.objects.get(id=int(request.POST.get('tarifa_seleccionada')))
        jugador.save()
        return redirect('gestion_familia')


def calculador_categoria(diferencia, errors):
    categoria = ""
    if diferencia.days <= 1825:
        categoria =""
    elif diferencia.days < 2555:
        categoria = 'PreBenjamin'
    elif diferencia.days < 3285:
        categoria = 'Benjamin'
    elif diferencia.days < 4015:
        categoria = 'Alevin'
    elif diferencia.days < 4745:
        categoria = 'Infantil'
    elif diferencia.days < 5475:
        categoria = 'Cadete'
    elif diferencia.days < 6575:
        categoria = 'Juvenil'
    else:
        errors.append("El jugador debe ser menor de 18 años y mayor de 5")
    return categoria


def inicio_jugador(request, id=None):
    list_noticias = Noticias.objects.all().order_by('-id')
    list_noticias = list_noticias[0:3]
    hijos=[]
    usuario = request.user
    if usuario.rol == 'Jugador':
        jugador = Jugador.objects.get(usuario_id=usuario.id)
    else:
        tutor = TutorLegal.objects.get(usuario_id=usuario.id)
        hijos = Jugador.objects.filter(tutorLegal_id=tutor.id)
        jugador = Jugador.objects.get(usuario_id=id)

    equipos = Equipo.objects.filter(categoria_id=jugador.equipo.categoria)

    clasificacion = saca_clasificacion(equipos)

    fecha_actual = date.today()

    equipo3 = Equipo.objects.get(id=jugador.equipo.id)
    partidos_futuros = Partido.objects.filter(
        Q(equipo1_id=equipo3.id) | Q(equipo2_id=equipo3.id), fecha__gte=fecha_actual).order_by('fecha')

    entrenamientos = Entrenamiento.objects.filter(equipo=equipo3, fecha__gte=fecha_actual).order_by('fecha')

    response = requests.get(f"https://nominatim.openstreetmap.org/search?q={partidos_futuros[0].lugar}&format=json")
    if response.status_code != 200:
        list_partidos = Partido.objects.filter(Q(equipo1_id=equipo3.id) | Q(equipo2_id=equipo3.id))
        return render(request, 'inicio_jugador.html', {'noticias': list_noticias, 'jugador': jugador, 'equipos': equipos, 'clasificacion': clasificacion, 'hijos': hijos, 'partidos':list_partidos,'mapa_fallo': True,'siguiente_partido': partidos_futuros[0], 'entrenamiento': entrenamientos.first()})
    data = response.json()
    lat = data[0]['lat']
    lon = data[0]['lon']

    primer_entrenamiento = None
    if entrenamientos.exists():
        primer_entrenamiento = entrenamientos.first()

    list_partidos = Partido.objects.filter(Q(equipo1_id= equipo3.id)| Q(equipo2_id= equipo3.id))
    return render(request, 'inicio_jugador.html', {'noticias': list_noticias, 'jugador': jugador, 'equipos': equipos, 'clasificacion': clasificacion, 'hijos': hijos, 'partidos':list_partidos,'siguiente_partido': partidos_futuros[0], 'lat': lat, 'lon': lon, 'entrenamiento': primer_entrenamiento,'mapa_fallo': False})


def saca_clasificacion(equipos):
    clasificacion = list()
    for e in equipos:
        partidos_equipo1 = Partido.objects.filter(equipo1_id=e.id)
        partidos_equipo2 = Partido.objects.filter(equipo2_id=e.id)

        partidos_ganados_equipo1 = partidos_equipo1.filter(puntos_equipo1__gt=F('puntos_equipo2'))
        partidos_ganados_equipo2 = partidos_equipo2.filter(puntos_equipo2__gt=F('puntos_equipo1'))
        total_partidos_ganados = partidos_ganados_equipo1.count() + partidos_ganados_equipo2.count()

        total_partidos_jugados = partidos_equipo1.count() + partidos_equipo2.count()

        total_anotados_equipo1 = partidos_equipo1.aggregate(total_anotados=Sum('puntos_equipo1'))['total_anotados'] or 0
        total_anotados_equipo2 = partidos_equipo2.aggregate(total_anotados=Sum('puntos_equipo2'))['total_anotados'] or 0
        total_recibidos_equipo1 = partidos_equipo1.aggregate(total_recibidos=Sum('puntos_equipo2'))['total_recibidos'] or 0
        total_recibidos_equipo2 = partidos_equipo2.aggregate(total_recibidos=Sum('puntos_equipo1'))['total_recibidos'] or 0
        diferencia_puntos = (total_anotados_equipo1 + total_anotados_equipo2) - (total_recibidos_equipo1 + total_recibidos_equipo2)
        datos_equipo = {
            'ganados': total_partidos_ganados,
            'jugados': total_partidos_jugados,
            'diferencia_puntos': diferencia_puntos,
            'nombre': e.nombre,
        }
        clasificacion.append(datos_equipo)
    clasificacion.sort(key=lambda x: ((x['ganados']), x['diferencia_puntos']), reverse=True)
    return clasificacion


def estadisticas_jugador(request, id):
    usuario = request.user
    hijos=[]
    list_noticias = Noticias.objects.all().order_by('-id')
    list_noticias = list_noticias[0:3]
    if usuario.rol == 'Tutor':
        tutor = TutorLegal.objects.get(usuario_id=usuario.id)
        hijos = Jugador.objects.filter(tutorLegal_id=tutor.id)
    jugador = Jugador.objects.get(id=id)
    estadisticas_jugador = EstadisticasJugador.objects.filter(jugador=jugador)

    return render(request, 'estadisticas_jugador.html', {'estadisticas_jugador': estadisticas_jugador, 'hijos': hijos ,'jugador': jugador, 'list_noticias': list_noticias})


def terminos_y_servicios(request):
    return render(request, 'terminos_y_servicios.html')

def entrenador(request, id = None):
    usuario = request.user
    vista = True
    if request.method == 'GET':
        equipos = Equipo.objects.filter(entrenadores__usuario_id=usuario.id)
        lugares_entrenamiento = LugarEntrenamiento.objects.all()
        entrenador = Entrenador.objects.get(usuario_id=usuario.id)
        lista_entrenamientos = Entrenamiento.objects.filter(entrenador__equipo__id=entrenador.id, fecha__gte=date.today()).order_by('fecha')
        data = {'equipos_entrenador': equipos, 'lista_entrenamientos': lista_entrenamientos,
                'lugares_entrenamiento': lugares_entrenamiento, 'vista': vista}
        if id != None:
            entrenamiento = Entrenamiento.objects.get(id=id)
            data['entrenamiento']= entrenamiento
            data['vista'] = False
        return render(request, 'entrenador.html', data)

    else:
        if id != None:
            entrenamiento = Entrenamiento.objects.get(id=id)
            entrenamiento.fecha = request.POST.get('fecha')
            entrenamiento.hora = request.POST.get('hora')
            entrenamiento.entrenador = Entrenador.objects.get(usuario_id=usuario.id)
            entrenamiento.equipo = Equipo.objects.get(id=int(request.POST.get('equipo')))
            entrenamiento.lugarEntrenamiento = LugarEntrenamiento.objects.get(id=int(request.POST.get('lugar')))
            entrenamiento.save()
        else:
            entrenamiento_nuevo = Entrenamiento()
            entrenamiento_nuevo.fecha = request.POST.get('fecha')
            entrenamiento_nuevo.hora = request.POST.get('hora')
            entrenamiento_nuevo.entrenador = Entrenador.objects.get(usuario_id=usuario.id)
            entrenamiento_nuevo.lugarEntrenamiento = LugarEntrenamiento.objects.get(id=int(request.POST.get('lugar')))
            entrenamiento_nuevo.equipo = Equipo.objects.get(id=int(request.POST.get('equipo')))
            entrenamiento_nuevo.save()
        return redirect('entrenador')
def pagina_equipo(request, id):
    equipos = equipos_entrenador(request)
    equipo = Equipo.objects.get(id=id)
    fecha_actual = date.today()
    partidos_anteriores = Partido.objects.filter(
        Q(equipo1_id=id) | Q(equipo2_id=id), fecha__lt=fecha_actual).order_by('-fecha')
    partidos_futuros = Partido.objects.filter(
        Q(equipo1_id=id) | Q(equipo2_id=id), fecha__gte=fecha_actual).order_by('fecha')
    jugadores = Jugador.objects.filter(equipo_id=id)
    equipos_cat= Equipo.objects.filter(categoria=equipo.categoria)
    entrenador= Entrenador.objects.get(usuario_id=request.user.id)
    entrenamientos= Entrenamiento.objects.filter(entrenador_id=entrenador.id, fecha__gte=fecha_actual).order_by('fecha')
    clasificacion= saca_clasificacion(equipos_cat)
    response = requests.get(f"https://nominatim.openstreetmap.org/search?q={partidos_futuros[0].lugar}&format=json")
    if response.status_code != 200:
        return render(request, 'equipo.html', {'equipo': equipo, 'partidos_anteriores':partidos_anteriores[:3], 'jugadores': jugadores, 'partidos_futuros': partidos_futuros[1:4],'clasificacion': clasificacion,'siguiente_partido': partidos_futuros[0],'equipos_entrenador': equipos, 'entrenamiento': entrenamientos.first(), 'mapa_fallo': True, 'modo_equipo':True})
    data = response.json()
    print(response.content)
    lat = data[0]['lat']
    lon = data[0]['lon']

    primer_entrenamiento = None
    if entrenamientos.exists():
        primer_entrenamiento = entrenamientos.first()

    return render(request, 'equipo.html', {'equipo': equipo, 'partidos_anteriores':partidos_anteriores[:3], 'jugadores': jugadores, 'partidos_futuros': partidos_futuros[1:4],'clasificacion': clasificacion,'siguiente_partido': partidos_futuros[0], 'lat': lat, 'lon': lon,'equipos_entrenador': equipos, 'entrenamiento': primer_entrenamiento,'modo_equipo':True})


def equipos_entrenador(request):
    usuario = request.user
    equipos = Equipo.objects.filter(entrenadores__usuario_id=usuario.id)
    return equipos

def obtener_jugadores_por_partido(request):
    if request.method == 'GET' and 'partido_id' in request.GET:
        partido_id = request.GET['partido_id']
        partido = Partido.objects.get(pk=partido_id)
        jugadores_equipo1 = Jugador.objects.filter(equipo=partido.equipo1)
        jugadores_equipo2 = Jugador.objects.filter(equipo=partido.equipo2)
        jugadores = list(jugadores_equipo1) + list(jugadores_equipo2)
        jugadores_data = [{'id': jugador.id, 'nombre': jugador.nombre} for jugador in jugadores]
        return JsonResponse({'jugadores': jugadores_data})
    else:
        return JsonResponse({'error': 'Se requiere el ID del partido'})

def producto(request, id):
    producto = Producto.objects.get(id=id)
    tallas = ProductoTalla.objects.filter(producto_id=id).order_by('talla')
    if request.method == 'POST':

        producto_talla = ProductoTalla.objects.get(producto_id=id, talla=request.POST.get('tallas'))

        carro = {}

        # Comprobar si hay ya un carrito en sesión
        if "carro" in request.session:
            carro = request.session.get("carro", {})

        # Comprobar que el producto está o no está en el carrito
        if str(producto_talla.id) in carro.keys():
            carro[str(producto_talla.id)] = int(carro[str(producto_talla.id)]) + int(request.POST.get('cantidad'))
        else:
            carro[str(producto_talla.id)] = int(request.POST.get('cantidad'))
        request.session["carro"] = carro

        return redirect('tienda')
    return render(request, 'producto.html', {'producto': producto, 'tallas': tallas})

def estadisticas_equipo(request, id):
    equipo = Equipo.objects.get(id=id)
    jugadores = Jugador.objects.filter(equipo_id=equipo.id)
    estadisticas_jugadores = []

    for jugador in jugadores:
        estadisticas = EstadisticasJugador.objects.filter(jugador=jugador).aggregate(
            total_puntos=Sum('puntos',default=0),
            total_minutos= Sum('minutos',default=0),
            total_rebotes = Sum('rebotes',default=0),
            total_asistencias =Sum('asistencias',default=0),
            total_faltas = Sum('faltas',default=0)
        )
        estadisticas_jugadores.append({
            'jugador': jugador,
            'estadisticas': estadisticas
        })

        usuario = request.user
        data = {}
        envio_datos_barra(data,request,usuario)

    return render(request, 'lista_estadisticas_equipo.html', {'equipo': equipo, 'estadisticas_jugadores': estadisticas_jugadores, 'data': data})


# def add_carrito(request):

def anyadir_carrito(request, id):
    carro = request.session.get('carro', {})
    carro[str(id)] = carro.get(str(id), 0) + 1
    request.session["carro"] = carro

    totalItems = sum(carro.values())
    totalPrice = sum(ProductoTalla.objects.get(id=producto_id).producto.precio * quantity for producto_id, quantity in carro.items())
    productQuantities = {str(product_id): quantity for product_id, quantity in carro.items()}

    # Devolver una respuesta JSON
    return JsonResponse({'totalItems': totalItems, 'totalPrice': totalPrice, 'productQuantities': productQuantities})

def restar_carrito(request, id):
    carro = request.session.get('carro', {})
    if str(id) in carro:
        carro[str(id)] -= 1
        if carro[str(id)] <= 0:
            del carro[str(id)]
    request.session["carro"] = carro

    # Calcular el total de items y el precio total
    totalItems = sum(carro.values())
    totalPrice = sum(ProductoTalla.objects.get(id=producto_id).producto.precio * cantidad for producto_id, cantidad in carro.items())

    # Crear un diccionario que mapee cada ID de producto a su cantidad
    productQuantities = {str(product_id): quantity for product_id, quantity in carro.items()}

    # Devolver una respuesta JSON
    return JsonResponse({'totalItems': totalItems, 'totalPrice': totalPrice, 'productQuantities': productQuantities})

def eliminar_carrito(request, id):
    carro = request.session.get('carro', {})
    if str(id) in carro:
        del carro[str(id)]
    request.session["carro"] = carro

    # Calcular el total de items y el precio total
    totalItems = sum(carro.values())
    totalPrice = sum(ProductoTalla.objects.get(id=producto_id).producto.precio * quantity for producto_id, quantity in carro.items())

    # Crear un diccionario que mapee cada ID de producto a su cantidad
    productQuantities = {str(product_id): quantity for product_id, quantity in carro.items()}

    # Devolver una respuesta JSON
    return JsonResponse({'totalItems': totalItems, 'totalPrice': totalPrice, 'productQuantities': productQuantities})

def carrito(request):
    carro = {}
    carro_cliente = {}
    total = 0.0
    cantProductos = 0

    if 'carro' in request.session:
        carro_cliente = request.session.get('carro', {})

    for key in carro_cliente.keys():
        producto = ProductoTalla.objects.get(id=key)
        cantidad = carro_cliente[key]
        carro[producto] = cantidad
        total += cantidad * producto.producto.precio
        cantProductos += cantidad  # Suma la cantidad de cada producto

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'cantProductos': cantProductos})

    return render(request, 'carrito.html', {'carro': carro, 'total': total, 'cantProductos': cantProductos})

def formulario_pago_pedido(request):
    carro = {}
    carro_cliente = {}
    total = 0.0
    cantProductos = 0

    if 'carro' in request.session:
        carro_cliente = request.session.get('carro', {})

    for key in carro_cliente.keys():
        producto = ProductoTalla.objects.get(id=key)
        cantidad = carro_cliente[key]
        carro[producto] = cantidad
        total += cantidad * producto.producto.precio
        cantProductos += cantidad

    usuario = request.user
    descuento= ""
    if usuario.rol == "Tutor":
        tutor = TutorLegal.objects.get(usuario=usuario)
        if tutor.tarifa == 'PREMIUM':
            total_descuento = total*0.90
            descuento="10%"
        else:
            total_descuento = total*0.95
            descuento ="5%"
    else:
        total_descuento = total

    return render(request, 'formulario_pago.html', {'total': total, 'cantProductos': cantProductos, 'carro': carro, 'total_descuento': total_descuento,'descuento': descuento})