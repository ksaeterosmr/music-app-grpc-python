import os
import requests
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

testrail_url = os.getenv('TESTRAIL_URL') + 'get_projects'
testrail_user = os.getenv('TESTRAIL_USER')
testrail_password = os.getenv('TESTRAIL_PASSWORD')

response = requests.get(testrail_url, auth=(testrail_user, testrail_password))
if response.status_code == 200:
    print("Autenticación exitosa")
else:
    print(f"Error en la autenticación: {response.status_code}")
    print(response.content)
