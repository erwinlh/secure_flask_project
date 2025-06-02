#ventas.py
import json
import requests

import utils.common as com
import utils.auth as aut
import utils.services as svc
import utils.web as web


### pasos del programa 
"""
1 - Importar las librerías necesarias.
2 - Definir la función principal `main` que ejecutará el flujo del programa.
3 - Definir listado de empresas a procesar.
4 - Iterar sobre cada empresa en el listado.
5 - Obtener el token de autenticación para la empresa actual.
6 - Obtener el listado de ventas para la empresa actual.
7 - Procesar cada venta obtenida.
8 - Para cada venta, crear el payload correspondiente.
9 - Enviar el payload a la base de datos local.
10 - Imprimir el resultado de cada envío.
11 - Manejar errores durante el proceso de envío.
"""


listado_empresas = svc.companies    
    #print(listado_empresas)
"""
    {'SADAS': {'RUT': '76.708.884-1', 'company_id': 20231110191441705533, 'razon_social': 'SADAS SPA'}, 'ADMAR': {'RUT': '77.184.032-9', 'company_id': '76.258.385-2', 'razon_social': 'ADMINISTRADORA ARATA ROJAS SPA.'}, 'ADMA': {'RUT': '76.708.884-1', 'company_id': 20230504131918705533, 'razon_social': 'ADMINISTRADORA ARDAC LTDA'}, 'ComPadu': {'RUT': '65.141.391-5', 'company_id': 20240219134214705533, 'razon_social': 'Comunidad Edificio Paseo Dunas'}, 'ComJaro': {'RUT': '56.070.050-4', 'company_id': 20230703160545705533, 'razon_social': 'Comunidad Edificio Jardín Oriente'}, 'ComAlvz': {'RUT': '53.321.006-6', 'company_id': 20230703162213705533, 'razon_social': 'Comunidad Centro Comercial Alvarez'}, 'INAARC': {'RUT': '76.161.387-1', 'company_id': 20230703161832705533, 'razon_social': 'Inmobiliaria Ina ARC Ltda.'}, 'INA': {'RUT': '78.610.790-3', 'company_id': 20230613132142705533, 'razon_social': 'Inmobiliaria Ardac S.A.'}, 'INAABS': {'RUT': '78.427.970-7', 'company_id': 20230612205856705533, 'razon_social': 'Inmobiliaria e Inversiones ABS Spa'}, 'ARC': {'RUT': '78.427.970-7', 'company_id': 20230612205856705533, 'razon_social': 'Inmobiliaria e Inversiones ABS Spa'}}
"""

for empresa in listado_empresas:
    #headers = svc.build_headers('SADAS')
    #print(headers)
    fecha_inicio = '2025-05-01'
    fecha_fin = '2025-05-31'
    documento_tipo = 'FEAV'
    sales = svc.consultar_venta_por_fechas(empresa, fecha_inicio, fecha_fin)
    #print(sales)
    for sale in sales:
        print(sale)
        ############################# datos de la venta
        """
        {'documentType': 'FEAV', 'firstFolio': 359, 'lastFolio': 0, 'status': 'CENTRALIZADO', 'emissionDate': '2025-05-02T00:00:00', 'dateTime': '2025-05-07T08:34:40.403', 'expirationDate': '2025-05-02T00:00:00', 'clientFile': '77.059.500-2', 'contactIndex': 'SAN DIEGO 1254', 'paymentCondition': 'CONTADO', 'sellerFileId': 'MarinaDunas', 'billingCoin': 'PESO', 'billingRate': 1.0, 'shopId': 'Local', 'priceList': '1', 'giro': 'Venta al por menor de otros productos en comercios especiali', 'city': 'SANTIAGO', 'district': 'Santiago', 'contact': -1, 'attachedDocuments': [], 'details': [{'detailLine': 1, 'type': 'S', 'code': 'MND001', 'count': 1.0, 'price': 126110.0, 'isExempt': None, 'discountType': 'M', 'discountValue': 0.0, 'comment': '', 'analysis': 'VENTAS', 'total': 126110.0, 'priceList': 0.0, 'infAnalysis': {'accountNumber': '', 'businessCenter': '', 'classifier01': '', 'classifier02': ''}}], 'gloss': 'FEAV # 359 Cliente 77.059.500-2 LAX SECURITY SISTEMS LIMITADA - DOCUMENTO IMPORTADO', 'affectableTotal': 126110.0, 'exemptTotal': 0.0, 'taxeCode': 'IVA', 'taxeValue': 23961.0, 'documentTaxes': [{'taxeCode1': 'IVA', 'taxePercentaje1': 19.0, 'taxeValue1': 23961.0, 'taxeCode2': '', 'taxePercentaje2': 0.0, 'taxeValue2': 0.0, 'taxeCode3': '', 'taxePercentaje3': 0.0, 'taxeValue3': 0.0, 'taxeCode4': '', 'taxePercentaje4': 0.0, 'taxeValue4': 0.0, 'taxeCode5': '', 'taxePercentaje5': 0.0, 'taxeValue5': 0.0}], 'ventaRecDesGlobal': None, 'total': 150071.0, 'voucherInfo': [{'folio': 359, 'year': '2025', 'type': 'Vta_FEAV'}], 'inventoryInfo': [], 'customFields': [], 'exportData': [{'exportBillingRate': 0.0, 'exportBillingCoinID': '', 'totalExport': None, 'exemptExport': None, 'destinationCountry': '', 'destinationMerchandise': '', 'landingPort': '', 'saleClause': '', 'saleMode': '', 'shipmentPort': '', 'totalClause': 0.0, 'transportWay': ''}], 'isTransferDocument': 'S', 'timestamp': None, 'dispatchTypeData': {'assetsCode': 'No Posee', 'assetsType': 'No posee', 'dispatchCode': '1', 'dispatchType': 'Por cuenta del cliente'}, 'libVentas': '202505', 'success': False, 'message': None, 'exceptionMessage': None}
        """
        documentType= sale['documentType']
        folio = sale['firstFolio']
        
        status = sale['status']
        emissionDate = sale['emissionDate']
        
        # Información del documento
        sale['documentType']        # 'FEAV'
        sale['firstFolio']         # 359
        sale['lastFolio']          # 0
        sale['status']             # 'CENTRALIZADO'

        # Fechas
        sale['emissionDate']       # '2025-05-02T00:00:00'
        sale['dateTime']           # '2025-05-07T08:34:40.403'
        sale['expirationDate']     # '2025-05-02T00:00:00'

        # Información del cliente
        sale['clientFile']         # '77.059.500-2'
        sale['contactIndex']       # 'SAN DIEGO 1254'
        sale['contact']            # -1

        # Condiciones comerciales
        sale['paymentCondition']   # 'CONTADO'
        sale['sellerFileId']       # 'MarinaDunas'
        sale['billingCoin']        # 'PESO'
        sale['billingRate']        # 1.0
        sale['shopId']             # 'Local'
        sale['priceList']          # '1'

        # Ubicación y giro
        sale['giro']               # 'Venta al por menor de otros productos...'
        sale['city']               # 'SANTIAGO'
        sale['district']           # 'Santiago'

        # Totales principales
        sale['affectableTotal']    # 126110.0
        sale['exemptTotal']        # 0.0
        sale['total']              # 150071.0

        # Impuestos
        sale['taxeCode']           # 'IVA'
        sale['taxeValue']          # 23961.0

        # Otros
        sale['gloss']              # 'FEAV # 359 Cliente...'
        sale['isTransferDocument'] # 'S'
        sale['libVentas']          # '202505'
        sale['timestamp']          # None

        # Estado de respuesta
        sale['success']            # False
        sale['message']            # None
        sale['exceptionMessage']   # None
        
        # Lista vacía en tu ejemplo: []
        # Si tuviera datos:
        for doc in sale['attachedDocuments']:
            doc['date']
            doc['attachedDocumentType']
            doc['attachedDocumentName']
            doc['attachedDocumentNumber']
            doc['attachedDocumentTotal']
            doc['documentTypeId']
            doc['folio']
            doc['reason']
            doc['gloss']
        
        # Acceso al primer (y único) detalle:
        detalle = sale['details'][0]

        detalle['detailLine']      # 1
        detalle['type']            # 'S'
        detalle['code']            # 'MND001'
        detalle['count']           # 1.0
        detalle['price']           # 126110.0
        detalle['isExempt']        # None
        detalle['discountType']    # 'M'
        detalle['discountValue']   # 0.0
        detalle['comment']         # ''
        detalle['analysis']        # 'VENTAS'
        detalle['total']           # 126110.0
        detalle['priceList']       # 0.0

        # Sub-objeto dentro de details
        detalle['infAnalysis']['accountNumber']    # ''
        detalle['infAnalysis']['businessCenter']   # ''
        detalle['infAnalysis']['classifier01']     # ''
        detalle['infAnalysis']['classifier02']     # ''

        # Para iterar todos los detalles:
        for detalle in sale['details']:
            print(f"Producto: {detalle['code']} - Cantidad: {detalle['count']}")
            
        # Acceso al primer (y único) registro de impuestos:
        impuesto = sale['documentTaxes'][0]

        impuesto['taxeCode1']      # 'IVA'
        impuesto['taxePercentaje1'] # 19.0
        impuesto['taxeValue1']     # 23961.0
        impuesto['taxeCode2']      # ''
        impuesto['taxePercentaje2'] # 0.0
        impuesto['taxeValue2']     # 0.0
        # ... hasta taxeCode5, taxePercentaje5, taxeValue5
        
        # Acceso al primer comprobante:
        voucher = sale['voucherInfo'][0]

        voucher['folio']           # 359
        voucher['year']            # '2025'
        voucher['type']            # 'Vta_FEAV'
        
        
        # Lista vacía en tu ejemplo: []
        # Si tuviera datos:
        for inv in sale['inventoryInfo']:
            inv['folio']
            inv['fiscalYear']
            inv['documentType']
        
        
        # Lista vacía en tu ejemplo: []
        # Si tuviera datos:
        for field in sale['customFields']:
            field['classDescription']
            field['classValue']
        
        # Acceso al primer registro de exportación:
        export = sale['exportData'][0]

        export['exportBillingRate']     # 0.0
        export['exportBillingCoinID']   # ''
        export['totalExport']           # None
        export['exemptExport']          # None
        export['destinationCountry']    # ''
        export['destinationMerchandise'] # ''
        export['landingPort']           # ''
        export['saleClause']            # ''
        export['saleMode']              # ''
        export['shipmentPort']          # ''
        export['totalClause']           # 0.0
        export['transportWay']          # ''

        # Acceso al primer registro de exportación:
        export = sale['exportData'][0]

        export['exportBillingRate']     # 0.0
        export['exportBillingCoinID']   # ''
        export['totalExport']           # None
        export['exemptExport']          # None
        export['destinationCountry']    # ''
        export['destinationMerchandise'] # ''
        export['landingPort']           # ''
        export['saleClause']            # ''
        export['saleMode']              # ''
        export['shipmentPort']          # ''
        export['totalClause']           # 0.0
        export['transportWay']          # ''

        dispatch = sale['dispatchTypeData']

        dispatch['assetsCode']     # 'No Posee'
        dispatch['assetsType']     # 'No posee'
        dispatch['dispatchCode']   # '1'
        dispatch['dispatchType']   # 'Por cuenta del cliente'

        # Valor None en tu ejemplo
        # Si tuviera datos sería una lista:
        if sale['ventaRecDesGlobal']:
            for item in sale['ventaRecDesGlobal']:
                item['amount']
                item['modifierClass']
                item['name']
                item['percentage']
                item['value']
                
                # Aquí puedes procesar cada venta           
                
        
        
        break
    
    break
    #print() # print(f"Procesando empresa: {razon_social} - RUT: {rut}")
    
    # 5 - conseguir el TOKEN para la empresa 
    
    

