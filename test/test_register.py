import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests
import json
import os
from dotenv import load_dotenv

class TestRegister(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Cargar variables de entorno desde el archivo .env
        load_dotenv()
        cls.driver = webdriver.Chrome()
        cls.driver.get('http://localhost:5000/register')

        cls.testrail_url = os.getenv('TESTRAIL_URL')
        cls.testrail_user = os.getenv('TESTRAIL_USER')
        cls.testrail_password = os.getenv('TESTRAIL_PASSWORD')
        cls.project_id = int(os.getenv('TESTRAIL_PROJECT_ID'))
        cls.plan_id = int(os.getenv('TESTRAIL_PLAN_ID'))

        # Crear una ejecución de pruebas dentro del plan de pruebas
        cls.run_id = cls.create_test_run()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    @classmethod
    def create_test_run(cls):
        url = f'{cls.testrail_url}add_run/{cls.project_id}'
        data = {
            "suite_id": cls.plan_id,
            "name": "Test Run - Funcionalidad de registro",
            "description": "Ejecución de pruebas automatizadas para la funcionalidad de registro",
            "include_all": True
        }
        response = requests.post(url, auth=(cls.testrail_user, cls.testrail_password), headers={'Content-Type': 'application/json'}, data=json.dumps(data))
        if response.status_code != 200:
            print(f'Error al crear la ejecución de pruebas: {response.status_code}')
            print(response.content)
            return None
        else:
            run_id = response.json()['id']
            print(f'Ejecución de pruebas creada con ID: {run_id}')
            return run_id

    def send_result_to_testrail(self, case_id, status_id, comment):
        if not self.run_id:
            print('No hay un run_id válido disponible. Omitiendo actualización de TestRail.')
            return

        url = f'{self.testrail_url}add_result_for_case/{self.run_id}/{case_id}'
        data = {
            "status_id": status_id,
            "comment": comment
        }
        response = requests.post(url, auth=(self.testrail_user, self.testrail_password), headers={'Content-Type': 'application/json'}, data=json.dumps(data))
        if response.status_code != 200:
            print(f'Error: {response.status_code}')
            print(response.content)
        else:
            print(f'Resultado enviado para el caso {case_id}')

    def test_successful_registration(self):
        case_id = 13  # Actualiza con el ID del caso de prueba en TestRail
        try:
            self.driver.get('http://localhost:5000/register')

            username = self.driver.find_element(By.ID, 'username')
            email = self.driver.find_element(By.ID, 'email')
            password = self.driver.find_element(By.ID, 'password')
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")

            username.send_keys('new_user6')  # Cambia 'new_user' por un nuevo usuario
            email.send_keys('new_user6@example.com')  # Cambia 'new_user@example.com' por un nuevo correo
            password.send_keys('password')
            submit_button.click()

            # Esperar al mensaje de registro exitoso en la página de login
            success_message = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'alert-danger'))
            )
            self.assertIn('Registro exitoso, por favor inicia sesión.', success_message.text)

            # Ingresar datos para iniciar sesión
            username = self.driver.find_element(By.ID, 'username')
            password = self.driver.find_element(By.ID, 'password')
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")

            username.send_keys('new_user6')
            password.send_keys('password')
            login_button.click()

            # Verificar que la redirección fue exitosa al index
            WebDriverWait(self.driver, 10).until(EC.url_to_be('http://localhost:5000/index'))
            self.assertEqual(self.driver.current_url, 'http://localhost:5000/index')
            self.send_result_to_testrail(case_id, 1, 'Prueba exitosa')

        except TimeoutException as e:
            print(f"TimeoutException: {str(e)}")
            print("HTML de la página actual para ayudar a depurar:")
            print(self.driver.page_source)
            self.send_result_to_testrail(case_id, 5, 'La redirección después del registro falló')
            self.fail("La redirección después del registro falló")
    def test_username_already_exists(self):
        case_id = 11  # Actualiza con el ID del caso de prueba en TestRail
        try:
            self.driver.get('http://localhost:5000/register')

            username = self.driver.find_element(By.ID, 'username')
            email = self.driver.find_element(By.ID, 'email')
            password = self.driver.find_element(By.ID, 'password')
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")

            username.send_keys('ksaeteros')  # Cambia 'existing_username' por un usuario existente
            email.send_keys('new_email@example.com')
            password.send_keys('password')
            submit_button.click()

            error_message = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'alert-danger'))
            )
            self.assertIn('Ya existe un usuario con ese nombre.', error_message.text)
            self.send_result_to_testrail(case_id, 1, 'Prueba exitosa')

        except TimeoutException as e:
            print(f"TimeoutException: {str(e)}")
            print("HTML de la página actual para ayudar a depurar:")
            print(self.driver.page_source)
            self.send_result_to_testrail(case_id, 5, 'El mensaje de error no apareció a tiempo')
            self.fail("El mensaje de error no apareció a tiempo")

    def test_email_already_exists(self):
        case_id = 12  # Actualiza con el ID del caso de prueba en TestRail
        try:
            self.driver.get('http://localhost:5000/register')

            username = self.driver.find_element(By.ID, 'username')
            email = self.driver.find_element(By.ID, 'email')
            password = self.driver.find_element(By.ID, 'password')
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")

            username.send_keys('new_username')
            email.send_keys('user2@gmail.com')  # Cambia 'existing_email@example.com' por un correo existente
            password.send_keys('password')
            submit_button.click()

            error_message = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'alert-danger'))
            )
            self.assertIn('Ya existe un usuario con ese email.', error_message.text)
            self.send_result_to_testrail(case_id, 1, 'Prueba exitosa')

        except TimeoutException as e:
            print(f"TimeoutException: {str(e)}")
            print("HTML de la página actual para ayudar a depurar:")
            print(self.driver.page_source)
            self.send_result_to_testrail(case_id, 5, 'El mensaje de error no apareció a tiempo')
            self.fail("El mensaje de error no apareció a tiempo")


if __name__ == '__main__':
    unittest.main()
