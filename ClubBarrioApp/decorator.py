from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


def user_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_active:
            return render(request, "login.html")
        return view_func(request, *args, **kwargs)
    return wrapper

def rol_requerido(rol_requerido):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user is not None and request.user.is_authenticated and request.user.rol == rol_requerido:
                return view_func(request, *args, **kwargs)
            else:
                return render(request, 'login.html')
        return wrapper
    return decorator