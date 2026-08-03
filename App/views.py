from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Usuario
from .decorators import requiere_rol
from django.shortcuts import render

def inicio(request):
    return render(request, "App/inicio.html")

def login(request):
    mensaje = ""
    if request.method == "POST":
        email = request.POST.get("email")
        usuario = request.POST.get("usuario")
        contraseña = request.POST.get("contraseña")

        try:

            user = Usuario.objects.get(
                email=email,
                usuario=usuario,
                contraseña=contraseña
            )

            request.session["usuario"] = user.id_usuario
            request.session["rol"] = user.rol

            if user.rol == "Administrador":
                return redirect("admin")

            elif user.rol == "Medico":
                return redirect("medico")

            elif user.rol == "Secretaria":
                return redirect("secretaria")

        except Usuario.DoesNotExist:
            mensaje = "Correo, usuario o contraseña incorrectos"

    return render(request, "App/login.html", {
        "mensaje": mensaje
    })
    
from django.shortcuts import redirect

def logout(request):
    request.session.flush()   # Elimina toda la sesión
    return redirect("login")

@requiere_rol("Administrador")
def admin(request):
    return render(request, "App/admin.html")


@requiere_rol("Medico")
def medico(request):
    return render(request, "App/medico.html")


@requiere_rol("Secretaria")
def secretaria(request):
    return render(request, "App/secretaria.html")