import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import timedelta
from functools import wraps

import functions  # Asegúrate de que functions.py esté en el mismo directorio o en sys.path

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

        conn = functions.connect()
        if conn:
            if functions.registrar_usuario(
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

        conn = functions.connect()
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
            ) = functions.login_usuario(conn, username, password)
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

        conn = functions.connect()
        if conn:
            success, message = functions.cambiar_contrasena(
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
    conn = functions.connect()
    if conn:
        users = functions.obtener_todos_los_usuarios(conn)
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
    conn = functions.connect()
    if not conn:
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('admin_users'))

    if request.method == 'POST':
        new_level = request.form.get('nivel')
        if new_level:
            success, message = functions.actualizar_nivel_usuario(
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
    user = functions.obtener_usuario_por_id(conn, user_id)
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

    conn = functions.connect()
    if conn:
        success, message = functions.eliminar_usuario(conn, user_id)
        flash(message, 'success' if success else 'danger')
        conn.close()
    else:
        flash('Error de conexión a la base de datos.', 'danger')
    return redirect(url_for('admin_users'))


# Rutas de ejemplo para diferentes niveles (para demostración)
@app.route('/intermedio')
@requiere_nivel(['user', 'admin', 'master'])
def intermedio():
    return render_template(
        'intermedio.html'
    )  # Contenido exclusivo para usuarios con nivel 'user' o superior


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


if __name__ == '__main__':
    app.run(debug=True)  # En producción, debug=False

## Changelog
# - Se agregó la función de cambiar contraseña.
# - Se agregó la función de eliminar usuario.   
# - Se agregó la función de editar usuario.
# - Se agregó la función de registrar usuario.
# - Se agregó la función de login.
# - se edita propiedad footer