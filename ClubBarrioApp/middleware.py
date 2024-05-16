from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from .decorator import user_required, rol_requerido

class AdminRequiredMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        url_path = request.path_info
        if 'administrador' in url_path:
            return user_required(rol_requerido('Administrador')(view_func))(request, *view_args, **view_kwargs)