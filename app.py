from flask import Flask, render_template, request, redirect, url_for, session, flash, redirect, url_for
import requests
import lxml.etree as et
import xml.etree.ElementTree as ET
from datetime import timedelta
import os
import base64
import hashlib
import zipfile
from acceso import acceso_api
import json

app = Flask(__name__ , static_url_path='/static', static_folder="static")
app.secret_key = '*@1@2@3*' ###CAMBIAR A GUSTO####
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

@app.route('/logout')
def logout():
    session.pop('user', None) 
    return redirect(url_for('login')) 
@app.before_request
def check_session():
    rutas_publicas = ['login']
    if request.endpoint in rutas_publicas:
        return
    if 'static' in request.path:
        return 
    if not is_authenticated():
        return redirect(url_for('login'))
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

def crear_zip(xml_filename, xml_content):
    zip_filename = xml_filename.replace('.xml', '.zip')
    zip_path = os.path.join('./', zip_filename)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(xml_filename, xml_content)
    return zip_path

def codificar_base64(zip_path):
    with open(zip_path, 'rb') as file:
        encoded_zip = base64.b64encode(file.read()).decode('utf-8')
    return encoded_zip

def calcular_hash(zip_path):
    with open(zip_path, 'rb') as file:
        hash_zip = hashlib.sha256(file.read()).hexdigest()
    return hash_zip
def get_next_num_cpe():
    try:
        with open('contador.txt', 'r') as file:
            current_value = file.read().strip()
            if not current_value:  
                current_value = '00000001'
    except FileNotFoundError:
        current_value = '00000001'
    return current_value
def incrementar_num_cpe():
    current_value = get_next_num_cpe()
    next_value = str(int(current_value) + 1).zfill(8)
    with open('contador.txt', 'w') as file:
        file.write(next_value)


def is_authenticated():
    return 'user' in session

@app.before_request
def check_session():
    if is_authenticated():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=3)



def replace_values_in_xml(original_xml_path, replacements, output_xml_filename):
    tree = ET.parse(original_xml_path)
    root = tree.getroot()

    namespaces = {
        "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2": "cac",
        "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2": "cbc",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",

    }
    for uri, prefix in namespaces.items():
        ET.register_namespace(prefix, uri)
        

    paths = {
        "NUMERO_GUIA": "./cbc:ID",
        "FACTURA_ENLAZADA": ".//cac:AdditionalDocumentReference/cbc:ID",
        "DOCUMENTO_IDENTIFICACION": ".//cac:DeliveryCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID",
        "ID_EMISOR": "./cac:DespatchSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID",
        "NOMBRE_CLIENTE": ".//cac:DeliveryCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName",
        "PESO_KILOS": ".//cac:Shipment/cbc:GrossWeightMeasure",
        "FECHA_PARTIDA": ".//cac:Shipment/cac:ShipmentStage/cac:TransitPeriod/cbc:StartDate",
        "DIRECCION": ".//cac:Shipment/cac:Delivery/cac:DeliveryAddress/cac:AddressLine/cbc:Line",
        "PLACA_VEHICULO": ".//cac:Shipment/cac:TransportHandlingUnit/cac:TransportEquipment/cbc:ID",
        "DESCRIPCION_CARGA": ".//cac:DespatchLine/cac:Item/cbc:Description",
        "FECHA_EMISION": "./cbc:IssueDate",
        "ID_ISSUER_PARTY": ".//cac:AdditionalDocumentReference/cac:IssuerParty/cac:PartyIdentification/cbc:ID",
        "ADDRESS_TYPE_CODE_LIST_ID": "./cac:Shipment/cac:Delivery/cac:DeliveryAddress/cbc:AddressTypeCode/@listID",
        "DNI_chofer": "./cac:Shipment/cac:ShipmentStage/cac:DriverPerson/cbc:ID",
        "licencia": "./cac:Shipment/cac:ShipmentStage/cac:DriverPerson/cac:IdentityDocumentReference/cbc:ID",
        "codigo_sunat": "./cac:DespatchLine/cac:Item/cac:CommodityClassification/cbc:ItemClassificationCode"
    }
  
    for key, path in paths.items():
        if key in replacements:
            if '@' in path: 
                element, attribute = path.rsplit('/', 1)
                target_element = root.find(element, namespaces=namespaces)
                if target_element is not None:
                    target_element.set(attribute[1:], replacements[key]) 
            else: 
                target_element = root.find(path, namespaces=namespaces)
                if target_element is not None:
                    target_element.text = replacements[key]

    tree.write(output_xml_filename, encoding='utf-8', xml_declaration=True)

def actualizar_bitacora(xml_filename, ticket):
    bitacora_path = 'bitacora.json'
    registros = []

    try:
        with open(bitacora_path, 'r') as bitacora_file:
            registros = json.load(bitacora_file)
    except FileNotFoundError:
        print("El archivo de bitácora no existe, se creará uno nuevo.")
    except json.JSONDecodeError:
        print("Error al leer el archivo de bitácora, se iniciará uno nuevo.")

    registro = {"xml_filename": xml_filename, "ticket": ticket}
    registros.append(registro)

    with open(bitacora_path, 'w') as bitacora_file:
        json.dump(registros, bitacora_file, indent=4)


@app.route('/enviar', methods=['GET', 'POST'])
def enviar():
    if 'xml_file' in request.files:
        xml_file = request.files['xml_file']
        xml_filename = xml_file.filename
        xml_content = xml_file.read()
        zip_path = crear_zip(xml_filename, xml_content)
        arc_gre_zip = codificar_base64(zip_path)
        hash_zip = calcular_hash(zip_path)

        nom_archivo_zip = os.path.basename(zip_path).replace('.zip', '')
        response = enviar_a_sunat_api(nom_archivo_zip, arc_gre_zip, hash_zip)
        print(response.text)
        if response.status_code == 200:
            ticket = response.json()['numTicket']
            actualizar_bitacora(xml_filename, ticket)
            headers = {'Authorization': 'Bearer ' + acceso_api.access_token}
            cdr_response = requests.get(f'https://api-cpe.sunat.gob.pe/v1/contribuyente/gem/comprobantes/envios/{ticket}', headers=headers)
            if cdr_response.status_code == 200:
                cdr_data = cdr_response.json()
                print("DATA DEL CDR ==>",cdr_response.text)
                print("TIKET --->",ticket)
                if 'arcCdr' in cdr_data:
                    cdr_base64 = cdr_data['arcCdr']
                    cdr_content = base64.b64decode(cdr_base64)
                    agregar_cdr_a_zip(zip_path, cdr_content, nom_archivo_zip)

                    flash('Envío exitoso. Ticket: ' + ticket, 'success')
                    return render_template('enviar.html', cdr_zip_path=zip_path)
                else:
                    flash('Error al obtener el CDR: "arcCdr" no encontrado en la respuesta', 'error')
            else:
                flash('Error al obtener el CDR de SUNAT', 'error')
        else:
            flash('Error al enviar a SUNAT', 'error')

        return redirect(url_for('enviar'))

    xml_files = [f for f in os.listdir('./') if f.endswith('.xml') and f != 'original.xml']
    return render_template('enviar.html', xml_files=xml_files)

def agregar_cdr_a_zip(zip_path, cdr_content, nom_archivo_zip):
    with zipfile.ZipFile(zip_path, 'a') as zipf:
        cdr_filename = f"cdr_{nom_archivo_zip}.xml"
        zipf.writestr(cdr_filename, cdr_content)

    return zip_path

def enviar_a_sunat_api(nom_archivo_sin_extension, arc_gre_zip, hash_zip):
    ruc_emisor, cod_cpe, num_serie, num_cpe = nom_archivo_sin_extension.split('-')
    url = f'https://api-cpe.sunat.gob.pe/v1/contribuyente/gem/comprobantes/{ruc_emisor}-{cod_cpe}-{num_serie}-{num_cpe}'
    
    headers = {'Authorization': 'Bearer ' + acceso_api.access_token}
    body = {
        'archivo': {
            'nomArchivo': nom_archivo_sin_extension + '.zip', 
            'arcGreZip': arc_gre_zip,
            'hashZip': hash_zip
        }
    }
  
    response = requests.post(url, json=body, headers=headers)
    if response.status_code == 200:
            flash('Envío exitoso. Ticket: ' + response.json()['numTicket'], 'success')
    print("RESPUESTA DE SUNAT -->",response.text)
    return response

@app.route('/Generar', methods=['GET', 'POST'])

def generar_xml():
    next_num_cpe = get_next_num_cpe() 
    if request.method == 'POST':
        documento_identificacion = request.form['documento_identificacion']
        replacements = {
            "NUMERO_GUIA": request.form.get('numero_guia', next_num_cpe),
            "FACTURA_ENLAZADA": request.form['factura_enlazada'],
            "DOCUMENTO_IDENTIFICACION": documento_identificacion ,
            "NOMBRE_CLIENTE": request.form['nombre_cliente'],
            "PESO_KILOS": request.form['peso_kilos'],
            "FECHA_PARTIDA": request.form['fecha_partida'],
            "DIRECCION": request.form['direccion'],
            "PLACA_VEHICULO": request.form['placa_vehiculo'],
            "DESCRIPCION_CARGA": request.form['descripcion_carga'],
            "FECHA_EMISION": request.form.get('fecha_emision'),
            "ID_EMISOR": "20605782231",
            "ID_ISSUER_PARTY": "20605782231",
            "ADDRESS_TYPE_CODE_LIST_ID": documento_identificacion,
            "DNI_chofer": request.form.get("DNI_chofer"),
            "codigo_sunat":request.form.get("codigo_sunat"),
            "licencia":request.form.get("licencia")
        }

        ruc_emisor = '20605782231' 
        cod_cpe = '09' 
        num_serie = 'T001' 
        output_xml_filename = f'{ruc_emisor}-{cod_cpe}-{num_serie}-{next_num_cpe}.xml'

        try:
            replace_values_in_xml('./original.xml', replacements, output_xml_filename)
            flash('XML generado con éxito: ' + output_xml_filename, 'success')
            incrementar_num_cpe()
            return redirect(url_for('generar_xml'))
        except Exception as e:
            flash(f'Error al generar XML: {str(e)}', 'error')

    return render_template('generar.html', next_num_cpe=next_num_cpe)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "Audiotek" and password == "0@1@2":###CAMBIAR A GUSTO####
            session['user'] = username
            flash('Inicio de sesión exitoso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas. Inténtalo de nuevo.', 'danger')

    return render_template("login.html")

@app.route("/dashboard", methods=['GET'])
def dashboard():

    return render_template("dashboard.html")

@app.route("/estado", methods=['GET'])
def estado():
    pagina = request.args.get('pagina', 1, type=int)
    registros_por_pagina = 20
    todos_los_registros = obtener_registros() 
    total_registros = len(todos_los_registros)

    total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina

    inicio = (pagina - 1) * registros_por_pagina
    final = inicio + registros_por_pagina
    registros = todos_los_registros[inicio:final]

    return render_template("estado.html", registros=registros, total_pages=total_paginas)
def obtener_registros():
    try:
        with open('bitacora.json', 'r') as file:
            registros = json.load(file)
    except FileNotFoundError:
        print("Archivo de bitácora no encontrado.")
        registros = []

    return registros


@app.route('/solicitar_estado/<ticket>')
def solicitar_estado(ticket):
    headers = {'Authorization': 'Bearer ' + acceso_api.access_token}
    url = f'https://api-cpe.sunat.gob.pe/v1/contribuyente/gem/comprobantes/envios/{ticket}'
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'No se pudo obtener el estado'}, 500



if __name__ == '__main__':
    app.run()
