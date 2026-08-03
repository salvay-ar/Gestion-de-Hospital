from django.db import connection
from django.shortcuts import render, redirect
from .decorators import requiere_rol


def inicio(request):
    return render(request, "App/inicio.html")


def login(request):

    mensaje = ""

    if request.method == "POST":

        email = request.POST.get("email")
        usuario = request.POST.get("usuario")
        contraseña = request.POST.get("contraseña")

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT id_usuario, rol
                FROM usuario
                WHERE email = %s
                AND usuario = %s
                AND contraseña = %s
            """, [email, usuario, contraseña])

            user = cursor.fetchone()

        if user:

            request.session["usuario"] = user[0]
            request.session["rol"] = user[1]

            if user[1] == "Administrador":
                return redirect("admin")

            elif user[1] == "Medico":
                return redirect("medico")

            elif user[1] == "Secretaria":
                return redirect("secretaria")

        else:

            mensaje = "Correo, usuario o contraseña incorrectos"

    return render(request, "App/login.html", {
        "mensaje": mensaje
    })


def logout(request):
    request.session.flush()
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