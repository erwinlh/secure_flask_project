import utils.auth as aut
import utils.common as com
import utils.services as svc
import json
import os
import time


from datetime import datetime, timedelta

# Obtener la fecha de inicio desde el usuario
#fecha_str = input("Ingresa la fecha de inicio (YYYY-MM-DD): ")
fecha_str = "2025-03-01"

# Convertir la entrada de texto a un objeto datetime usando el formato YYYY-MM-DD
fecha = datetime.strptime(fecha_str, "%Y-%m-%d")

# Ejemplo: ciclo for para aumentar la fecha por 10 días
for i in range(1):
    # Mostrar la fecha actual en formato YYYY-MM-DD
    
    try:
        svc.procesar_voucher_dia(fecha.strftime('%Y-%m-%d'))
        print(f"Voucher procesado Correctamentepara la fecha: {fecha.strftime('%Y-%m-%d')}")
        input("presione una tecla para continuar")
    except Exception as e:
        print(f"Error al procesar el voucher para la fecha {fecha.strftime('%Y-%m-%d')}: {e}")
        # Aquí puedes agregar lógica adicional para manejar el error si es necesario    
    # Incrementar la fecha en 1 día
    fecha = fecha + timedelta(days=1)
    time.sleep(1)