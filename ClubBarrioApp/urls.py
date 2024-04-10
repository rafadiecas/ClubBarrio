"""
URL configuration for ClubBarrio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import *

urlpatterns = [
    path('inicio/', pagina_inicio, name='inicio'),
    path('noticias/', pagina_noticias, name='noticias'),
    path('login/', logear, name='login'),
    path('administrador/', administrador, name='administrador'),
    path('administrador/usuarios/', usuarios, name='usuarios'),
    path('administrador/usuarios/new',new_user, name='new_user'),
    path('administrador/usuarios/eliminar/<int:id>/', elimina_usuario , name='elimina_usuario'),
    path('registro/', registro, name='registro'),
    path('administrador/usuarios/edit/<int:id>/', edita_usuario, name='edita_usuario'),
    path('logout/', desloguear, name='desloguear'),
    path('administrador/equipos/', equipos_listado, name='equipos'),
    path('administrador/equipos/new', crear_equipo, name='crear_equipo'),
    path('administrador/equipos/editar/<int:id>/', editar_equipo, name='editar_equipo'),
    path('administrador/equipos/eliminar/<int:id>/', elimina_equipo, name='elimina_equipo'),
    path('administrador/entrenamientos/', entrenamientos_listado, name='entrenamientos_listado'),
    path('administrador/entrenamientos/new', crear_entrenamiento, name='crear_entrenamiento'),
    path('administrador/entrenamientos/editar/<int:id>/', editar_entrenamiento, name='editar_entrenamiento'),
    path('administrador/entrenamientos/eliminar/<int:id>/', elimina_entrenamiento, name='elimina_entrenamiento'),

]
