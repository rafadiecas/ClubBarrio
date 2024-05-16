from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


from django.shortcuts import redirect

def user_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('error')
        elif not request.user.is_active:
            return redirect('error')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper

def rol_requerido(rol_requerido):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated or request.user.rol != rol_requerido:
                return redirect('error')
            else:
                return view_func(request, *args, **kwargs)
        return wrapper
    return decorator