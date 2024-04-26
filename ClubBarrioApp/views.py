from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.utils.datetime_safe import datetime
import re

from .models import *
from django.core.paginator import Paginator
from django.http import Http404
from django.http import JsonResponse
from .decorator import user_required, rol_requerido
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash


# Create your views here.

def pagina_inicio(request):
    list_noticias = Noticias.objects.all().order_by('-id')
    list_noticias = list_noticias[0:3]
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
    if usuario.is_authenticated:
        if usuario.rol == 'Tutor':
            tutor = TutorLegal.objects.get(usuario_id=usuario.id)
            hijos = Jugador.objects.filter(tutorLegal_id=tutor.id)
            data = {
                'entity': list_noticias,
                'paginator': paginator,
                'hijos': hijos
            }
            return render(request, 'Noticias.html', data)

    return render(request, 'Noticias.html', data)

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
    return errores

def perfil(request):
    usuario = User.objects.get(id=request.user.id)
    roles_map = {
        'Tutor': TutorLegal,
        'Jugador': Jugador,
        'Entrenador': Entrenador

    }

    if usuario.rol in roles_map:
        perfil = roles_map[usuario.rol].objects.get(usuario_id=usuario.id)

        if request.method == 'POST':
            perfil.nombre = request.POST.get('nombre')
            perfil.apellidos = request.POST.get('apellidos')
            perfil.save()

        if usuario.rol == 'Jugador':
            equipo = perfil.equipo  # Obtén el equipo asociado al perfil si el usuario es un jugador
            return render(request, 'profile.html', {'perfil': perfil, 'equipo': equipo})

        return render(request, 'profile.html', {'perfil': perfil})

    return render(request, 'profile.html')

def perfil_pass(request):
    usuario = request.user
    error_en_cambio_de_contraseña = False

    if request.method == 'POST':
        contraseña_actual = request.POST.get('password_actual')
        nueva_contraseña = request.POST.get('new_password')
        confirmacion_contraseña = request.POST.get('confirmacion_password')

        errores = validar_contraseña(usuario, contraseña_actual, nueva_contraseña, confirmacion_contraseña)
        if errores:
            error_en_cambio_de_contraseña = True
            return JsonResponse({'errores': errores}, status=400)

        usuario.password = make_password(nueva_contraseña)
        usuario.save()  # Guarda el usuario después de cambiar la contraseña
        update_session_auth_hash(request, usuario)  # Actualiza la sesión del usuario

        return JsonResponse({'success': 'Contraseña cambiada con éxito'})

    return render(request, 'profile.html', {'error_en_cambio_de_contraseña': error_en_cambio_de_contraseña})



def new_user(request):
    Users = User.objects.all()
    Equipos = Equipo.objects.all()
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

        errores = filtro(email, fecha_nacimiento, 'Usuario', nombre_usuario, contrasenya, repetirContrasenya)


        if len(errores) != 0:
            return render(request, 'registro.html', {"errores": errores, "nombre_usuraio": nombre_usuario, "email": email, "fecha_nacimiento": fecha_nacimiento})
        else:
            usuario = User.objects.create(username=nombre_usuario, password=make_password(contrasenya), email=email,
                                          fecha_nacimiento=fecha_nacimiento)
            usuario.save()

            return redirect('login')

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
        lista_categorias = categoria.objects.all()
        entrenadores = Entrenador.objects.all()
        return render(request, 'crear_equipo.html', {'lista_categorias': lista_categorias, 'entrenadores': entrenadores})
    else:
        equipo_nuevo= Equipo()
        equipo_nuevo.nombre= request.POST.get('nombre')
        equipo_nuevo.escudo = request.POST.get('escudo')
        equipo_nuevo.es_safa = request.POST.get('is_safa')
        equipo_nuevo.categoria= categoria.objects.get(id=int(request.POST.get('categoria')))
        equipo_nuevo.save()

        lista_entrenadores = request.POST.getlist('entrenadores')
        for e in lista_entrenadores:
            equipo_nuevo.entrenadores.add(e)

        return redirect('equipos')

def editar_equipo(request, id):
    equipo = Equipo.objects.get(id=id)
    if request.method == 'GET':
        lista_categorias = categoria.objects.all()
        entrenadores = Entrenador.objects.all()
        id_entrenadores = equipo.entrenadores.values_list('id', flat=True)
        return render(request, 'crear_equipo.html', {'equipo':equipo, 'id_entrenadores':id_entrenadores, 'lista_categorias': lista_categorias, 'entrenadores': entrenadores})
    else:
        equipo.nombre = request.POST.get('nombre')
        equipo.escudo = request.POST.get('escudo')
        equipo.categoria = categoria.objects.get(id=int(request.POST.get('categoria')))
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
    lista_entrenamientos = Entrenamiento.objects.all()

    return render(request, 'lista_entrenamiento.html', {"lista_entrenamientos":lista_entrenamientos})
def crear_entrenamiento(request):
    if request.method == 'GET':
        lista_entrenadores = Entrenador.objects.all()
        lista_lugares_entrenamiento = LugarEntrenamiento.objects.all()
        return render(request, 'crear_entrenamiento.html',
                      {'lista_entrenadores': lista_entrenadores, 'lista_lugares_entrenamiento': lista_lugares_entrenamiento})
    else:
        entrenamiento_nuevo = Entrenamiento()
        entrenamiento_nuevo.fecha = request.POST.get('fecha')
        entrenamiento_nuevo.hora = request.POST.get('hora')
        entrenamiento_nuevo.entrenador = Entrenador.objects.get(id=int(request.POST.get('entrenador')))
        entrenamiento_nuevo.lugarEntrenamiento = LugarEntrenamiento.objects.get(id=int(request.POST.get('lugarEntrenamiento')))
        entrenamiento_nuevo.save()

        return redirect('entrenamientos_listado')
def editar_entrenamiento(request, id):
    entrenamiento = Entrenamiento.objects.get(id=id)
    if request.method == 'GET':
        lista_entrenadores = Entrenador.objects.all()
        lista_lugares_entrenamiento = LugarEntrenamiento.objects.all()
        return render(request, 'crear_entrenamiento.html',
                      {'entrenamiento': entrenamiento, 'lista_entrenadores': lista_entrenadores, 'lista_lugares_entrenamiento': lista_lugares_entrenamiento})
    else:
        entrenamiento.fecha = request.POST.get('fecha')
        entrenamiento.hora = request.POST.get('hora')
        entrenamiento.entrenador = Entrenador.objects.get(id=int(request.POST.get('entrenador')))
        entrenamiento.lugarEntrenamiento = LugarEntrenamiento.objects.get(id=int(request.POST.get('lugarEntrenamiento')))
        entrenamiento.save()

        return redirect('entrenamientos_listado')

def elimina_entrenamiento(request, id):
    entrenamiento = Entrenamiento.objects.get(id=id)
    entrenamiento.delete()
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
        return redirect('noticias_admin')

def elimina_noticia(request, id):
    noticia = Noticias.objects.get(id=id)
    noticia.delete()
    return redirect('noticias_admin')

def editar_noticia(request,id):
    noticia = Noticias.objects.get(id=id)
    if request.method == 'GET':
        return render(request, 'crear_noticias.html', {'noticia':noticia})
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
        lista_partidos = Partido.objects.all()
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
        estadisticas_jugador_nuevo.jugador = Jugador.objects.get(id=int(request.POST.get('jugador')))
        estadisticas_jugador_nuevo.partido = Partido.objects.get(id=int(request.POST.get('partido')))
        estadisticas_jugador_nuevo.save()

        return redirect('entrenamientos_listado')
def editar_estadisticas_jugador(request, id):
    estadisticas_jugador = EstadisticasJugador.objects.get(id=id)
    if request.method == 'GET':
        lista_entrenadores = Entrenador.objects.all()
        lista_partidos = Partido.objects.all()
        return render(request, 'crear_estadisticas_jugador.html',
                      {'estadisticas_jugador': estadisticas_jugador, 'lista_entrenadores': lista_entrenadores, 'lista_partidos': lista_partidos})
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
        return render(request, 'crear_partidos.html', {'partido': partido, 'lista_equipos': lista_equipos, 'temporadas': temporadas})
    else:
        partido.fecha = request.POST.get('fecha')
        partido.hora = request.POST.get('hora')
        partido.lugar = request.POST.get('lugar')
        partido.puntos_equipo1 = request.POST.get('puntos_equipo1')
        partido.puntos_equipo2 = request.POST.get('puntos_equipo2')
        partido.equipo1 = Equipo.objects.get(id=int(request.POST.get('equipo_local')))
        partido.equipo2 = Equipo.objects.get(id=int(request.POST.get('equipo_visitante')))
        partido.temporada = Temporada.objects.get(id=int(request.POST.get('temporada')))
        if request.POST.get('equipo_local') == request.POST.get('equipo_visitante'):
            errores = ["Los equipos no pueden ser iguales"]
            return render(request, 'crear_partidos.html', {'errores': errores, 'lista_equipos': Equipo.objects.all(), 'temporadas': Temporada.objects.all()})
        else:
            partido.save()
            return redirect('partidos_listado')


def lista_tienda(request):
    lista_productos = Producto.objects.all()
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
        producto_nuevo.talla = Talla.objects.get(id=int(request.POST.get('talla')))
        producto_nuevo.tipo = Tipo.objects.get(id=int(request.POST.get('tipo')))
        producto_nuevo.stock = request.POST.get('stock')
        producto_nuevo.url_imagen = request.POST.get('url_imagen')
        producto_nuevo.save()
        return redirect('lista_tienda')

def elimina_producto(request, id):
    producto = Producto.objects.get(id=id)
    producto.delete()
    return redirect('lista_tienda')

def edita_producto(request, id):
    producto = Producto.objects.get(id=id)
    if request.method == 'GET':
        tallas = Talla.objects.all()
        tipos = Tipo.objects.all()
        return render(request, 'crear_productos.html', {'producto': producto, 'tallas': tallas, 'tipos': tipos})
    else:
        producto.nombre = request.POST.get('nombre')
        producto.precio = request.POST.get('precio')
        producto.talla = Talla.objects.get(id=int(request.POST.get('talla')))
        producto.tipo = Tipo.objects.get(id=int(request.POST.get('tipo')))
        producto.stock = request.POST.get('stock')
        producto.url_imagen = request.POST.get('url_imagen')
        producto.save()
        return redirect('lista_tienda')


def pagina_usuario(request):
    list_noticias = Noticias.objects.all().order_by('-id')
    list_noticias = list_noticias[0:3]
    list_partidos = Partido.objects.all()
    usuario = request.user
    if usuario.rol == 'Tutor':
        tutor = TutorLegal.objects.get(usuario_id=usuario.id)
        hijos = Jugador.objects.filter(tutorLegal_id=tutor.id)
        return render(request, 'usuario.html', {'noticias': list_noticias, 'partidos': list_partidos, 'hijos': hijos})
    else:
        return render(request, 'usuario.html', {'noticias': list_noticias, 'partidos': list_partidos})

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

        return redirect('usuario')
def terminos_y_servicios(request):
    return render(request, 'terminos_y_servicios.html')

def lista_hijos(request):
    usuario = request.user
    tutor = TutorLegal.objects.get(usuario_id=usuario.id)
    hijos = Jugador.objects.filter(tutorLegal_id=tutor.id)
    return render(request, 'lista_hijos.html', {'hijos': hijos})

def crea_hijos(request):
    usuario = request.user
    tutor = TutorLegal.objects.get(usuario_id=usuario.id)
    categoria = ""
    hijos = Jugador.objects.filter(tutorLegal_id=tutor.id)
    errors = []
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
                hijo.username= username
                hijo.email = email
                hijo.fecha_nacimiento = fecha_nacimiento
                hijo.password = make_password(password)


            if diferencia.days < 1825:
                categoria = 'Prebenjamin'
            elif diferencia.days < 2920:
                categoria = 'Benjamin'
            elif diferencia.days < 4015:
                categoria = 'Alevin'
            elif diferencia.days < 5110:
                categoria = 'Infantil'
            elif diferencia.days < 6205:
                categoria = 'Cadete'
            elif diferencia.days < 7300:
                categoria = 'Juvenil'
            else:
                errors.append("El jugador debe ser menor de 20 años")



            if (tutor.tarifa == 'BASE' and len(hijos) >= 1) or (tutor.tarifa == 'PLUS' and len(hijos) >= 3) or (
                    tutor.tarifa == 'PREMIUM' and len(hijos) >= 5):
                errors.append("No puedes añadir más hijos")

            if len(errors) != 0:
                return render(request, 'crear_hijo.html',
                              {'equipos': lista_equipos, 'edicion_equipo': False, 'fecha_nacimiento': fecha_nacimiento,
                               'password': password, 'email': email, 'username': username, 'errores': errors,
                               'hijos': hijos, 'nombre': nombre, 'apellidos': apellidos})

            hijo.save()


            for equipo in Equipo.objects.all():
                if categoria in equipo.categoria.tipo:
                    lista_equipos.append(equipo)
            return render(request, 'crear_hijo.html', {'equipos': lista_equipos, 'edicion_equipo': True, 'nombre': nombre, 'apellidos': apellidos, 'hijo': hijo})

        jugador.usuario = User.objects.get(id=request.POST.get('hijo'))
        jugador.nombre = request.POST.get('nombre-jug')
        jugador.apellidos = request.POST.get('apellidos-jug')
        jugador.tutorLegal = tutor
        jugador.equipo = Equipo.objects.get(id=int(request.POST.get('tarifa_seleccionada')))
        jugador.save()
        return redirect('gestion_familia')

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


            if diferencia.days < 1825:
                categoria = 'Prebenjamin'
            elif diferencia.days < 2920:
                categoria = 'Benjamin'
            elif diferencia.days < 4015:
                categoria = 'Alevin'
            elif diferencia.days < 5110:
                categoria = 'Infantil'
            elif diferencia.days < 6205:
                categoria = 'Cadete'
            elif diferencia.days < 7300:
                categoria = 'Juvenil'
            else:
                errors.append("El jugador debe ser menor de 20 años")

            if len(errors) != 0:
                return render(request, 'crear_hijo.html', {'jugador': jugador,'modo_edicion': True, 'fecha_nacimiento': fecha_nacimiento,'errores': errors, 'edicion_equipo': False})

            jugador.save()

            for equipo in Equipo.objects.all():
                if categoria in equipo.categoria.tipo:
                    lista_equipos.append(equipo)
            return render(request, 'crear_hijo.html',
                          {'equipos': lista_equipos, 'edicion_equipo': True,'jugador': jugador})

        jugador.equipo = Equipo.objects.get(id=int(request.POST.get('tarifa_seleccionada')))
        jugador.save()
        return redirect('gestion_familia')