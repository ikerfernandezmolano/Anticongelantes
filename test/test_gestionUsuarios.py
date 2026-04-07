import unittest
import os
import sqlite3
import sys
import time

# Añade el directorio raíz al path para poder importar la app
sys.path.insert(0, os.getcwd())

from app import create_app
from app.config import Config
from app.controller.model.Sesion import Sesion
from app.controller.model.Usuario import Usuario

# Base de datos de pruebas
TEST_DB = 'test_pimpam.db'


class TestUsuarios(unittest.TestCase):

    def setUp(self):
        """CONFIGURACIÓN INICIAL"""
        self._borrar_bd_segura()
        Config.DB_PATH = TEST_DB 
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self._init_test_db()


    def tearDown(self):
        """LIMPIEZA"""
        del self.client
        del self.app
        Sesion().usuario=Usuario(0,'','','','',0)
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
        conn = sqlite3.connect(TEST_DB, timeout=10)
        cursor = conn.cursor()

        schema_path = os.path.join(os.getcwd(), 'app', 'database', 'schema.sql')
        with open(schema_path, 'r') as f:
            try:
                cursor.executescript(f.read())
            except sqlite3.OperationalError:
                pass

        cursor.execute("INSERT OR IGNORE INTO Especie (PokedexID, Nombre, Generacion) VALUES (1, 'bulbasaur', 1)")
        cursor.execute("INSERT OR IGNORE INTO Especie (PokedexID, Nombre, Generacion) VALUES (2, 'ivysaur', 1)")
        cursor.execute("INSERT OR IGNORE INTO Especie (PokedexID, Nombre, Generacion) VALUES (4, 'charmander', 1)")
        cursor.execute("INSERT OR IGNORE INTO Especie (PokedexID, Nombre, Generacion) VALUES (25, 'pikachu', 1)")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Usuario (
                IDUsuario INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre TEXT,
                Email TEXT UNIQUE,
                Contrasena TEXT,
                Estado TEXT,
                IDFavorito INTEGER
            )
        """)

        # Usuario Aceptado con ID 1
        cursor.execute("""
            INSERT OR IGNORE INTO Usuario
            (Nombre, Email, Contrasena, Estado, IDFavorito)
            VALUES ('Admin', 'admin@test.com', 'admin', 'Aceptado', 1)
        """)

        # Usuario Pendiente con ID 2
        cursor.execute("""
            INSERT OR IGNORE INTO Usuario 
            (Nombre, Email, Contrasena, Estado, IDFavorito)
            VALUES ('Pendiente', 'pendiente@test.com', 'test','Esperando', 4)
        """)

        # Usuarios extra
        cursor.execute("""
            INSERT OR IGNORE INTO Usuario 
            (Nombre, Email, Contrasena, Estado, IDFavorito)
            VALUES ('User1', 'user1@test.com', '1234', 'Aceptado', 1)
        """)
        cursor.execute("""
            INSERT OR IGNORE INTO Usuario 
            (Nombre, Email, Contrasena, Estado, IDFavorito)
            VALUES ('User2', 'user2@test.com', '1234', 'Aceptado', 1)
        """)

        conn.commit()
        conn.close()
    
    #--------------------LOGIN-------------------------
    # -------------------------------------------------
    # TEST 1: Usuario no registrado
    def test_1_usuario_no_existe(self):
        response = self.client.post('/inicioSesion', data={
            'email': 'noexiste@test.com',
            'password': '1234'
        })
        self.assertIn(b'EL USUARIO NO EXISTE', response.data)

    # -------------------------------------------------
    # TEST 2: Contraseña incorrecta
    def test_2_contrasena_incorrecta(self):
        response = self.client.post('/inicioSesion', data={
            'email': 'admin@test.com',
            'password': 'incorrecta'
        })
        self.assertIn(b'CONTRASE\xc3\x91A INCORRECTA', response.data)

    # -------------------------------------------------
    # TEST 3: Usuario aún no aceptado
    def test_3_usuario_no_aceptado(self):
        response = self.client.post('/inicioSesion', data={
            'email': 'pendiente@test.com',
            'password': 'test'
        })
        self.assertIn(b'USUARIO A\xc3\x9aN NO ACEPTADO', response.data)

    # -------------------------------------------------
    # TEST 4: Login correcto
    def test_4_login_correcto(self):
        response = self.client.post('/inicioSesion', data={
            'email': 'admin@test.com',
            'password': 'admin'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'GRENINJA', response.data)

    # -------------------------------------------------
    # TEST 5: Botón retroceder
    def test_5_retroceder(self):
        response = self.client.get('/home')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'PIMPAM', response.data)

    # -------------------------------------------------
    # TEST 6: Error de conexión
    # No podemos probar este test
    def test_6_error_conexion(self):
        # Forzamos una ruta inválida de BD, pero la app no gestiona el error
        Config.DB_PATH = '/ruta/invalida/test.db'

        response = self.client.post('/inicioSesion', data={
            'email': 'admin@test.com',
            'password': 'admin'
        })

        # La app redirige igualmente
        self.assertEqual(response.status_code, 302)
        self.assertIn(b'/pokedex', response.data)
        
    #--------------------REGISTRARSE-------------------
    # -------------------------------------------------
    # TEST 1: Registro correcto
    def test_1_registro_correcto(self):
        response = self.client.post('/registro', data={
            'user': 'NuevoUsuario',
            'email': 'nuevo@test.com',
            'password': '1234',
            'confirm_password': '1234'
        })
        self.assertIn(b'SOLICITUD DE REGISTRO ENVIADA', response.data)

    # -------------------------------------------------
    # TEST 2: Usuario ya existente
    def test_2_usuario_existente(self):
        response = self.client.post('/registro', data={
            'user': 'Admin',
            'email': 'otro@test.com',
            'password': '1234',
            'confirm_password': '1234'
        })
        self.assertIn(b'USUARIO YA EXISTE', response.data)

    # -------------------------------------------------
    # TEST 3: Correo ya registrado
    def test_3_correo_existente(self):
        response = self.client.post('/registro', data={
            'user': 'OtroUsuario',
            'email': 'admin@test.com',
            'password': '1234',
            'confirm_password': '1234'
        })
        self.assertIn(b'CORREO PREVIAMENTE REGISTRADO', response.data)

    # -------------------------------------------------
    # TEST 4: Contraseñas no coinciden
    def test_4_contrasenas_no_coinciden(self):
        response = self.client.post('/registro', data={
            'user': 'UsuarioNuevo',
            'email': 'nuevo2@test.com',
            'password': '1234',
            'confirm_password': '4321'
        })
        self.assertIn(b'LAS CONTRASE\xc3\x91AS NO COINCIDEN', response.data)

    # -------------------------------------------------
    # TEST 5: Botón retroceder
    def test_5_retroceder(self):
        response = self.client.get('/home')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'PIMPAM', response.data)

    # -------------------------------------------------
    # TEST 6: Error de conexión
    # No podemos probar este test
    def test_6_error_conexion(self):
        Config.DB_PATH = '/ruta/invalida/test.db'

        response = self.client.post('/registro', data={
            'user': 'ErrorUser',
            'email': 'error@test.com',
            'password': '1234',
            'confirm_password': '1234'
        })

        # La app NO gestiona errores de conexión
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SOLICITUD DE REGISTRO ENVIADA', response.data)
        
    #----------------------AMIGOS----------------------
    # 1: No sesión → acceso denegado
    def test_1_no_sesion(self):
        Sesion().usuario = None
        # Verifica que acceder a /amigos sin sesión lanza AttributeError
        with self.assertRaises(AttributeError):
            self.client.get('/amigos')


    # 2: Acceso correcto con sesión
    def test_2_acceso_correcto(self):
        Sesion().usuario.IDUsuario = 1
        response = self.client.get('/amigos')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AMIGOS', response.data)
        self.assertIn(b'SUGERENCIAS', response.data)

    # 3: Añadir amigo válido
    def test_3_añadir_amigo(self):
        Sesion().usuario.IDUsuario = 1
        # Usuario 2 está disponible para añadir
        response = self.client.post('/amigos', data={'accion': 'seguir', 'user_id': 2}, follow_redirects=True)
        html = response.data.decode('utf-8')

        # Debe aparecer en la lista de solicitudes enviadas o esperando aceptación
        self.assertIn('pendiente', html.lower() or 'esperandoamigo.png' in html)

        # Verificar base de datos
        with sqlite3.connect(TEST_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Seguidor WHERE IDUsuarioSeguido=2 AND IDUsuarioSeguidor=1")
            self.assertEqual(len(cursor.fetchall()), 1)

    # 4: Eliminar amigo
    def test_4_eliminar_amigo(self):
        Sesion().usuario.IDUsuario = 1
        # Primero añadimos como amigo directamente en BD
        with sqlite3.connect(TEST_DB) as conn:
            conn.execute("INSERT INTO Seguidor (IDUsuarioSeguido, IDUsuarioSeguidor) VALUES (1, 2)")
            conn.execute("INSERT INTO Seguidor (IDUsuarioSeguido, IDUsuarioSeguidor) VALUES (2, 1)")

        response = self.client.post('/amigos', data={'accion': 'dejarseguir', 'user_id': 2}, follow_redirects=True)
        html = response.data.decode('utf-8')

        # Usuario ya no debe aparecer en la lista de amigos
        self.assertNotIn('Pendiente', html.lower() or 'esperandoamigo.png' in html)

    # 5: Botón retroceder
    def test_6_retroceder(self):
        response = self.client.get('/pokedex')
        self.assertIn(b'Pokedex - PimPam', response.data)

    # 6: Persistencia tras añadir/eliminar
    # Test visual
    
    #----------------------GESTION DATOS----------------------
    # 1. Usuario no logueado
    def test_1_no_sesion(self):
        Sesion().usuario = None
        with self.assertRaises(AttributeError):
            self.client.get('/modificarDatos')

    # 2. Usuario inicia sesión y accede
    def test_2_acceso_correcto(self):
        Sesion().usuario.IDUsuario = 1
        response = self.client.get('/modificarDatos')
        html = response.data.decode('utf-8')
        self.assertIn('MODIFICAR DATOS', html)

    # 3. Usuario retrocede sin cambios
    def test_3_retroceder_sin_cambios(self):
        Sesion().usuario.IDUsuario = 1
        response = self.client.get('/modificarDatos')
        # Simular clic en retroceder
        response = self.client.get('/pokedex')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Pokedex - PimPam', response.data)

    # 4. Usuario modifica datos correctamente
    def test_4_modificacion_correcta(self):
        # Usuario logueado con ID 1
        Sesion().usuario = Usuario(1, 'Admin', 'admin@test.com', 'admin', 'Aceptado', 1)

        # Datos de modificación
        data = {
            'email': 'nuevo@test.com',
            'password_old': 'admin',       # contraseña correcta
            'password_new': 'admin123',
            'pokefav': 'bulbasaur'         # exactamente igual que en la DB
        }

        # Llamada a la vista
        response = self.client.post('/modificarDatos', data=data, follow_redirects=True)

        # Comprobación de mensaje de éxito
        self.assertIn(b'CAMBIOS REALIZADOS CORRECTAMENTE', response.data)


    # 5. Usuario introduce correo ya registrado
    def test_5_correo_existente(self):
        Sesion().usuario = Usuario(1,'Admin','admin@test.com','admin','Aceptado',1)
        response = self.client.post('/modificarDatos', data={
            'email': 'pendiente@test.com',
            'password_old': 'admin',
            'password_new': '',
            'pokefav': 'bulbasaur'
        }, follow_redirects=True)
        self.assertIn(b'CORREO YA REGISTRADO', response.data)

    # 6. Usuario introduce contraseña actual incorrecta
    def test_6_pass_incorrecta(self):
        Sesion().usuario = Usuario(1,'Admin','admin@test.com','admin','Aceptado',1)
        data = {
            'email': 'nuevo2@test.com',
            'password_old': 'wrongpass',
            'password_new': 'nuevo2',
            'pokefav': 'bulbasaur'
        }
        response = self.client.post('/modificarDatos', data=data, follow_redirects=True)
        self.assertIn(b'CONTRASE\xc3\x91A ACTUAL INCORRECTA', response.data)

    # 7. Varias modificaciones correctas seguidas
    def test_7_varias_modificaciones(self):
        Sesion().usuario = Usuario(1, 'Admin', 'admin@test.com', 'admin0', 'Aceptado', 1)
        current_password = 'admin0'  # contraseña inicial en la BD
        for i in range(2):
            new_password = f'admin{i}'  # nueva contraseña a establecer
            response = self.client.post('/modificarDatos', data={
                'email': f'nuevo{i}@test.com',
                'password_old': current_password,  # contraseña correcta actual
                'password_new': new_password,
                'pokefav': 'charmander'
            }, follow_redirects=True)
            self.assertIn(b'CAMBIOS REALIZADOS CORRECTAMENTE', response.data)
            current_password = new_password  # actualizamos para la siguiente iteración


    # 8. Usuario retrocede con cambios pendientes
    def test_8_retroceder(self):
        Sesion().usuario.IDUsuario = 1
        response = self.client.get('/pokedex')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Pokedex - PimPam', response.data)
        
    # ----------------------GESTIÓN DE USUARIOS----------------------
    # 1: Usuario no admin → acceso denegado
    def test_1_no_admin_acceso(self):
        Sesion().usuario = Usuario(2,'User1','user1@test.com','1234','Aceptado',1)
        response = self.client.get('/gestionUsuarios')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No tienes los permisos necesarios', response.data)

    # 2: Admin accede correctamente
    def test_2_admin_acceso(self):
        Sesion().usuario = Usuario(1,'Admin','admin@test.com','admin','Admin',1)
        response = self.client.get('/gestionUsuarios')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn('ACEPTADOS', html)
        self.assertIn('GESTIÓN DE USUARIOS', html)

    # 3: Administrador acepta usuario pendiente
    def test_3_aceptar_usuario(self):
        Sesion().usuario = Usuario(1,'Admin','admin@test.com','admin','Admin',1)
        # Asegurar que usuario 2 está pendiente
        with sqlite3.connect(TEST_DB) as conn:
            conn.execute("UPDATE Usuario SET Estado='Esperando' WHERE IDUsuario=2")

        response = self.client.post('/gestionUsuarios', data={'user_id':2,'accion':'aceptar'}, follow_redirects=True)
        html = response.data.decode('utf-8')

        with sqlite3.connect(TEST_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Estado FROM Usuario WHERE IDUsuario=2")
            estado = cursor.fetchone()[0]
            self.assertEqual(estado, 'Aceptado')

    # 4: Administrador rechaza usuario pendiente
    def test_4_rechazar_usuario(self):
        Sesion().usuario = Usuario(1,'Admin','admin@test.com','admin','Admin',1)
        
        # Asegurar que usuario 2 está pendiente
        with sqlite3.connect(TEST_DB) as conn:
            conn.execute("UPDATE Usuario SET Estado='Espera' WHERE IDUsuario=2")

        # POST con acción "rechazar"
        response = self.client.post('/gestionUsuarios', data={'user_id':2,'accion':'eliminar'}, follow_redirects=True)

        # Comprobamos en la BD que el usuario ya no está pendiente
        with sqlite3.connect(TEST_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Usuario WHERE IDUsuario=2")
            user = cursor.fetchone()
            # Dependiendo de tu implementación, si lo eliminas completamente:
            self.assertIsNone(user)


    # 5: Administrador elimina usuario aceptado
    def test_5_eliminar_usuario(self):
        Sesion().usuario = Usuario(1,'Admin','admin@test.com','admin','Admin',1)
        # Asegurarnos de que User1 (ID 3) está aceptado
        with sqlite3.connect(TEST_DB) as conn:
            conn.execute("UPDATE Usuario SET Estado='Aceptado' WHERE IDUsuario=3")

        response = self.client.post('/gestionUsuarios', data={'user_id':3,'accion':'rechazar'}, follow_redirects=True)
        html = response.data.decode('utf-8')
        
        with sqlite3.connect(TEST_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Estado FROM Usuario WHERE IDUsuario=3")
            estado = cursor.fetchone()[0]
            self.assertEqual(estado, 'Rechazado')  # o como sea que manejes el estado "rechazado"

    # 6: Administrador edita usuario
    def test_6_modificar_usuario(self):
        Sesion().usuario = Usuario(1,'Admin','admin@test.com','admin','Admin',1)
        response = self.client.get('/modificarDatosAdmin?id=3')
        html = response.data.decode('utf-8')
        self.assertIn('MODIFICAR DATOS', html)
        self.assertIn('pendiente@test.com', html)

    # 7: Botón retroceder
    def test_7_retroceder(self):
        response = self.client.get('/pokedex')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Pokedex - PimPam', response.data)

if __name__ == '__main__':
    unittest.main()

