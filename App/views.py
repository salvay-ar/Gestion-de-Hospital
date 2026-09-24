from django.db import connection
from django.shortcuts import render, redirect
from .decorators import requiere_rol
from datetime import date


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

    return render(request, "App/login.html", {"mensaje": mensaje})


def logout(request):
    request.session.flush()
    return redirect("login")


@requiere_rol("Administrador")
def admin(request):
    return render(request, "App/admin.html")


@requiere_rol("Medico")
def medico(request):
    paciente = None
    pacientes = []
    historial = []
    mensaje = ""

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT dni
            FROM paciente
            ORDER BY dni
        """)
        dnis = cursor.fetchall()

        cursor.execute("""
            SELECT nombre, apellido
            FROM paciente
            ORDER BY nombre, apellido
        """)
        nombres = cursor.fetchall()

    if request.method == "POST" and "buscar" in request.POST:
        busqueda = request.POST.get("busqueda", "").strip()

        if busqueda:
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
                """, [busqueda])

                paciente = cursor.fetchone()

                if not paciente:
                    partes = busqueda.split()

                    if len(partes) >= 2:
                        nombre = partes[0]
                        apellido = " ".join(partes[1:])

                        cursor.execute("""
                            SELECT
                                id_paciente,
                                nombre,
                                apellido,
                                dni,
                                grupo_sanguineo,
                                antecedentes
                            FROM paciente
                            WHERE nombre LIKE %s
                            AND apellido LIKE %s
                            ORDER BY nombre, apellido
                        """, [
                            f"%{nombre}%",
                            f"%{apellido}%"
                        ])
                    else:
                        cursor.execute("""
                            SELECT
                                id_paciente,
                                nombre,
                                apellido,
                                dni,
                                grupo_sanguineo,
                                antecedentes
                            FROM paciente
                            WHERE nombre LIKE %s
                            OR apellido LIKE %s
                            ORDER BY nombre, apellido
                        """, [
                            f"%{busqueda}%",
                            f"%{busqueda}%"
                        ])

                    pacientes = cursor.fetchall()

                    if len(pacientes) == 1:
                        paciente = pacientes[0]
                        pacientes = []
                    elif len(pacientes) > 1:
                        mensaje = "Se encontraron varios pacientes. Seleccione uno."
                    else:
                        mensaje = "Paciente no encontrado"
        else:
            mensaje = "Ingrese un DNI, nombre o apellido."

    if request.method == "POST" and "seleccionar" in request.POST:
        id_paciente = request.POST.get("id_paciente")

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
                WHERE id_paciente = %s
            """, [id_paciente])

            paciente = cursor.fetchone()

    if request.method == "POST" and "guardar" in request.POST:
        id_paciente = request.POST.get("id_paciente")
        sintomas = request.POST.get("sintomas", "").strip()
        diagnostico = request.POST.get("diagnostico", "").strip()
        tratamiento = request.POST.get("tratamiento", "").strip()

        id_usuario = request.session.get("usuario")
        fecha_actual = date.today()

        if not id_paciente:
            mensaje = "No se seleccionó ningún paciente."
        else:
            with connection.cursor() as cursor:

                cursor.execute("""
                    SELECT id_medico
                    FROM medico
                    WHERE id_usuario = %s
                """, [id_usuario])

                medico = cursor.fetchone()

                if not medico:
                    mensaje = "El usuario no está registrado como médico."
                else:
                    id_medico = medico[0]

                    cursor.execute("""
                        SELECT
                            id_paciente,
                            nombre,
                            apellido,
                            dni,
                            grupo_sanguineo,
                            antecedentes
                        FROM paciente
                        WHERE id_paciente = %s
                    """, [id_paciente])

                    paciente = cursor.fetchone()

                    if paciente:
                        cursor.execute("""
                            INSERT INTO historial_medico
                            (
                                id_paciente,
                                fecha_registro
                            )
                            VALUES (%s, %s)
                        """, [
                            id_paciente,
                            fecha_actual
                        ])

                        id_historial = cursor.lastrowid

                        cursor.execute("""
                            INSERT INTO diagnostico
                            (
                                id_historial,
                                id_medico,
                                fecha,
                                sintomas,
                                diagnostico
                            )
                            VALUES (%s, %s, %s, %s, %s)
                        """, [
                            id_historial,
                            id_medico,
                            fecha_actual,
                            sintomas,
                            diagnostico
                        ])

                        id_diagnostico = cursor.lastrowid

                        if tratamiento:
                            cursor.execute("""
                                INSERT INTO tratamiento
                                (
                                    id_diagnostico,
                                    descripcion,
                                    fecha_inicio
                                )
                                VALUES (%s, %s, %s)
                            """, [
                                id_diagnostico,
                                tratamiento,
                                fecha_actual
                            ])

                        mensaje = "Consulta guardada correctamente."

    if paciente:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    d.fecha,
                    d.sintomas,
                    d.diagnostico,
                    t.descripcion
                FROM historial_medico h
                INNER JOIN diagnostico d
                    ON h.id_historial = d.id_historial
                LEFT JOIN tratamiento t
                    ON d.id_diagnostico = t.id_diagnostico
                WHERE h.id_paciente = %s
                ORDER BY d.fecha DESC
            """, [paciente[0]])

            historial = cursor.fetchall()

    return render(request, "App/medico.html", {
        "paciente": paciente,
        "pacientes": pacientes,
        "historial": historial,
        "mensaje": mensaje,
        "dnis": dnis,
        "nombres": nombres
    })


@requiere_rol("Secretaria")
def secretaria(request):
    return render(request, "App/secretaria.html")