from django.shortcuts import render, redirect
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
    lista_usuarios = Usuario.objects.all()
    return render(request, 'usuarios.html', {'usuarios': lista_usuarios})

def new_user(request):
    if request.method == 'GET':
        Users = Usuario.objects.all()
        return render(request, "crea_usuario.html", {'Users': Users})
    else:
        new = Usuario()
        new.nombre = request.POST.get('nombre')
        new.apellidos = request.POST.get('apellidos')
        new.email = request.POST.get('email')
        new.password = request.POST.get('password')
        new.fecha_nacimiento = request.POST.get('fecha_nacimiento')
        new.save()

    if request.POST.get('rol') == 'Padre':
        new_padre = TutorLegal()
        new_padre.usuario_id = new.id
        new_padre.save()

        return redirect('/ClubBarrioApp/administrador/usuarios/')
