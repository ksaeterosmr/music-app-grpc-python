import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests
import json
import os
from dotenv import load_dotenv

class TestAddMusic(unittest.TestCase):

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

        username_field = cls.driver.find_element(By.ID, 'username')
        password_field = cls.driver.find_element(By.ID, 'password')
        login_button = cls.driver.find_element(By.XPATH, "//button[@type='submit']")

        username_field.send_keys('ksaeteros')
        password_field.send_keys('123')
        login_button.click()

        WebDriverWait(cls.driver, 10).until(EC.url_to_be('http://localhost:5000/index'))

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    @classmethod
    def create_test_run(cls):
        url = f'{cls.testrail_url}add_run/{cls.project_id}'
        data = {
            "suite_id": cls.plan_id,
            "name": "Test Run - Search Music Functionality",
            "description": "Ejecución de prueba automatizada para agregar funcionalidad de música",
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

    def test_song_found(self):
        case_id = 14  # Actualiza con el ID del caso de prueba en TestRail
        try:
            self.driver.get('http://localhost:5000/search')

            search_box = self.driver.find_element(By.NAME, 'song_name')
            search_box.send_keys('Shape of You')
            search_box.send_keys(Keys.RETURN)

            # Esperamos a que el mensaje de éxito sea visible
            success_message = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'alert-success'))
            )
            self.assertIn('Canción encontrada.', success_message.text)
            self.send_result_to_testrail(case_id, 1, 'Prueba exitosa')

        except TimeoutException:
            # En caso de que falle, imprimimos el HTML de la página actual para ayudar a depurar
            print(self.driver.page_source)
            self.send_result_to_testrail(case_id, 5, 'El mensaje de éxito no apareció a tiempo')
            self.fail("El mensaje de éxito no apareció a tiempo")

        except Exception as e:
            # Registrar cualquier otra excepción
            self.send_result_to_testrail(case_id, 5, str(e))
            raise

    def test_song_not_found(self):
        case_id = 15  # Actualiza con el ID del caso de prueba en TestRail
        try:
            self.driver.get('http://localhost:5000/search')

            search_box = self.driver.find_element(By.NAME, 'song_name')
            search_box.send_keys('##48es')
            search_box.send_keys(Keys.RETURN)

            # Esperamos a que el mensaje de error sea visible
            error_message = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'alert-error'))
            )
            self.assertIn('No se encontró la canción.', error_message.text)
            self.send_result_to_testrail(case_id, 1, 'Prueba exitosa')

        except TimeoutException:
            # En caso de que falle, imprimimos el HTML de la página actual para ayudar a depurar
            print(self.driver.page_source)
            self.send_result_to_testrail(case_id, 5, 'El mensaje de error no apareció a tiempo')
            self.fail("El mensaje de error no apareció a tiempo")

        except Exception as e:
            # Registrar cualquier otra excepción
            self.send_result_to_testrail(case_id, 5, str(e))
            raise

if __name__ == '__main__':
    unittest.main()
