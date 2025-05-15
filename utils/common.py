import mysql.connector
import json
import os
from dotenv import load_dotenv
import base64
import xmltodict
from termcolor import colored

load_dotenv()
host = os.getenv("db_host")
user= os.getenv("db_user")
db = os.getenv("database")
passwd = os.getenv("passwd")
# Define symbols
ERROR_SYMBOL = " ✗ "
OK_SYMBOL = " ✓ "
ASK_SYMBOL = " ? "
NEW_SYMBOL = " # "
WARNING_SYMBOL = " ! "

def pausa():
    """
    Pausa la ejecución del programa hasta que el usuario presione Enter.
    """
    input("Presione Enter para continuar...")
#funciones de formato
def formatear_rut(rut):
    """
    Recibe un RUT chileno en cualquier formato y lo normaliza al formato estándar:
    XX.XXX.XXX-Y

    1. Elimina puntos.
    2. Elimina guion.
    3. Convierte el dígito verificador a mayúscula si corresponde.
    4. Aplica el formato chileno estándar agrupando con puntos y guion.

    Ejemplos:
        formatear_rut('3.136.992-4')    # '3.136.992-4'
        formatear_rut('66666666-6')     # '66.666.666-6'
        formatear_rut('16143583-k')     # '16.143.583-K'
    """
    # Paso 1 y 2: Elimina puntos y guion
    clean = rut.replace('.', '').replace('-', '').strip()

    # Paso 3: Valida que al menos tiene dos caracteres
    if len(clean) < 2:
        return rut  # No es un rut válido, retorna el mismo

    cuerpo, dv = clean[:-1], clean[-1].upper() if clean[-1].isalpha() else clean[-1]
    
    # Paso 4: Formatea el cuerpo
    inv = cuerpo[::-1]
    formateado = ''
    for i, c in enumerate(inv):
        if i > 0 and i % 3 == 0:
            formateado += '.'
        formateado += c
    formateado = formateado[::-1]  # Devuelve el string al orden correcto

    return f"{formateado}-{dv}"

def formatRut(rut):

    #separa el digito verificador
    dv = rut[-1]  # Obtiene el dígito verificador
    dv = dv.upper()

    # Obtiene el número del RUT
    numero = rut[:-1]  
    numero = numero.replace(".", "").replace("-", "")  # Elimina puntos y guiones existentes

    #print(numero+dv)
    if len(numero+dv) == 9:
        a = str(numero+dv)
        rutFormateado = f"{a[0]+a[1]}.{a[2]+a[3]+a[4]}.{a[5]+a[6]+a[7]}-{a[8]}"
        return rutFormateado
    elif len(numero+dv) == 8:
        a = str(numero+dv)
        rutFormateado = f"{a[0]}.{a[1]+a[2]+a[3]}.{a[4]+a[5]+a[6]}-{a[7]}"
        return rutFormateado
    else:
        rutFormateado = ''
        return rutFormateado


#funciones de tratamiento de fecha

def convertir_fecha_iso_a_fecha_hora(fecha_iso):
    """
    Convierte una fecha en formato 'dd-mm-aaaa' a 'aaaa-mm-dd'.

    Args:
    fecha_latin: La fecha en formato de cadena 'dd-mm-aaaa'.

    Returns:
        Una cadena con la fecha en formato 'aaaa-mm-dd', o None si la entrada es inválida.
    """
    try:
        anio, mes, dia = fecha_iso.split('-')
        return f"{anio}-{mes}-{dia} 01:00:00"
    except ValueError:
        print(f"Error: La fecha '{fecha_iso}' no tiene el formato esperado 'dd-mm-aaaa'.")
        return None

def convertir_fecha_a_iso(fecha_latin):
    """
    Convierte una fecha en formato 'dd-mm-aaaa' a 'aaaa-mm-dd'.

    Args:
    fecha_latin: La fecha en formato de cadena 'dd-mm-aaaa'.

    Returns:
        Una cadena con la fecha en formato 'aaaa-mm-dd', o None si la entrada es inválida.
    """
    try:
        anio, mes, dia = fecha_latin.split('-')
        return f"{anio}-{mes}-{dia}"
    except ValueError:
        print(f"Error: La fecha '{fecha_latin}' no tiene el formato esperado 'dd-mm-aaaa'.")
        return None

def convertir_fecha_latin_a_iso(fecha_latin):
    """
    Convierte una fecha en formato 'dd-mm-aaaa' a 'aaaa-mm-dd'.

    Args:
    fecha_latin: La fecha en formato de cadena 'dd-mm-aaaa'.

    Returns:
        Una cadena con la fecha en formato 'aaaa-mm-dd', o None si la entrada es inválida.
    """
    try:
        dia, mes, anio = fecha_latin.split('-')
        return f"{anio}-{mes}-{dia}"
    except ValueError:
        print(f"Error: La fecha '{fecha_latin}' no tiene el formato esperado 'dd-mm-aaaa'.")
        return None

def convertir_datetime_a_fecha_iso(fecha_datetime):
    fecha_iso_solo_fecha = fecha_datetime.date().isoformat()
    return fecha_iso_solo_fecha

def convertir_datetime_a_fecha_iso_hora(fecha_datetime):
    fecha_iso_solo_fecha_hora = fecha_datetime.isoformat()
    return fecha_iso_solo_fecha_hora


def decodificar_xml(xml_encoded):
    """
    Extrae el campo 'Data' en base64, lo decodifica y convierte el XML resultante en un diccionario.

    Parámetros:
        xml_encoded (dict): Diccionario con estructura {'RecoverDocumentResult': {'@xmlns': ..., 'Data': 'PD94bW...==', ...}}

    Retorno:
        dict: Diccionario correspondiente al XML decodificado.
    """
    data_b64 = xml_encoded['RecoverDocumentResult']['Data']
    xml_bytes = base64.b64decode(data_b64)
    try:
        xml_string = xml_bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            xml_string = xml_bytes.decode('latin-1')
        except UnicodeDecodeError:
            xml_string = xml_bytes.decode('iso-8859-1')
    return xmltodict.parse(xml_string)

def extraer_data_base64(texto_json):
    """
    Extrae la cadena Base64 de la clave 'Data' dentro de un texto JSON
    y la decodifica a su forma original (probablemente XML).

    Args:
        texto_json: Una cadena que representa un objeto JSON.

    Returns:
        Una cadena con los datos decodificados, o None si no se encuentra la clave 'Data'
        o si hay un error en la decodificación.
    """
    try:
        data_dict = json.loads(texto_json)
        data_base64 = data_dict.get('RecoverDocumentResult', {}).get('Data')
        if data_base64:
            data_decodificada = base64.b64decode(data_base64).decode('utf-8')
            return data_decodificada
        else:
            print("Advertencia: No se encontró la clave 'Data' en el JSON.")
        return None
    except json.JSONDecodeError:
        print("Error: El texto de entrada no es un JSON válido.")
        return None
    except base64.binascii.Error:
        print("Error: La cadena en 'Data' no es una codificación Base64 válida.")
        return None
    except UnicodeDecodeError:
        print("Advertencia: La data decodificada no parece ser UTF-8. Intenta con otra codificación.")
        # Puedes intentar decodificar con otra codificación si es necesario, por ejemplo:
        # data_decodificada = base64.b64decode(data_base64).decode('iso-8859-1')
        return None

#funciones de base de datos

def connect():
    """
    Función que establece y devuelve una conexión a la base de datos MariaDB.
    (Debes reemplazar los valores de conexión con los tuyos)
    """
    
    
    # Primer intento de conexión con mysql_native_password
    mydb = None
    try:
        mydb = mysql.connector.connect(
            host=host,
            user=user,
            database=db,
            password=passwd,
            auth_plugin='mysql_native_password',
            charset='utf8mb4',      # El charset
           # collation='utf8mb4_0900_ai_ci' # La collation problemas con la collation
        )
        
        if mydb.is_connected():
            #print("Conexión exitosa con auth_plugin.")
            return mydb
        #time.sleep(5)
        
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos con mysql Native Password: {err}")
        
    
        try:
            mydb = mysql.connector.connect(
                host=host,
                user=user,
                database=db,
                password=passwd,
                charset='utf8mb4',      # El charset
                collation='utf8mb4_0900_ai_ci'
            )
            
            if mydb.is_connected():
                print("Conexión exitosa sin auth_plugin.")
                return mydb
        #time.sleep(5)
        
        except mysql.connector.Error as err:
            print(f"Error al conectar a la base de datos: {err}")
            return None
    
def ejecutar_consulta(conexion, query):
    """
    Función que ejecuta una consulta SQL dada en la conexión proporcionada.
    """
    if conexion is None:
        print("No se puede ejecutar la consulta porque no hay conexión a la base de datos.")
        return None

    mycursor = conexion.cursor()
    try:
        mycursor.execute(query)
        # Guardar los cambios
        resultados = mycursor.fetchall()
        return resultados
    except mysql.connector.Error as err:
        print(f"Error al ejecutar la consulta: {err}")
        return None
    finally:
        mycursor.close()

def insertar_resultados(conexion, query):
    """
    Función que inserta los resultados obtenidos de una consulta en la tabla especificada.
    """
    if conexion is None or query is None:
        return
    #print(query)
    mycursor = conexion.cursor()

    
    try:
        mycursor.execute(query)
        conexion.commit()  # Guardar los cambios
        print(colored(f"  {OK_SYMBOL} Registro actualizado correctamente", "green"))

    except mysql.connector.Error as err:
        print(f"Error al insertar datos: {err}")
        conexion.rollback()  # Revertir los cambios en caso de error

    finally:
        mycursor.close()

