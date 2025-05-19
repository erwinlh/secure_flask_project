import os
from datetime import timedelta
from functools import wraps
import time
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, Response, stream_with_context
from utils.web import procesar_fiscal_stream, exportar_consulta_xls, subir_a_defontana_por_fechas_stream, procesar_fiscal_gde_stream 
import utils.auth as auth  # Asegúrate de que functions.py esté en el mismo directorio o en sys.path
import utils.common as common
import traceback

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Asegúrate de tener esto en tu .env
app.permanent_session_lifetime = timedelta(minutes=30)  # Sesiones permanentes por 30 minutos


# Decoradores para control de acceso
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def requiere_nivel(niveles_requeridos):
    def decorador(f):
        @wraps(f)
        def funcion_decorada(*args, **kwargs):
            if 'username' not in session:
                flash('Debes iniciar sesión para acceder a esta página.', 'warning')
                return redirect(url_for('login'))

            user_level = session.get('nivel')  # Obtiene el nivel. Puede ser 'pending' o None.

            # Si el nivel es 'pending' o None, siempre redirigir a la página de cuenta pendiente
            if user_level is None or user_level == 'pending':
                flash(
                    f'Tu cuenta está pendiente de aprobación y no puede acceder a esta funcionalidad.',
                    'danger',
                )
                return redirect(url_for('cuenta_pendiente'))

            # Si el nivel no está en los niveles requeridos, acceso denegado
            if user_level not in niveles_requeridos:
                flash(f'Acceso denegado. Tu cuenta no tiene el nivel requerido.', 'danger')
                return redirect(url_for('dashboard'))  # O a una página de acceso denegado más general
            return f(*args, **kwargs)

        return funcion_decorada

    return decorador


# --- RUTAS ---
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        if session.get('nivel') is None or session.get('nivel') == 'pending':
            return redirect(url_for('cuenta_pendiente'))
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        telefono = request.form.get('telefono')  # Usar .get para campos opcionales
        rut = request.form.get('rut')
        direccion = request.form.get('direccion')
        nota_secreta = request.form.get('nota_secreta')

        if len(password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres.', 'danger')
            return (
                render_template(
                    'register.html',
                    username=username,
                    email=email,
                    telefono=telefono,
                    rut=rut,
                    direccion=direccion,
                    nota_secreta=nota_secreta,
                ),
            )

        # Validaciones básicas de email y RUT antes de cifrar
        if not email or '@' not in email:
            flash('Formato de email inválido.', 'danger')
            return (
                render_template(
                    'register.html',
                    username=username,
                    email=email,
                    telefono=telefono,
                    rut=rut,
                    direccion=direccion,
                    nota_secreta=nota_secreta,
                ),
            )

        conn = common.connect()
        if conn:
            if auth.registrar_usuario(
                conn, username, password, email, telefono, rut, direccion, nota_secreta
            ):
                flash(
                    'Cuenta creada exitosamente. Tu cuenta está pendiente de aprobación por un administrador. Recibirás una notificación cuando esté activa.',
                    'success',
                )
                conn.close()
                return redirect(url_for('login'))
            else:
                flash(
                    'Error al registrar usuario. El usuario ya podría existir o hubo un problema con los datos.',
                    'danger',
                )
            conn.close()
        else:
            flash('Error al conectar a la base de datos.', 'danger')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        if session.get('nivel') is None or session.get('nivel') == 'pending':
            return redirect(url_for('cuenta_pendiente'))
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = common.connect()
        if conn:
            (
                login_successful,
                decrypted_note,
                user_level,
                decrypted_email,
                decrypted_telefono,
                decrypted_rut,
                decrypted_direccion,
                user_id,
            ) = auth.login_usuario(conn, username, password)
            conn.close()

            if login_successful:
                session['username'] = username
                session['nivel'] = user_level  # Esto puede ser 'pending' o None
                session['user_id'] = user_id  # Almacena el ID del usuario en la sesión
                session.permanent = True  # Hace la sesión permanente (con el timedelta)

                # Guarda los datos descifrados en la sesión (¡Solo si son necesarios para mostrar en la UI de la sesión!)
                # Podrías recuperarlos de la DB cada vez que se necesiten, es más seguro que guardarlos en la sesión.
                # Sin embargo, para mostrar en el dashboard o perfil, es práctico.
                session['email'] = decrypted_email
                session['telefono'] = decrypted_telefono
                session['rut'] = decrypted_rut
                session['direccion'] = decrypted_direccion
                session['nota_secreta'] = decrypted_note

                if user_level is None or user_level == 'pending':
                    flash(
                        'Tu cuenta está pendiente de aprobación. Por favor, espera a que un administrador la active.',
                        'info',
                    )
                    return redirect(url_for('cuenta_pendiente'))
                else:
                    flash('Inicio de sesión exitoso!', 'success')
                    return redirect(url_for('dashboard'))
            else:
                flash('Usuario o contraseña incorrectos.', 'danger')
        else:
            flash('Error al conectar a la base de datos.', 'danger')
    return render_template('login.html')


@app.route('/dashboard')
@login_required
# Este decorador de nivel en el dashboard es redundante con la lógica en login_required y requiere_nivel,
# pero lo dejo para énfasis visual. La lógica de redirección a cuenta_pendiente ya se maneja en `requiere_nivel`.
@requiere_nivel(['user', 'admin', 'master'])  # Solo si el nivel NO es 'pending' o None.
def dashboard():
    user_level = session.get('nivel', 'unknown')  # Nivel ya estará asignado y válido aquí
    return render_template(
        'dashboard.html', username=session['username'], user_level=user_level
    )


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('change_password.html')

        if len(new_password) < 8:
            flash('La nueva contraseña debe tener al menos 8 caracteres.', 'danger')
            return render_template('change_password.html')

        conn = common.connect()
        if conn:
            success, message = auth.cambiar_contrasena(
                conn, session['username'], new_password
            )
            conn.close()
            if success:
                flash(message, 'success')
                # La contraseña se cambió, forzar logout por seguridad para un nuevo login
                session.pop('username', None)
                session.pop('nivel', None)
                session.pop('user_id', None)
                flash('Por favor, inicia sesión con tu nueva contraseña.', 'info')
                return redirect(url_for('login'))
            else:
                flash(message, 'danger')
        else:
            flash('Error al conectar a la base de datos.', 'danger')
    return render_template('change_password.html')


@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    session.pop('nivel', None)
    session.pop('user_id', None)
    # Eliminar otros datos sensibles de la sesión
    session.pop('email', None)
    session.pop('telefono', None)
    session.pop('rut', None)
    session.pop('direccion', None)
    session.pop('nota_secreta', None)
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('home'))


# Ruta para cuentas pendientes de aprobación
@app.route('/cuenta_pendiente')
@login_required
def cuenta_pendiente():
    # Si el usuario ya tiene un nivel válido, redirigirlo al dashboard
    if session.get('nivel') is not None and session.get('nivel') != 'pending':
        return redirect(url_for('dashboard'))
    return render_template('cuenta_pendiente.html', username=session.get('username'))


# --- RUTAS DE ADMINISTRACIÓN DE USUARIOS (Solo para 'master') ---
@app.route('/admin/users')
@requiere_nivel(['master'])  # Solo el usuario 'master' puede acceder a esta ruta
def admin_users():
    conn = common.connect()
    if conn:
        users = auth.obtener_todos_los_usuarios(conn)
        conn.close()
        return render_template('admin_users.html', users=users)
    else:
        flash(
            'Error al conectar a la base de datos para obtener usuarios.', 'danger'
        )
        return redirect(url_for('dashboard'))


@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@requiere_nivel(['master'])
def admin_edit_user(user_id):
    conn = common.connect()
    if not conn:
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('admin_users'))

    if request.method == 'POST':
        new_level = request.form.get('nivel')
        if new_level:
            success, message = auth.actualizar_nivel_usuario(
                conn, user_id, new_level
            )
            flash(message, 'success' if success else 'danger')
            conn.close()
            return redirect(url_for('admin_users'))
        else:
            flash('Nivel no válido.', 'danger')
            conn.close()
            return redirect(url_for('admin_edit_user', user_id=user_id))

    # GET request
    user = auth.obtener_usuario_por_id(conn, user_id)
    conn.close()
    if user:
        return render_template('admin_edit_user.html', user=user)
    else:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('admin_users'))


@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@requiere_nivel(['master'])
def admin_delete_user(user_id):
    # No permitir que el master se elimine a sí mismo
    if session.get('user_id') and int(user_id) == session['user_id']:
        flash('No puedes eliminar tu propia cuenta de master.', 'danger')
        return redirect(url_for('admin_users'))

    conn = common.connect()
    if conn:
        success, message = auth.eliminar_usuario(conn, user_id)
        flash(message, 'success' if success else 'danger')
        conn.close()
    else:
        flash('Error de conexión a la base de datos.', 'danger')
    return redirect(url_for('admin_users'))


# Rutas de ejemplo para diferentes niveles (para demostración)
@app.route('/marinaDunas')
@requiere_nivel(['user', 'admin', 'master'])
def marinaDunas():
    return render_template(
        'marinaDunas.html'
    )  # Contenido exclusivo para usuarios con nivel 'user' o superior

@app.route('/marinaHoteles')
@requiere_nivel(['user', 'admin', 'master'])
def marinaHoteles():
    return render_template(
        'marinaHoteles.html'
    )
    
@app.route('/revicentro')
@requiere_nivel(['user', 'admin', 'master'])
def revicentro():
    return render_template(
        'revicentro.html'
    )


@app.route('/avanzado')
@requiere_nivel(['admin', 'master'])
def avanzado():
    return render_template(
        'avanzado.html'
    )  # Contenido exclusivo para usuarios con nivel 'admin' o 'master'


@app.route('/master_function')
@requiere_nivel(['master'])
def master_function():
    return render_template(
        'master_function.html'
    )  # Contenido exclusivo para 'master'



@app.route('/procesar_archivo', methods=['POST']) # Mantenemos POST para recibir el archivo
def procesar_archivo():
    if 'file1' not in request.files:
        # Es mejor devolver un error JSON o un mensaje claro
        return jsonify({'status': 'error', 'message': 'No se encontró el archivo en la solicitud.'}), 400

    archivo = request.files['file1']

    if archivo.filename == '':
        return jsonify({'status': 'error', 'message': 'No se seleccionó ningún archivo.'}), 400

    if archivo: #and archivo.filename.endswith('.xlsx'): # Puedes añadir validación de extensión
        print(f"Archivo recibido: {archivo.filename}")

        # Define la función generadora que Flask usará para el stream
        def generate_stream():
            # Pasamos el objeto 'archivo' (FileStorage) directamente
            for message in procesar_fiscal_stream(archivo):
                # Formato SSE: "data: <mensaje>\n\n"
                yield f"data: {message}\n\n"
                # Pequeña pausa para asegurar que el navegador reciba los eventos
                time.sleep(0.01)
            # Puedes enviar un evento especial para indicar el final si lo deseas
            yield "event: end\ndata: Proceso finalizado.\n\n"

        # Retorna una respuesta de tipo stream
        return Response(stream_with_context(generate_stream()), mimetype='text/event-stream')
    else:
        # Mensaje si el archivo no es válido o no existe
        return jsonify({'status': 'error', 'message': 'Archivo no válido o no proporcionado.'}), 400

@app.route('/procesar_archivo_GDE', methods=['POST']) # Mantenemos POST para recibir el archivo
def procesar_archivo_GDE():
    if 'file-gde' not in request.files:
        # Es mejor devolver un error JSON o un mensaje claro
        return jsonify({'status': 'error', 'message': 'No se encontró el archivo en la solicitud.'}), 400

    archivo = request.files['file-gde']

    if archivo.filename == '':
        return jsonify({'status': 'error', 'message': 'No se seleccionó ningún archivo.'}), 400

    if archivo: #and archivo.filename.endswith('.xlsx'): # Puedes añadir validación de extensión
        print(f"Archivo recibido: {archivo.filename}")

        # Define la función generadora que Flask usará para el stream
        def generate_stream():
            # Pasamos el objeto 'archivo' (FileStorage) directamente
            for message in procesar_fiscal_gde_stream(archivo):
                # Formato SSE: "data: <mensaje>\n\n"
                yield f"data: {message}\n\n"
                # Pequeña pausa para asegurar que el navegador reciba los eventos
                time.sleep(0.01)
            # Puedes enviar un evento especial para indicar el final si lo deseas
            yield "event: end\ndata: Proceso finalizado.\n\n"

        # Retorna una respuesta de tipo stream
        return Response(stream_with_context(generate_stream()), mimetype='text/event-stream')
    else:
        # Mensaje si el archivo no es válido o no existe
        return jsonify({'status': 'error', 'message': 'Archivo no válido o no proporcionado.'}), 400


@app.route('/exportar_archivo', methods=['POST'])
def exportar_archivo():
    try:
        # Obtener fechas del formulario enviado por JavaScript
        desde = request.form.get('fechaDesde')
        hasta = request.form.get('fechaHasta')
        # Validar que las fechas fueron recibidas
        if not desde or not hasta:
            return jsonify({'status': 'error', 'message': 'Fechas "Desde" y "Hasta" son requeridas.'}), 400

        print(f"Recibida solicitud de exportación desde {desde} hasta {hasta}")

        # Llamar a la función que ahora devuelve (buffer, filename)
        file_buffer, filename = exportar_consulta_xls(desde, hasta)

        print(f"Enviando archivo: {filename}")

        # Enviar el archivo desde el buffer de memoria
        return send_file(
            file_buffer,
            mimetype='application/vnd.ms-excel', # Mimetype correcto para .xls
            as_attachment=True, # Indica al navegador que lo descargue
            download_name=filename # Nombre que tendrá el archivo descargado
        )

    except ConnectionError as db_conn_err:
         print(f"Error de conexión DB en exportar_archivo: {db_conn_err}")
         return jsonify({'status': 'error', 'message': f'Error de base de datos: {db_conn_err}'}), 500
    except ValueError as val_err: # Captura errores lanzados desde exportar_consulta_xls
         print(f"Error de valor en exportar_archivo: {val_err}")
         return jsonify({'status': 'error', 'message': f'Error durante la exportación: {val_err}'}), 500
    except Exception as e:
        print(f"Error inesperado en /exportar_archivo: {e}")
        traceback.print_exc() # Imprime el stack trace completo en la consola del servidor
        return jsonify({'status': 'error', 'message': 'Ocurrió un error interno al generar el archivo.'}), 500

@app.route('/subir_defontana', methods=['POST'])
def subir_defontana():
    # Obtener datos del formulario
    desde = request.form.get('fechaDesde')
    hasta = request.form.get('fechaHasta')
    tipoDte = request.form.get('tipoDte')

    # Validar datos
    if not desde or not hasta or not tipoDte:
        # Para SSE, es mejor no devolver JSON aquí, el error se manejará en el stream
        # o el cliente JS debería validar antes de llamar.
        # Por simplicidad, dejaremos que la función stream maneje la validación inicial si es necesario,
        # o podrías devolver un error 400 plano, pero el JS actual no lo manejaría bien.
        # Lo ideal es validar en JS primero.
        # Si la validación falla aquí, podríamos iniciar un stream que solo envíe el error.
        def error_stream():
            yield "data: Error: Faltan parámetros (Fechas o Tipo DTE).\n\n"
            yield "event: end\ndata: Proceso terminado con error.\n\n"
        return Response(stream_with_context(error_stream()), mimetype='text/event-stream', status=400)


    print(f"Recibida solicitud de subida a Defontana desde {desde} hasta {hasta} para tipo {tipoDte}")

    # Define la función generadora para el stream SSE
    def generate_stream():
        try:
            # Llama a la función generadora que hace el trabajo real
            for message in subir_a_defontana_por_fechas_stream(desde, hasta, tipoDte):
                yield f"data: {message}\n\n"
                time.sleep(0.01) # Pausa para el navegador
            # Señal de finalización (opcional pero útil)
            yield "event: end\ndata: Finalizado.\n\n"
        except Exception as e:
             # Captura errores inesperados *durante* la generación del stream
             error_msg = f"Error inesperado en el servidor durante el stream: {e}"
             print(error_msg)
             traceback.print_exc()
             yield f"data: Error Crítico: {error_msg}\n\n"
             yield "event: end\ndata: Proceso terminado con error crítico.\n\n"


    # Retorna la respuesta de tipo stream
    return Response(stream_with_context(generate_stream()), mimetype='text/event-stream')



if __name__ == '__main__':
    app.run(debug=False, port=8000)  # En producción, debug=False

## Changelog
# - Se agregó la función de cambiar contraseña.
# - Se agregó la función de eliminar usuario.   
# - Se agregó la función de editar usuario.
# - Se agregó la función de registrar usuario.
# - Se agregó la función de login.
# - se edita propiedad footer
