from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.utils.datetime_safe import datetime
import re

from .models import *
from django.core.paginator import Paginator
from django.http import Http404


# Create your views here.

def pagina_inicio(request):
    list_noticias = Noticias.objects.all().order_by('-id')
    list_noticias = list_noticias[0:3]
    return render(request, 'inicio.html', {'noticias': list_noticias})

def login(request):
    return render(request, 'login.html')


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

    return render(request, 'Noticias.html', data)

def administrador(request):
    return render(request, 'administrador.html')

def usuarios(request):
    lista_usuarios = User.objects.all()
    return render(request, 'usuarios.html', {'usuarios': lista_usuarios})

def new_user(request):
    Users = User.objects.all()
    Equipos = Equipo.objects.all()
    Tutores = TutorLegal.objects.all()
    roles = Role.labels[:-1]
    if request.method == 'GET':

        return render(request, "crea_usuario.html", {'Users': Users, 'Equipos': Equipos, 'Tutores': Tutores, 'roles': roles})
    else:

        username = request.POST.get('username')
        rol =Role.value_for_label(request.POST.get('rol'))
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')

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
        if diferencia.days < 6570:
            errors.append("El usuario debe ser mayor de edad")
        largo = re.compile(r'.{8,}')
        digito = re.compile(r'\d+')
        letra_may = re.compile(r'[A-Z]+')
        letra_min = re.compile(r'[a-z]+')
        validaciones = [largo, digito, letra_may, letra_min]
        for v in validaciones:
            if not v.search(password):
                errors.append("La contraseña debe tener al menos 8 caracteres, una letra mayúscula, una minúscula y un número")
                break

        if len(errors) != 0:
            return render(request, "crea_usuario.html", {"errores": errors, "username": username, "email": email, "roles": roles, "fecha_nacimiento": fecha_nacimiento, "Users": Users, "Equipos": Equipos, "Tutores": Tutores})
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

        errores = []

        if contrasenya!=repetirContrasenya:
            errores.append("Las contraseñas no coinciden.")

        existe_usuario = User.objects.filter(username=nombre_usuario)
        if existe_usuario:
            errores.append("Ese nombre de usuario ya existe.")
        existe_email = User.objects.filter(email=email)
        if existe_email:
            errores.append("Existe una cuenta asociada a ese correo.")
        fecha = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
        diferencia = datetime.now() - fecha
        if diferencia.days < 6570:
            errores.append("El usuario debe ser mayor de edad")
        largo = re.compile(r'.{8,}')
        digito = re.compile(r'\d+')
        letra_may = re.compile(r'[A-Z]+')
        letra_min = re.compile(r'[a-z]+')
        validaciones = [largo, digito, letra_may, letra_min]
        for v in validaciones:
            if not v.search(contrasenya):
                errores.append(
                    "La contraseña debe tener al menos 8 caracteres, una letra mayúscula, una minúscula y un número")
                return render(request, 'registro.html', {"errores": errores})

        if len(errores) != 0:
            return render(request, 'registro.html', {"errores": errores})
        else:
            usuario = User.objects.create(username=nombre_usuario, password=make_password(contrasenya), email=email, fecha_nacimiento=fecha_nacimiento)
            usuario.save()

            return redirect('login')