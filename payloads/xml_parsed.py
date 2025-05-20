# Ejemplo de acceso a los principales campos de xml_data

# RUTs y Nombres
rut_emisor = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Emisor']['RUTEmisor']
rut_receptor = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Receptor']['RUTRecep']
rut_envia = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Caratula']['RutEnvia']

nombre_emisor = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Emisor']['RznSoc']
nombre_receptor = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Receptor']['RznSocRecep']

# Giros
giro_emisor = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Emisor']['GiroEmis']
giro_receptor = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Receptor']['GiroRecep']

# Dirección y Ciudad
dir_origen = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Emisor']['DirOrigen']
#dir_recep = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Receptor']['DirRecep']
ciudad_origen = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Emisor']['CiudadOrigen']
ciudad_recep = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Receptor']['CiudadRecep']

# Comuna
comuna_origen = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Emisor']['CmnaOrigen']
comuna_recep = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Receptor']['CmnaRecep']

# Otros datos Emisor
sucursal = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Emisor']['Sucursal']
acteco = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Emisor']['Acteco']

# Datos Documento
#tipo_dte = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['IdDoc']['TipoDTE']
#folio = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['IdDoc']['Folio']
fecha_emision = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['IdDoc']['FchEmis']
forma_pago = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['IdDoc']['FmaPago']

# Montos y Totales
mnt_neto = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Totales']['MntNeto']
tasa_iva = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Totales']['TasaIVA']
iva = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Totales']['IVA']
mnt_total = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Totales']['MntTotal']

# TmstFirmaEnv
tmst_firma_env = xml_data[envioTipo]['SetDTE']['Caratula']['TmstFirmaEnv']

# Totales completos (diccionario)
totales = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Encabezado']['Totales']

# Detalle (itinerario de productos o servicios)
detalle = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['Detalle']
# Si detalle es lista, para cada ítem:
for item in detalle:
    nro_lin_det = item['NroLinDet']
    nombre_item = item['NmbItem']
    cantidad_item = item['QtyItem']
    precio_item = item['PrcItem']
    monto_item = item['MontoItem']

# Caratula extra
nro_resol = xml_data[envioTipo]['SetDTE']['Caratula']['NroResol']
fch_resol = xml_data[envioTipo]['SetDTE']['Caratula']['FchResol']

# ID de SetDTE y Documento
id_setdte = xml_data[envioTipo]['SetDTE']['@ID']
id_documento = xml_data[envioTipo]['SetDTE']['DTE']['Documento']['@ID']

# Enlaces Signature, TED, CAF, etc. pueden tener rutas similares.

Nivel raíz
version_envio = data['EnvioDTE']['@version']
xmlns_envio = data['EnvioDTE']['@xmlns']
xmlns_xsi = data['EnvioDTE']['@xmlns:xsi']
xsi_schemaLocation = data['EnvioDTE']['@xsi:schemaLocation']

Datos Carátula
id_setdte = data['EnvioDTE']['SetDTE']['@ID']
version_caratula = data['EnvioDTE']['SetDTE']['Caratula']['@version']
caratula_rut_emisor = data['EnvioDTE']['SetDTE']['Caratula']['RutEmisor']
caratula_rut_envia = data['EnvioDTE']['SetDTE']['Caratula']['RutEnvia']
caratula_rut_receptor = data['EnvioDTE']['SetDTE']['Caratula']['RutReceptor']
caratula_fch_resol = data['EnvioDTE']['SetDTE']['Caratula']['FchResol']
caratula_nro_resol = data['EnvioDTE']['SetDTE']['Caratula']['NroResol']
caratula_tmst_firma_env = data['EnvioDTE']['SetDTE']['Caratula']['TmstFirmaEnv']
caratula_subtotdte_tipo = data['EnvioDTE']['SetDTE']['Caratula']['SubTotDTE']['TpoDTE']
caratula_subtotdte_nro = data['EnvioDTE']['SetDTE']['Caratula']['SubTotDTE']['NroDTE']

Documento principal
doc_id = data['EnvioDTE']['SetDTE']['DTE']['Documento']['@ID']
tipo_dte = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['IdDoc']['TipoDTE']
folio = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['IdDoc']['Folio']
fecha_emision = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['IdDoc']['FchEmis']
forma_pago = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['IdDoc']['FmaPago']

Emisor
rut_emisor = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Emisor']['RUTEmisor']
razon_social_emisor = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Emisor']['RznSoc']
giro_emisor = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Emisor']['GiroEmis']
acteco_emisor = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Emisor']['Acteco']
sucursal_emisor = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Emisor']['Sucursal']
dir_origen_emisor = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Emisor']['DirOrigen']
comuna_origen_emisor = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Emisor']['CmnaOrigen']
ciudad_origen_emisor = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Emisor']['CiudadOrigen']

Receptor
rut_recep = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Receptor']['RUTRecep']
rznsoc_recep = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Receptor']['RznSocRecep']
giro_recep = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Receptor']['GiroRecep']
contacto_recep = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Receptor']['Contacto']
correo_recep = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Receptor']['CorreoRecep']
dir_recep = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Receptor']['DirRecep']
comuna_recep = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Receptor']['CmnaRecep']
ciudad_recep = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Receptor']['CiudadRecep']

Totales
monto_neto = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Totales']['MntNeto']
tasa_iva = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Totales']['TasaIVA']
valor_iva = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Totales']['IVA']
monto_total = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Encabezado']['Totales']['MntTotal']

Detalle - es una lista de productos o servicios
Para cada producto en productos:
for i, producto in enumerate(data['EnvioDTE']['SetDTE']['DTE']['Documento']['Detalle']):
numero_linea = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Detalle'][i]['NroLinDet']
nombre_item = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Detalle'][i]['NmbItem']
cantidad_item = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Detalle'][i]['QtyItem']
precio_item = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Detalle'][i]['PrcItem']
monto_item = data['EnvioDTE']['SetDTE']['DTE']['Documento']['Detalle'][i]['MontoItem']

Personalizados campoString y campoNumero
campos_string = data['EnvioDTE']['Personalizados']['DocPersonalizado']['campoString']
campos_numero = data['EnvioDTE']['Personalizados']['DocPersonalizado']['campoNumero']

Ejemplo para obtener un campo específico por nombre (campoString/numero es lista de dicts con '@name')
Para extraer el valor de "NombrePos" en campoString:
nombre_pos = next(c['#text'] for c in campos_string if c['@name'] == 'NombrePos')
condicionpago = next(c['#text'] for c in campos_string if c['@name'] == 'CondicionPago')

Repite para cualquier otro campo usando el nombre correspondiente

Para "PagoTotal" en campoNumero
pago_total = next(c['#text'] for c in campos_numero if c['@name'] == 'PagoTotal')