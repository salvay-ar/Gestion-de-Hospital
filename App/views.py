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

    paciente = None
    historial = []
    mensaje = ""

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT dni
            FROM paciente
            ORDER BY dni
        """)
        dnis = cursor.fetchall()
        
    if request.method == "POST" and "buscar" in request.POST:

        dni = request.POST.get("dni")

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    id_paciente,
                    nombre,
                    apellido,
                    dni,
                    grupo_sanguineo,
                    antecedentes
                FROM paciente
                WHERE dni = %s
            """, [dni])

            paciente = cursor.fetchone()

            if paciente:

                cursor.execute("""
                    SELECT
                        d.fecha,
                        d.diagnostico,
                        h.observaciones
                    FROM historial_medico h
                    INNER JOIN diagnostico d
                        ON h.id_historial = d.id_historial
                    WHERE h.id_paciente=%s
                    ORDER BY d.fecha DESC
                """, [paciente[0]])

                historial = cursor.fetchall()

            else:

                mensaje = "Paciente no encontrado"

    return render(request, "App/medico.html", {
        "paciente": paciente,
        "historial": historial,
        "mensaje": mensaje,
        "dnis": dnis
    })
    


@requiere_rol("Secretaria")
def secretaria(request):
    return render(request, "App/secretaria.html")