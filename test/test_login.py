import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json
import os
from dotenv import load_dotenv

class TestLogin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Cargar las variables de entorno desde el archivo .env
        load_dotenv()
        cls.driver = webdriver.Chrome()
        cls.driver.get('http://localhost:5000/login')
        cls.testrail_url = os.getenv('TESTRAIL_URL')
        cls.testrail_user = os.getenv('TESTRAIL_USER')
        cls.testrail_password = os.getenv('TESTRAIL_PASSWORD')
        cls.project_id = int(os.getenv('TESTRAIL_PROJECT_ID'))
        cls.plan_id = int(os.getenv('TESTRAIL_PLAN_ID'))
        
        # Crear un test run dentro del test plan
        cls.run_id = cls.create_test_run()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    @classmethod
    def create_test_run(cls):
        url = f'{cls.testrail_url}add_run/{cls.project_id}'
        data = {
            "suite_id": cls.plan_id,
            "name": "Test Run: funcionalidad de inicio de sesión",
            "description": "Ejecución de prueba automatizada para la funcionalidad de inicio de sesión",
            "include_all": True
        }
        response = requests.post(url, auth=(cls.testrail_user, cls.testrail_password), headers={'Content-Type': 'application/json'}, data=json.dumps(data))
        if response.status_code != 200:
            print(f'Error creating test run: {response.status_code}')
            print(response.content)
            return None
        else:
            run_id = response.json()['id']
            print(f'Created test run with ID: {run_id}')
            return run_id

    def send_result_to_testrail(self, case_id, status_id, comment):
        if not self.run_id:
            print('No valid run_id available. Skipping TestRail update.')
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

    def test_login_valid_credentials(self):
        try:
            username = self.driver.find_element(By.ID, 'username')
            password = self.driver.find_element(By.ID, 'password')
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")

            username.send_keys('ksaeteros')
            password.send_keys('123')
            submit_button.click()

            WebDriverWait(self.driver, 10).until(EC.url_to_be('http://localhost:5000/index'))
            self.assertEqual(self.driver.current_url, 'http://localhost:5000/index')
            
            # Registrar resultado en TestRail
            self.send_result_to_testrail(case_id=5, status_id=1, comment='Prueba exitosa')
        
        except Exception as e:
            # Registrar resultado en TestRail
            self.send_result_to_testrail(case_id=5, status_id=5, comment=str(e))
            raise

    def test_login_invalid_credentials(self):
        try:
            username = self.driver.find_element(By.ID, 'username')
            password = self.driver.find_element(By.ID, 'password')
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")

            username.send_keys('usuario_incorrecto')
            password.send_keys('contraseña_incorrecta')
            submit_button.click()

            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'alert-danger'))
            )

            error_message = self.driver.find_element(By.CLASS_NAME, 'alert-danger').text
            self.assertIn('Usuario o contraseña incorrecta', error_message)
            
            # Registrar resultado en TestRail
            self.send_result_to_testrail(case_id=6, status_id=1, comment='Prueba exitosa')
        
        except Exception as e:
            # Registrar resultado en TestRail
            self.send_result_to_testrail(case_id=6, status_id=5, comment=str(e))
            raise

if __name__ == "__main__":
    unittest.main()
