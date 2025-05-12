import os
import mysql.connector
from mysql.connector import Error
from bcrypt import hashpw, gensalt, checkpw
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import base64
import hashlib # Para hashing de email/RUT para búsquedas

# Cargar variables de entorno
load_dotenv()

# Credenciales de la base de datos desde .env
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWD = os.getenv('DB_PASSWD')
DB_NAME = os.getenv('DB_NAME')

# Clave para cifrado/descifrado (desde .env)
CIPHER_PASS = os.getenv('CIPHER_PASS')

def get_fernet_key_from_cipher_pass():
    """
    Deriva una clave Fernet a partir de la CIPHER_PASS del .env.
    """
    if not CIPHER_PASS:
        print("Error: CIPHER_PASS no está configurada en .env.")
        return None
    # Usar un hash SHA256 de la CIPHER_PASS para obtener 32 bytes
    key_hash = hashlib.sha256(CIPHER_PASS.encode('utf-8')).digest()
    # Codificar en base64url seguro para Fernet (los primeros 32 bytes del hash)
    key = base64.urlsafe_b64encode(key_hash)
    return Fernet(key)

def encrypt_data(data, fernet_cipher):
    """
    Cifra los datos usando Fernet.
    """
    if not data:
        return None
    if not fernet_cipher:
        return None
    try:
        # Los datos deben ser bytes para cifrar
        return fernet_cipher.encrypt(data.encode('utf-8'))
    except Exception as e:
        print(f"Error al cifrar datos: {e}")
        return None

def decrypt_data(encrypted_data, fernet_cipher):
    """
    Descifra los datos usando Fernet.
    """
    if not encrypted_data:
        return None
    if not fernet_cipher:
        return None
    try:
        # Los datos cifrados son bytes, y el resultado de desencriptar es bytes.
        # Luego se decodifica a string para mostrar.
        return fernet_cipher.decrypt(encrypted_data).decode('utf-8')
    except Exception as e:
        print(f"Error al descifrar datos: {e}")
        return None

def hash_password(password):
    """
    Genera un hash bcrypt de la contraseña.
    """
    return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

def check_password(password, hashed_password):
    """
    Verifica una contraseña contra su hash bcrypt.
    """
    return checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def hash_for_search(data):
    """Genera un hash SHA256 para campos que se usarán en búsquedas."""
    if not data:
        return None
    return hashlib.sha256(data.lower().encode('utf-8')).hexdigest().encode('utf-8') # Retornar bytes para VARBINARY

def connect():
    """
    Establece una conexión a la base de datos.
    """
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWD,
            database=DB_NAME
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    return None

# Funciones de usuario

def registrar_usuario(conn, username, password, email, telefono, rut, direccion, nota_secreta=None):
    """
    Registra un nuevo usuario, cifrando email, telefono, rut, direccion y nota_secreta.
    El nivel inicial se establecerá a 'pending' por defecto en la DB.
    """
    if not conn or not conn.is_connected():
        print("Error: No hay conexión a la base de datos.")
        return False

    hashed_password = hash_password(password)
    fernet_cipher = get_fernet_key_from_cipher_pass()

    if not fernet_cipher:
        print("Error: No se pudo obtener la clave Fernet. Imposible cifrar datos.")
        return False

    try:
        # Cifrar cada campo sensible
        encrypted_email = encrypt_data(email, fernet_cipher)
        encrypted_telefono = encrypt_data(telefono, fernet_cipher)
        encrypted_rut = encrypt_data(rut, fernet_cipher)
        encrypted_direccion = encrypt_data(direccion, fernet_cipher)
        encrypted_nota_secreta = encrypt_data(nota_secreta, fernet_cipher) if nota_secreta else None

        # Generar hashes para búsqueda (si las columnas existen y son necesarias)
        email_search_hash = hash_for_search(email)
        rut_search_hash = hash_for_search(rut)

    except Exception as e:
        print(f"Error al cifrar datos o generar hashes: {e}")
        return False

    cursor = None
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO usuarios (usuario, hash, email, telefono, rut, direccion, nota_secreta, email_hash, rut_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (username, hashed_password,
                               encrypted_email, encrypted_telefono, encrypted_rut,
                               encrypted_direccion, encrypted_nota_secreta,
                               email_search_hash, rut_search_hash))
        conn.commit()
        return True
    except Error as err:
        if err.errno == 1062: # Error de clave duplicada (UNIQUE constraint)
            print(f"Error: El usuario '{username}' o algún campo UNIQUE (email/RUT) ya existe.")
        else:
            print(f"Error al registrar usuario: {err}")
        conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()

def login_usuario(conn, username, password):
    """
    Verifica credenciales y retorna True, los datos descifrados del usuario
    (incluida nota secreta) y el nivel, junto con el ID del usuario.
    """
    if not conn or not conn.is_connected():
        return False, None, None, None, None, None, None, None # Retorna éxito, nota, nivel, email, tel, rut, dir, user_id

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True) # Retorna resultados como diccionarios
        query = "SELECT id, hash, nota_secreta, nivel, email, telefono, rut, direccion FROM usuarios WHERE usuario = %s"
        cursor.execute(query, (username,))
        user_data = cursor.fetchone()

        if user_data:
            stored_hash = user_data['hash']
            if check_password(password, stored_hash):
                fernet_cipher = get_fernet_key_from_cipher_pass()
                if not fernet_cipher:
                    print("Error: No se pudo obtener la clave Fernet. Imposible descifrar datos.")
                    return False, None, None, None, None, None, None, None

                # Desencriptar cada campo cifrado al recuperarlo
                decrypted_note = decrypt_data(user_data['nota_secreta'], fernet_cipher) if user_data['nota_secreta'] else None
                decrypted_email = decrypt_data(user_data['email'], fernet_cipher) if user_data['email'] else None
                decrypted_telefono = decrypt_data(user_data['telefono'], fernet_cipher) if user_data['telefono'] else None
                decrypted_rut = decrypt_data(user_data['rut'], fernet_cipher) if user_data['rut'] else None
                decrypted_direccion = decrypt_data(user_data['direccion'], fernet_cipher) if user_data['direccion'] else None

                # Retornar los datos descifrados y el ID del usuario
                return True, decrypted_note, user_data['nivel'], \
                       decrypted_email, decrypted_telefono, decrypted_rut, \
                       decrypted_direccion, user_data['id']
            else:
                return False, None, None, None, None, None, None, None # Contraseña incorrecta
        else:
            return False, None, None, None, None, None, None, None # Usuario no encontrado
    except Exception as err: # Captura cualquier excepción de descifrado o DB
        print(f"Error al intentar iniciar sesión para '{username}': {err}")
        return False, None, None, None, None, None, None, None
    finally:
        if cursor:
            cursor.close()

def cambiar_contrasena(conn, username, new_password):
    """
    Cambia la contraseña de un usuario.
    """
    if not conn or not conn.is_connected():
        return False, "Error de conexión a la base de datos."

    hashed_password = hash_password(new_password)
    cursor = None
    try:
        cursor = conn.cursor()
        query = "UPDATE usuarios SET hash = %s WHERE usuario = %s"
        cursor.execute(query, (hashed_password, username))
        conn.commit()
        if cursor.rowcount > 0:
            return True, "Contraseña actualizada exitosamente."
        else:
            return False, "Usuario no encontrado."
    except Error as err:
        print(f"Error al cambiar contraseña: {err}")
        conn.rollback()
        return False, f"Error al actualizar contraseña: {err}"
    finally:
        if cursor:
            cursor.close()

# Funciones de administración (para usuario master)

def obtener_todos_los_usuarios(conn):
    """
    Retorna una lista de todos los usuarios con su información básica y nivel.
    No descifra datos sensibles aquí, solo para la lista general.
    """
    if not conn or not conn.is_connected():
        return []

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, usuario, nivel, fecha_creacion FROM usuarios ORDER BY fecha_creacion DESC"
        cursor.execute(query)
        users = cursor.fetchall()
        # Reemplazar 'None' por 'Pendiente de Aprobación' para la UI
        for user in users:
            if user['nivel'] is None or user['nivel'] == 'pending': # Asegura que 'pending' también se muestre bien
                user['nivel'] = 'Pendiente de Aprobación'
        return users
    except Error as err:
        print(f"Error al obtener usuarios: {err}")
        return []
    finally:
        if cursor:
            cursor.close()

def obtener_usuario_por_id(conn, user_id):
    """
    Retorna los datos de un usuario específico por su ID, descifrando los campos sensibles.
    Útil para una página de edición de usuario.
    """
    if not conn or not conn.is_connected():
        return None

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM usuarios WHERE id = %s"
        cursor.execute(query, (user_id,))
        user_data = cursor.fetchone()

        if user_data:
            fernet_cipher = get_fernet_key_from_cipher_pass()
            if not fernet_cipher:
                print("Error: No se pudo obtener la clave Fernet para descifrar.")
                return user_data # Retorna datos cifrados si no puede descifrar

            # Desencriptar los campos sensibles
            user_data['email_decrypted'] = decrypt_data(user_data['email'], fernet_cipher) if user_data['email'] else None
            user_data['telefono_decrypted'] = decrypt_data(user_data['telefono'], fernet_cipher) if user_data['telefono'] else None
            user_data['rut_decrypted'] = decrypt_data(user_data['rut'], fernet_cipher) if user_data['rut'] else None
            user_data['direccion_decrypted'] = decrypt_data(user_data['direccion'], fernet_cipher) if user_data['direccion'] else None
            user_data['nota_secreta_decrypted'] = decrypt_data(user_data['nota_secreta'], fernet_cipher) if user_data['nota_secreta'] else None
            
            # Asegurarse de que el nivel sea 'pending' para mostrar en UI si es None o 'pending'
            if user_data['nivel'] is None or user_data['nivel'] == 'pending':
                user_data['nivel_display'] = 'Pendiente de Aprobación'
            else:
                user_data['nivel_display'] = user_data['nivel']

            return user_data
        return None
    except Error as err:
        print(f"Error al obtener usuario por ID: {err}")
        return None
    finally:
        if cursor:
            cursor.close()

def actualizar_nivel_usuario(conn, user_id, nuevo_nivel):
    """
    Actualiza el nivel de un usuario específico.
    """
    if not conn or not conn.is_connected():
        return False, "Error de conexión a la base de datos."

    # Validar que el nuevo_nivel sea uno de los valores ENUM permitidos (excluyendo 'pending' aquí)
    if nuevo_nivel not in ['user', 'admin', 'master']:
        return False, "Nivel de usuario no válido para asignación."

    cursor = None
    try:
        cursor = conn.cursor()
        query = "UPDATE usuarios SET nivel = %s WHERE id = %s"
        cursor.execute(query, (nuevo_nivel, user_id))
        conn.commit()
        if cursor.rowcount > 0:
            return True, "Nivel de usuario actualizado exitosamente."
        else:
            return False, "Usuario no encontrado o nivel ya era el mismo."
    except Error as err:
        print(f"Error al actualizar nivel de usuario: {err}")
        conn.rollback()
        return False, f"Error al actualizar nivel: {err}"
    finally:
        if cursor:
            cursor.close()

def eliminar_usuario(conn, user_id):
    """
    Elimina un usuario de la base de datos.
    """
    if not conn or not conn.is_connected():
        return False, "Error de conexión a la base de datos."

    cursor = None
    try:
        cursor = conn.cursor()
        query = "DELETE FROM usuarios WHERE id = %s"
        cursor.execute(query, (user_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return True, "Usuario eliminado exitosamente."
        else:
            return False, "Usuario no encontrado."
    except Error as err:
        print(f"Error al eliminar usuario: {err}")
        conn.rollback()
        return False, f"Error al eliminar usuario: {err}"
    finally:
        if cursor:
            cursor.close()