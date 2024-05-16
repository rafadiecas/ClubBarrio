from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


from django.shortcuts import redirect

def user_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper

def rol_requerido(*roles_requeridos):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated or request.user.rol not in roles_requeridos:
                return redirect('error')
            else:
                return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def rol_prohibido(*roles_prohibidos):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.rol in roles_prohibidos:
                return redirect('error')
            else:
                return view_func(request, *args, **kwargs)
        return wrapper
    return decorator