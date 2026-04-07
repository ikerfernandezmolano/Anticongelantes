import unittest
import os
import sqlite3
import sys
import time

# Ajustamos el path
sys.path.insert(0, os.getcwd()) 

from app import create_app
from app.config import Config 

TEST_DB = 'test_pimpam_final_clean.db'

class TestChangelog(unittest.TestCase):
    """
    Suite de pruebas para el Changelog.
    Solo prueba la visualización, el buscador y los permisos.
    SIN amigos y SIN notificaciones automáticas.
    """

    def setUp(self):
        """CONFIGURACIÓN INICIAL"""
        self._borrar_bd_segura()
        Config.DB_PATH = TEST_DB
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self._init_test_db()

        # Por defecto, somos el Admin (ID 1)
        from app.controller.model.Sesion import Sesion
        Sesion().usuario.IDUsuario = 1

    def tearDown(self):
        """LIMPIEZA"""
        del self.client
        del self.app
        from app.controller.model.Sesion import Sesion
        Sesion().usuario.IDUsuario = 0
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
        try:
            schema_path = os.path.join(os.getcwd(), 'app', 'database', 'schema.sql')
            with open(schema_path, 'r') as f:
                cursor.executescript(f.read())

            # DATOS SEMILLA BÁSICOS
            cursor.execute("INSERT OR IGNORE INTO Especie (PokedexID, Nombre, Generacion) VALUES (1, 'Bulbasaur', 1)")
            cursor.execute("INSERT OR IGNORE INTO Especie (PokedexID, Nombre, Generacion) VALUES (25, 'Pikachu', 1)")
            
            # Usuario 1 (Admin)
            cursor.execute("INSERT OR IGNORE INTO Usuario (IDUsuario, Nombre, Email, Estado, IDFavorito) VALUES (1, 'Admin', 'admin@test.com', 'Activo', 1)")
            # Usuario 2 (Normal)
            cursor.execute("INSERT OR IGNORE INTO Usuario (IDUsuario, Nombre, Email, Estado, IDFavorito) VALUES (2, 'UsuarioNormal', 'user@test.com', 'Activo', 25)")
            
            # Mensaje inicial manual (para probar que se ven)
            cursor.execute("INSERT OR IGNORE INTO Mensaje (IDUsuario, Texto, Fecha) VALUES (1, 'Mensaje de Bienvenida', '2025-01-01 10:00:00')")
            
            conn.commit()
        finally:
            conn.close()

    # ==========================================================
    # PRUEBAS VISUALES Y DE NAVEGACIÓN
    # ==========================================================

    def test_01_carga_correcta(self):
        """1. Verifica que la página carga correctamente."""
        response = self.client.get('/changelog')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'CHANGELOG', response.data)

    def test_02_visualizar_mensajes(self):
        """2. Verifica que se ven los mensajes de la base de datos."""
        response = self.client.get('/changelog')
        self.assertIn(b'Mensaje de Bienvenida', response.data)

    def test_03_boton_volver(self):
        """3. Verifica que existe el botón para volver."""
        response = self.client.get('/changelog')
        self.assertIn(b'return.png', response.data)

    def test_04_feed_vacio(self):
        """4. Verifica el mensaje cuando borramos todo."""
        with sqlite3.connect(TEST_DB) as conn:
            conn.execute("DELETE FROM Mensaje")
        
        response = self.client.get('/changelog')
        self.assertIn(b'No hay actividad reciente', response.data)

    # ==========================================================
    # PRUEBAS DEL BUSCADOR
    # ==========================================================

    def test_05_buscar_usuario_existente(self):
        """5. Filtra por un usuario que existe (Admin)."""
        response = self.client.post('/changelog', data={'busqueda': 'Admin'})
        self.assertIn(b'Mensaje de Bienvenida', response.data)

    def test_06_buscar_usuario_inexistente(self):
        """6. Filtra por un usuario que NO existe."""
        response = self.client.post('/changelog', data={'busqueda': 'Fantasma'})
        self.assertNotIn(b'Mensaje de Bienvenida', response.data)

    def test_07_boton_todos(self):
        """7. Verifica que se puede resetear el filtro."""
        # Filtramos mal primero
        self.client.post('/changelog', data={'busqueda': 'Fantasma'})
        # Volvemos a cargar (simula botón TODOS)
        response = self.client.get('/changelog') 
        self.assertIn(b'Mensaje de Bienvenida', response.data)

    # ==========================================================
    # PRUEBAS DE PERMISOS (ADMIN vs NORMAL)
    # ==========================================================

    def test_08_boton_admin_visible(self):
        """8. Si soy Admin (ID 1), veo el botón 'Gestionar usuarios'."""
        from app.controller.model.Sesion import Sesion
        Sesion().usuario.IDUsuario = 1
        
        response = self.client.get('/changelog')
        self.assertIn(b'Gestionar usuarios', response.data)

    def test_09_boton_admin_oculto(self):
        """9. Si soy Normal (ID 2), NO veo el botón."""
        from app.controller.model.Sesion import Sesion
        Sesion().usuario.IDUsuario = 2
        
        response = self.client.get('/changelog')
        self.assertNotIn(b'Gestionar usuarios', response.data)

if __name__ == '__main__':
    unittest.main()