from flask import Blueprint, session, render_template, request, redirect, url_for
from app.controller.model.GestorCoches import GestorCoches
from app.controller.model.car_model import CarModel
from app.controller.model.Sesion import Sesion


def car_blueprint(db):
    bp = Blueprint("car", __name__)
    model = CarModel(db)
    service_coches = GestorCoches(db)  # Instancia para usar la búsqueda por ID

    # LISTAR COCHES
    @bp.route("/catalogo")
    def listar_coches():
        coches = model.get_all()
        # En tu proyecto, los datos del usuario suelen venir de Sesion().getSession()
        usuario_actual = Sesion().getSession()
        return render_template("catalogo.html", coches=coches, usuario=usuario_actual)

    # FORMULARIO AÑADIR
    @bp.route("/add_car", methods=["GET", "POST"])
    def add_car():
        if request.method == "POST":
            marca = request.form["marca"]
            modelo = request.form["modelo"]
            precio = request.form["precio"]
            kilometraje = request.form["kilometraje"]
            imagen = request.form["imagen"]

            model.add_car(marca, modelo, precio, kilometraje, imagen)
            return redirect(url_for("car.listar_coches"))

        return render_template("add_car.html", usuario=Sesion().getSession())

    # ELIMINAR COCHE
    @bp.route("/delete_car/<int:idCoche>")
    def delete_car(idCoche):
        model.delete_car(idCoche)
        return redirect(url_for("car.listar_coches"))

    # DETALLES DEL COCHE
    @bp.route('/detalles/<int:id_coche>')
    def detalles_coche(id_coche):
        # 1. Cambiado @app por @bp
        # 2. Usamos el servicio para buscar el coche específico
        todos = model.get_all()
        coche = next((c for c in todos if c['idCoche'] == id_coche), None)

        if not coche:
            return "Vehículo no encontrado", 404

        return render_template('detalles.html', coche=coche, usuario=Sesion().getSession())

    return bp