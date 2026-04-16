import os.path
import os
import sqlite3


from flask import Flask

from app.database.SGBD import SGBD
from app.config import Config
from app.controller.ui.ControladorVista import *
from app.controller.ui.car_controller import car_blueprint

def init_db():
    print("Iniciando la base de datos")
    conn = sqlite3.connect(Config.DB_PATH)
    try:
        # 1) schema
        with open("app/database/schema.sql", encoding="utf-8") as f:
            conn.executescript(f.read())

        conn.commit()
    except Exception as e:
        print(f"Error inicializando BD: {e}")
    finally:
        conn.close()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar base de datos
    init_db()

    # Crear conexión a la base de datos
    db = SGBD()

    app.register_blueprint(home_blueprint())
    app.register_blueprint(registro_blueprint(db))
    app.register_blueprint(inicioSesion_blueprint(db))
    app.register_blueprint(modificarDatos_blueprint(db))
    app.register_blueprint(modificarDatosAdmin_blueprint(db))
    app.register_blueprint(gestionUsuarios_blueprint(db))

    #catalogo coches
    app.register_blueprint(catalogo_blueprint(db))
    app.register_blueprint(car_blueprint(db))
    
    # Monitorización
    app.register_blueprint(db_blueprint(db))


    return app
