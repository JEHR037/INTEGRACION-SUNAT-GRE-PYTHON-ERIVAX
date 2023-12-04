import requests
import threading
from datetime import timedelta

class AccesoAPI:
    def __init__(self):
        self.client_id = 'TUINFO'
        self.client_secret = 'TUINFO'
        self.ruc = 'TUINFO'
        self.username_sol = 'TUINFO'
        self.password_sol = 'TUINFO'
        self.auth_url = f'https://api-seguridad.sunat.gob.pe/v1/clientessol/{self.client_id}/oauth2/token/'
        self.access_token = None
        self.token_type = None
        self.expires_in = 3600 
        self.lock = threading.Lock()
        self.actualizar_token()

    def obtener_token(self):
        auth_data = {
            'grant_type': 'password',
            'scope': 'https://api-cpe.sunat.gob.pe',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'username': f'{self.ruc}{self.username_sol}',
            'password': self.password_sol
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(self.auth_url, data=auth_data, headers=headers)
        if response.status_code == 200:
            self.access_token = response.json().get('access_token')
            self.token_type = response.json().get('token_type')
            self.expires_in = response.json().get('expires_in')
            print("Token -->", self.access_token, "Tipo de Token -->", self.token_type, "Expiracion -->", self.expires_in)
        else:
            print("Error al obtener el token:", response.text)

    def actualizar_token(self):
        with self.lock:
            self.obtener_token()
            threading.Timer(self.expires_in - 600, self.actualizar_token).start()

acceso_api = AccesoAPI()
