import os.path
import sqlite3

from flask import Flask

from app.controller.ui.book_controller import book_blueprint
from app.controller.ui.loan_controller import loan_blueprint
from app.controller.ui.user_controlller import user_blueprint
from app.database.connection import Connection
from config import Config


def init_db():
    print("Iniciando la base de datos")
    if os.path.exists(Config.DB_PATH):
        print("La base de datos existe")
        conn = sqlite3.connect(Config.DB_PATH)
        with open('app/database/schema.sql') as f:
            conn.executescript(f.read())
        conn.close()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar base de datos
    init_db()

    # Crear conexión a la base de datos
    db = Connection()

    app.register_blueprint(user_blueprint(db))
    app.register_blueprint(book_blueprint(db))
    app.register_blueprint(loan_blueprint(db))

    return app