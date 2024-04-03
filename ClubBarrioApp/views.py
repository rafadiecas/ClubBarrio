from django.shortcuts import render
from .models import *

# Create your views here.

def pagina_inicio(request):
    list_noticias = Noticias.objects.all()
    return render(request, 'inicio.html', {'noticias': list_noticias})
