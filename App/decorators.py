
from django.shortcuts import redirect
from functools import wraps

def requiere_rol(rol):

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if "usuario" not in request.session:
                return redirect("login")

            if request.session["rol"] != rol:
                return redirect("login")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator