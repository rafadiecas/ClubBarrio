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
    path('administrador/noticias/', lista_noticias , name='noticias_admin'),
    path('administrador/noticias/new', crear_noticia, name='crear_noticia'),
    path('administrador/noticias/eliminar/<int:id>/', elimina_noticia, name='elimina_noticia'),
    path('administrador/noticias/editar/<int:id>/', editar_noticia, name='editar_noticia'),
    path('administrador/entrenamientos/', entrenamientos_listado, name='entrenamientos_listado'),
    path('administrador/entrenamientos/new', crear_entrenamiento, name='crear_entrenamiento'),
    path('administrador/entrenamientos/editar/<int:id>/', editar_entrenamiento, name='editar_entrenamiento'),
    path('administrador/entrenamientos/eliminar/<int:id>/', elimina_entrenamiento, name='elimina_entrenamiento'),
    path('administrador/estadisticas_jugador/', estadisticas_jugador_listado, name='estadisticas_jugador_listado'),
    path('administrador/estadisticas_jugador/new', crear_estadisticas_jugador, name='crear_estadisticas_jugador'),
    path('administrador/estadisticas_jugador/editar/<int:id>/', editar_estadisticas_jugador, name='editar_estadisticas_jugador'),
    path('administrador/estadisticas_jugador/eliminar/<int:id>/', elimina_estadisticas_jugador, name='elimina_estadisticas_jugador'),
    path('administrador/partidos/', partidos_listado, name='partidos_listado'),
    path('administrador/partidos/new', crear_partido, name='crear_partido'),
    path('administrador/partidos/eliminar/<int:id>/', elimina_partido, name='elimina_partido'),
    path('administrador/partidos/editar/<int:id>/', editar_partido, name='editar_partido'),
    path('administrador/tienda/', lista_tienda, name='lista_tienda'),
    path('administrador/tienda/new', crear_producto, name='crear_producto'),

]
