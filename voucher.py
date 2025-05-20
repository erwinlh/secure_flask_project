import utils.auth as aut
import utils.common as com
import utils.services as svc
import json
import os


try:
    
    conexion = com.connect()
    print("conexion exitosa")
    
    # procesar Arqueo, lee archivo de excel que contiene los arqueos de caja y los almacena 
    # en nuestra base de datos de mysql
    
    
    
    payload_voucher = svc.crear_payload_voucher_lines('2025-05-18')
    payload_voucher_json = json.dumps(payload_voucher, indent=4)

    

    
    voucher = svc.subir_voucher_defontana(payload_voucher_json)
    
    
    
except Exception as e:
    print(f"error de conexion: {e}")
    
    
