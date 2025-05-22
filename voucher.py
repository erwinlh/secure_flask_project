import utils.auth as aut
import utils.common as com
import utils.services as svc
import json
import os
import time


from datetime import datetime, timedelta



#svc.importar_arqueo_opera(r"C:\OneDrive\OneDrive - Marina Hoteles\Downloads\03-CashierAu_v4 Rng RP_03-CashierAu_v3 A (3).xlsx")



# Obtener la fecha de inicio desde el usuario
#fecha_str = input("Ingresa la fecha de inicio (YYYY-MM-DD): ")
fecha_str = "2025-03-01"

# Convertir la entrada de texto a un objeto datetime usando el formato YYYY-MM-DD
fecha = datetime.strptime(fecha_str, "%Y-%m-%d")

# Ejemplo: ciclo for para aumentar la fecha por 10 días
for i in range(1):
    # Mostrar la fecha actual en formato YYYY-MM-DD
    
    try:
        #payload_voucher = svc.crear_payload_voucher_lines(fecha)
        svc.procesar_voucher_dia(fecha.strftime('%Y-%m-%d'))
        
        print(f"Voucher procesado Correctamentepara la fecha: {fecha.strftime('%Y-%m-%d')}")
        #update_query = f"insert into vouchers_enviados (fecha, glosa, numero_voucher, tipo_voucher, anio_fiscal, fecha_envio, json_payload) values (%s, %s, %s, %s, %s, %s, %s)"
        #resp = 'aqui va el response de enviar el foucher'
        #values utiliza valores de resp
        #values = (fecha.strftime('%Y-%m-%d'), "Voucher de prueba", "123456", "TRASPASO", 2025, fecha.strftime('%Y-%m-%d'), json.dumps({"key": "value"}))
        input("presione una tecla para continuar")
    except Exception as e:
        print(f"Error al procesar el voucher para la fecha {fecha.strftime('%Y-%m-%d')}: {e}")
        # Aquí puedes agregar lógica adicional para manejar el error si es necesario    
    # Incrementar la fecha en 1 día
    fecha = fecha + timedelta(days=1)
    time.sleep(1)