from flask import Flask

from app import create_app

app = create_app()


if __name__ == '__main__':
    app.run(debug=True)   # para no tener que reiniciar el servidor al hacer pruebas añadir parámetro--> debug=True
