# crear_usuario_master.py
import os
import sys
import getpass # Para solicitar la contraseña de forma segura
from dotenv import load_dotenv

# Añadir la ruta del directorio padre al sys.path para importar functions.py
# Esto asume que crear_usuario_master.py está en la raíz del proyecto,
# al mismo nivel que functions.py.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

import utils.auth as auth 

# Cargar variables de entorno (para la conexión a la DB)
load_dotenv()

def crear_master_user():
    """
    Script para crear un usuario con nivel 'master' en la base de datos.
    Solicita nombre de usuario, contraseña y una nota secreta (opcional).
    """
    print("--- Creación de Usuario Master ---")
    print("Este script creará un nuevo usuario con nivel 'master' en la base de datos.")
    print("Asegúrate de que las credenciales de tu base de datos en .env sean correctas.")

    username = input("Ingrese el nombre de usuario para el master: ").strip()
    if not username:
        print("Error: El nombre de usuario no puede estar vacío.")
        return

    password = getpass.getpass("Ingrese la contraseña para el master: ").strip()
    if not password:
        print("Error: La contraseña no puede estar vacía.")
        return
    if len(password) < 8:
        print("Error: La contraseña debe tener al menos 8 caracteres.")
        return

    confirm_password = getpass.getpass("Confirme la contraseña: ").strip()
    if password != confirm_password:
        print("Error: Las contraseñas no coinciden.")
        return

    nota_secreta = input("Ingrese una nota secreta (opcional, presione Enter para omitir): ").strip()

    conn = auth.connect()
    if conn:
        try:
            cursor = conn.cursor()
            # Verificar si el usuario ya existe
            cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", (username,))
            if cursor.fetchone():
                print(f"Error: El usuario '{username}' ya existe. Elija otro nombre de usuario o edítelo manualmente en la DB.")
                return

            # Hashear la contraseña
            hashed_password = auth.hash_password(password)

            # Encriptar la nota secreta si existe
            encrypted_note = None
            if nota_secreta:
                fernet_cipher = auth.get_fernet_key_from_cipher_pass()
                if fernet_cipher:
                    encrypted_note = auth.encrypt_data(nota_secreta, fernet_cipher)
                else:
                    print("Advertencia: No se pudo obtener la clave Fernet, la nota secreta NO se encriptará.")

            # Insertar el usuario con nivel 'master'
            query = "INSERT INTO usuarios (usuario, hash, nota_secreta, nivel) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (username, hashed_password, encrypted_note, 'master'))
            conn.commit()
            print(f"\n¡Usuario master '{username}' creado exitosamente!")
            print("Ahora puedes iniciar sesión con este usuario.")
        except Exception as e:
            conn.rollback() # Deshacer cualquier cambio en caso de error
            print(f"Ocurrió un error al crear el usuario: {e}")
            print("Asegúrate de que tu base de datos 'used_db' exista y la tabla 'usuarios' esté creada y accesible.")
        finally:
            if cursor:
                cursor.close()
            conn.close()
    else:
        print("\nError: No se pudo conectar a la base de datos.")
        print("Por favor, verifica tu archivo .env y asegúrate de que MySQL/MariaDB esté corriendo.")

if __name__ == '__main__':
    crear_master_user()