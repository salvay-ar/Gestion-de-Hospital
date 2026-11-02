from django.db import connection
from django.shortcuts import render, redirect
from .decorators import requiere_rol
from datetime import date, datetime
from django.db import transaction


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
    mensaje = ""
    tipo_mensaje = ""
    paciente_edicion = None
    cita_edicion = None
    resultados_pacientes = []
    busqueda = ""

    if request.method == "POST":
        accion = request.POST.get("accion", "")

        # REGISTRAR O MODIFICAR PACIENTE
        if accion == "guardar_paciente":
            id_paciente = request.POST.get("id_paciente", "").strip()
            dni = request.POST.get("dni", "").strip()
            nombre = request.POST.get("nombre", "").strip()
            apellido = request.POST.get("apellido", "").strip()
            fecha_nacimiento = request.POST.get("fecha_nacimiento") or None
            telefono = request.POST.get("telefono", "").strip() or None
            direccion = request.POST.get("direccion", "").strip() or None
            grupo_sanguineo = request.POST.get("grupo_sanguineo", "").strip() or None
            antecedentes = request.POST.get("antecedentes", "").strip() or None

            if not dni or not nombre or not apellido:
                mensaje = "DNI, nombre y apellido son obligatorios."
                tipo_mensaje = "error"

            elif fecha_nacimiento and fecha_nacimiento > date.today().isoformat():
                mensaje = "La fecha de nacimiento no puede ser futura."
                tipo_mensaje = "error"

            else:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id_paciente
                        FROM paciente
                        WHERE dni = %s
                        AND id_paciente != %s
                    """, [dni, id_paciente or 0])

                    dni_existente = cursor.fetchone()

                    if dni_existente:
                        mensaje = "Ya existe un paciente con ese DNI."
                        tipo_mensaje = "error"

                    else:
                        if id_paciente:
                            cursor.execute("""
                                UPDATE paciente
                                SET dni = %s,
                                    nombre = %s,
                                    apellido = %s,
                                    fecha_nacimiento = %s,
                                    telefono = %s,
                                    direccion = %s,
                                    grupo_sanguineo = %s,
                                    antecedentes = %s
                                WHERE id_paciente = %s
                            """, [
                                dni,
                                nombre,
                                apellido,
                                fecha_nacimiento,
                                telefono,
                                direccion,
                                grupo_sanguineo,
                                antecedentes,
                                id_paciente
                            ])

                            mensaje = "Paciente modificado correctamente."

                        else:
                            cursor.execute("""
                                INSERT INTO paciente (
                                    dni,
                                    nombre,
                                    apellido,
                                    fecha_nacimiento,
                                    telefono,
                                    direccion,
                                    grupo_sanguineo,
                                    antecedentes
                                )
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, [
                                dni,
                                nombre,
                                apellido,
                                fecha_nacimiento,
                                telefono,
                                direccion,
                                grupo_sanguineo,
                                antecedentes
                            ])

                            mensaje = "Paciente registrado correctamente."

                        tipo_mensaje = "exito"

        # BUSCAR PACIENTES
        elif accion == "buscar_paciente":
            busqueda = request.POST.get("busqueda", "").strip()

            if busqueda:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT
                            id_paciente,
                            dni,
                            nombre,
                            apellido,
                            fecha_nacimiento,
                            telefono,
                            direccion,
                            grupo_sanguineo,
                            antecedentes
                        FROM paciente
                        WHERE dni LIKE %s
                           OR nombre LIKE %s
                           OR apellido LIKE %s
                           OR CONCAT(nombre, ' ', apellido) LIKE %s
                        ORDER BY apellido, nombre
                    """, [
                        f"%{busqueda}%",
                        f"%{busqueda}%",
                        f"%{busqueda}%",
                        f"%{busqueda}%"
                    ])

                    resultados_pacientes = cursor.fetchall()

                if not resultados_pacientes:
                    mensaje = "No se encontraron pacientes."
                    tipo_mensaje = "error"
            else:
                mensaje = "Ingresá un DNI, nombre o apellido."
                tipo_mensaje = "error"

        # CARGAR PACIENTE PARA MODIFICAR
        elif accion == "editar_paciente":
            id_paciente = request.POST.get("id_paciente")

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        id_paciente,
                        dni,
                        nombre,
                        apellido,
                        fecha_nacimiento,
                        telefono,
                        direccion,
                        grupo_sanguineo,
                        antecedentes
                    FROM paciente
                    WHERE id_paciente = %s
                """, [id_paciente])

                paciente_edicion = cursor.fetchone()

            if not paciente_edicion:
                mensaje = "No se encontró el paciente."
                tipo_mensaje = "error"

        # AGENDAR O REPROGRAMAR CITA
        elif accion == "guardar_cita":
            id_cita = request.POST.get("id_cita", "").strip()
            id_paciente = request.POST.get("id_paciente", "").strip()
            id_medico = request.POST.get("id_medico", "").strip()
            fecha_cita = request.POST.get("fecha", "").strip()
            hora_cita = request.POST.get("hora", "").strip()

            if not id_paciente or not id_medico or not fecha_cita or not hora_cita:
                mensaje = "Completá todos los campos de la cita."
                tipo_mensaje = "error"

            elif fecha_cita < date.today().isoformat():
                mensaje = "No se pueden agendar citas en fechas pasadas."
                tipo_mensaje = "error"

            else:
                try:
                    # Verificar paciente, médico y disponibilidad.
                    with transaction.atomic():
                        with connection.cursor() as cursor:
                            cursor.execute("""
                                SELECT id_paciente
                                FROM paciente
                                WHERE id_paciente = %s
                            """, [id_paciente])

                            paciente_existe = cursor.fetchone()

                            cursor.execute("""
                                SELECT id_medico
                                FROM medico
                                WHERE id_medico = %s
                            """, [id_medico])

                            medico_existe = cursor.fetchone()

                            if not paciente_existe or not medico_existe:
                                mensaje = "El paciente o el médico seleccionado no existe."
                                tipo_mensaje = "error"

                            else:
                                cursor.execute("""
                                    SELECT id_cita
                                    FROM cita
                                    WHERE id_medico = %s
                                      AND fecha = %s
                                      AND hora = %s
                                      AND estado != 'Cancelada'
                                      AND id_cita != %s
                                """, [
                                    id_medico,
                                    fecha_cita,
                                    hora_cita,
                                    id_cita or 0
                                ])

                                conflicto = cursor.fetchone()

                                if conflicto:
                                    mensaje = "Ese médico ya tiene una cita en ese horario."
                                    tipo_mensaje = "error"

                                elif id_cita:
                                    cursor.execute("""
                                        UPDATE cita
                                        SET id_paciente = %s,
                                            id_medico = %s,
                                            fecha = %s,
                                            hora = %s
                                        WHERE id_cita = %s
                                          AND estado != 'Cancelada'
                                    """, [
                                        id_paciente,
                                        id_medico,
                                        fecha_cita,
                                        hora_cita,
                                        id_cita
                                    ])

                                    if cursor.rowcount:
                                        mensaje = "Cita reprogramada correctamente."
                                        tipo_mensaje = "exito"
                                    else:
                                        mensaje = "No se encontró la cita o ya fue cancelada."
                                        tipo_mensaje = "error"

                                else:
                                    cursor.execute("""
                                        INSERT INTO cita (
                                            id_paciente,
                                            id_medico,
                                            fecha,
                                            hora,
                                            estado
                                        )
                                        VALUES (%s, %s, %s, %s, %s)
                                    """, [
                                        id_paciente,
                                        id_medico,
                                        fecha_cita,
                                        hora_cita,
                                        "Pendiente"
                                    ])

                                    mensaje = "Cita agendada correctamente."
                                    tipo_mensaje = "exito"

                except Exception:
                    mensaje = "Ocurrió un error al guardar la cita. Revisá los datos."
                    tipo_mensaje = "error"

        # CARGAR CITA PARA REPROGRAMAR
        elif accion == "editar_cita":
            id_cita = request.POST.get("id_cita")

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        id_cita,
                        id_paciente,
                        id_medico,
                        fecha,
                        hora,
                        estado
                    FROM cita
                    WHERE id_cita = %s
                      AND estado != 'Cancelada'
                """, [id_cita])

                cita_edicion = cursor.fetchone()

            if not cita_edicion:
                mensaje = "No se encontró la cita o ya fue cancelada."
                tipo_mensaje = "error"

        # CANCELAR CITA
        elif accion == "cancelar_cita":
            id_cita = request.POST.get("id_cita")

            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE cita
                    SET estado = 'Cancelada'
                    WHERE id_cita = %s
                      AND estado != 'Cancelada'
                """, [id_cita])

                if cursor.rowcount:
                    mensaje = "Cita cancelada correctamente."
                    tipo_mensaje = "exito"
                else:
                    mensaje = "La cita no existe o ya estaba cancelada."
                    tipo_mensaje = "error"

    # DATOS PARA MOSTRAR EN LA PÁGINA
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                id_paciente,
                dni,
                nombre,
                apellido,
                fecha_nacimiento,
                telefono,
                direccion,
                grupo_sanguineo,
                antecedentes
            FROM paciente
            ORDER BY apellido, nombre
        """)
        pacientes = cursor.fetchall()

        cursor.execute("""
            SELECT
                id_medico,
                nombre,
                apellido,
                especialidad
            FROM medico
            ORDER BY apellido, nombre
        """)
        medicos = cursor.fetchall()

        cursor.execute("""
            SELECT
                c.id_cita,
                c.id_paciente,
                c.id_medico,
                p.nombre,
                p.apellido,
                p.dni,
                m.nombre,
                m.apellido,
                c.fecha,
                c.hora,
                c.estado
            FROM cita c
            INNER JOIN paciente p
                ON c.id_paciente = p.id_paciente
            INNER JOIN medico m
                ON c.id_medico = m.id_medico
            ORDER BY c.fecha, c.hora
        """)
        citas = cursor.fetchall()

    return render(request, "App/secretaria.html", {
        "mensaje": mensaje,
        "tipo_mensaje": tipo_mensaje,
        "pacientes": pacientes,
        "medicos": medicos,
        "citas": citas,
        "paciente_edicion": paciente_edicion,
        "cita_edicion": cita_edicion,
        "resultados_pacientes": resultados_pacientes,
        "busqueda": busqueda,
        "hoy": date.today().isoformat()
    })