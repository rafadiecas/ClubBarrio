from django.shortcuts import render
from .models import *

# Create your views here.

def pagina_inicio(request):
    list_noticias = Noticias.objects.all().order_by('-id')
    list_noticias = list_noticias[0:3]
    return render(request, 'inicio.html', {'noticias': list_noticias, 'ultima_noticia': ultima_noticia})
