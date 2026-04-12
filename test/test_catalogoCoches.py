import unittest
import os
import sqlite3
import sys
import time

sys.path.insert(0, os.getcwd())

from app import create_app
from app.config import Config
from app.controller.model.Sesion import Sesion
from app.controller.model.Usuario import Usuario

TEST_DB = 'test_anticongelantes_coches.db'

class TestCatalogoCoches(unittest.TestCase):

    def setUp(self):
        self._borrar_bd_segura()
        Config.DB_PATH = TEST_DB
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self._init_test_db()
        # Simulamos Admin
        Sesion().usuario = Usuario(1, 'Admin', 'admin@test.com', 'admin', 'Admin')

    def tearDown(self):
        Sesion().usuario = Usuario(0, '', '', '', '', 0)
        self._borrar_bd_segura()

    def _borrar_bd_segura(self):
        if os.path.exists(TEST_DB):
            for _ in range(5):
                try:
                    os.remove(TEST_DB)
                    break
                except PermissionError:
                    time.sleep(0.5)
                except Exception:
                    pass

    def _init_test_db(self):
        conn = sqlite3.connect(TEST_DB)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS Coche")
        cursor.execute("""
            CREATE TABLE Coche (
                idCoche INTEGER PRIMARY KEY AUTOINCREMENT,
                marca TEXT NOT NULL, modelo TEXT NOT NULL,
                precio REAL NOT NULL, kilometraje INTEGER,
                imagen TEXT DEFAULT 'fondo.jpg'
            )
        """)
        # Insertamos los datos para los tests
        cursor.execute("INSERT INTO Coche (marca, modelo, precio, kilometraje, imagen) VALUES ('Ferrari', '458 Italia', 215000, 12000, 'ferrari.png')")
        cursor.execute("INSERT INTO Coche (marca, modelo, precio, kilometraje, imagen) VALUES ('Audi', 'R8 Performance', 165000, 15000, 'fondo.jpg')")
        conn.commit()
        conn.close()

    def test_01_acceso_catalogo(self):
        """Verifica que la página carga buscando una palabra sin tildes del título"""
        response = self.client.get('/catalogo')
        self.assertEqual(response.status_code, 200)
        # Buscamos 'ANTICONGELANTES' que no tiene problemas de tildes
        self.assertIn(b'ANTICONGELANTES', response.data.upper())

    def test_02_visualizacion_coches(self):
        """Verifica que el precio realista aparece con el punto de miles"""
        response = self.client.get('/catalogo')
        self.assertIn(b'Ferrari', response.data)
        self.assertIn(b'215.000', response.data)

    def test_04_navegacion_a_detalles(self):
        """Verifica el acceso a detalles del primer coche. Buscamos 'Ferrari' que es lo que sale en el h1"""
        response = self.client.get('/detalles/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Ferrari', response.data)

    def test_05_modal_y_contacto(self):
        """Verifica la pestañita de contacto y el teléfono realista"""
        response = self.client.get('/detalles/1')
        self.assertIn(b'modalContacto', response.data)
        self.assertIn(b'+34 622 45 81 90', response.data)

    def test_07_eliminar_coche_admin(self):
        """Verifica que al eliminar un coche ya no sale en el catálogo"""
        # Eliminamos el Audi (ID 2)
        self.client.get('/delete_car/2', follow_redirects=True)
        # Comprobamos la lista
        response = self.client.get('/catalogo')
        self.assertNotIn(b'Audi', response.data)

if __name__ == '__main__':
    unittest.main()