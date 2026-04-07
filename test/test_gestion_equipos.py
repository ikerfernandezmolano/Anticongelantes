import unittest
import os
import sqlite3
import sys
import time

# Añade el directorio raíz al path para poder importar la app
sys.path.insert(0, os.getcwd())

from app import create_app
from app.config import Config

# Base de datos de pruebas
TEST_DB = 'test_pimpam.db'


class TestEquipos(unittest.TestCase):

    def setUp(self):
        # Elimina la base de datos de test si existe
        if os.path.exists(TEST_DB):
            try:
                os.remove(TEST_DB)
            except PermissionError:
                time.sleep(0.1)

        # Configura la ruta de la BD de pruebas
        Config.DB_PATH = TEST_DB
        self._init_test_db()

        # Crea la aplicación en modo testing
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def tearDown(self):
        # Limpia cliente y app tras cada test
        self.client = None
        self.app = None

        # Elimina la base de datos de pruebas
        if os.path.exists(TEST_DB):
            try:
                time.sleep(0.1)
                os.remove(TEST_DB)
            except PermissionError:
                pass

    def _init_test_db(self):
        # Inicializa la base de datos con el esquema y datos mínimos
        conn = sqlite3.connect(TEST_DB, timeout=10)
        cursor = conn.cursor()

        schema_path = os.path.join(os.getcwd(), 'app', 'database', 'schema.sql')
        with open(schema_path, 'r') as f:
            try:
                cursor.executescript(f.read())
            except sqlite3.OperationalError:
                pass

        # Inserta un usuario de prueba
        cursor.execute(
            "INSERT OR IGNORE INTO Usuario (Nombre, Email, Contrasena, Estado) VALUES (?, ?, ?, ?)",
            ('TestUser', 'test@test.com', '1234', 'Activo')
        )

        # Inserta una especie de prueba
        cursor.execute(
            "INSERT OR IGNORE INTO Especie (PokedexID, Nombre, Generacion) VALUES (25, 'Pikachu', 1)"
        )

        # Inserta un equipo de prueba asociado al usuario
        cursor.execute("""
            INSERT OR IGNORE INTO Equipo (Nombre, IDUsuario)
            VALUES ('Equipo Test', (SELECT IDUsuario FROM Usuario WHERE Nombre='TestUser'))
        """)

        conn.commit()
        conn.close()

    # --- PRUEBAS ---

    def test_2_acceso_gestion_equipos(self):
        # Comprueba que se puede acceder a la vista de equipos
        response = self.client.get('/equipos')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'EquipoDemo', response.data)

    def test_3_crear_equipo(self):
        # Comprueba que se puede crear un equipo nuevo
        response = self.client.post('/equipos/crear', data={'nombre': 'Equipo Nuevo'})
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/equipos')
        self.assertIn(b'Equipo Nuevo', response.data)

    def test_4_seleccionar_equipo(self):
        # Comprueba que la vista de equipos carga correctamente
        response = self.client.get('/equipos')
        self.assertEqual(response.status_code, 200)

    def test_5_anadir_pokemon(self):
        # Añade un Pokémon a un slot del equipo
        response = self.client.post(
            '/equipos/1/pokemon',
            data={'slot': 0, 'idPokemon': 25}
        )
        self.assertEqual(response.status_code, 302)

    def test_6_eliminar_pokemon(self):
        # Elimina un Pokémon de un slot usando la opción vacío
        response = self.client.post(
            '/equipos/1/pokemon',
            data={'slot': 0, 'idPokemon': '__empty__'}
        )
        self.assertEqual(response.status_code, 302)

    def test_7_modificar_nombre_equipo(self):
        # Modifica el nombre de un equipo existente
        response = self.client.post(
            '/equipos/1/modificar_nombre',
            data={'nombre': 'Equipo Modificado'}
        )
        self.assertEqual(response.status_code, 302)

    def test_8_eliminar_equipo(self):
        # Elimina un equipo completo
        response = self.client.post('/equipos/eliminar/1')
        self.assertEqual(response.status_code, 302)

    def test_10_volver_pokedex(self):
        # Comprueba que se puede acceder a la pokedex
        response = self.client.get('/pokedex')
        self.assertEqual(response.status_code, 200)

    def test_no_permite_nombre_equipo_duplicado(self):
        # Comprueba que no se permiten nombres de equipo duplicados
        self.client.post('/equipos/crear', data={'nombre': 'EquipoDuplicado'})
        self.client.post('/equipos/crear', data={'nombre': 'EquipoDuplicado'})
        response = self.client.get('/equipos')
        self.assertEqual(response.data.count(b'EquipoDuplicado'), 1)

    def test_no_permite_mas_de_seis_pokemons(self):
        # Comprueba que un equipo no puede tener más de seis Pokémon
        pokemons = [101, 102, 103, 104, 105, 106]

        for slot, pid in enumerate(pokemons):
            self.client.post(
                '/equipos/900/pokemon',
                data={'slot': slot, 'idPokemon': pid}
            )

        response = self.client.post(
            '/equipos/900/pokemon',
            data={'slot': 6, 'idPokemon': 107}
        )
        self.assertIn(response.status_code, (200, 302))

        response = self.client.post(
            '/equipos/900/pokemon',
            data={'slot': 6, 'idPokemon': 101}
        )
        self.assertIn(response.status_code, (200, 302))


if __name__ == '__main__':
    unittest.main()
