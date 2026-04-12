from flask import Blueprint,session, render_template, request, redirect, url_for
from app.controller.model.car_model import CarModel


def car_blueprint(db):
    bp = Blueprint("car", __name__)
    model = CarModel(db)

    # LISTAR COCHES (ya lo tienes parecido)
    @bp.route("/catalogo")
    def listar_coches():
        coches = model.get_all()
        return render_template("catalogo.html", coches=coches, usuario=session.get("usuario"))

    # FORMULARIO
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

        return render_template("add_car.html", usuario=session.get("usuario"))


    @bp.route("/delete_car/<int:idCoche>")
    def delete_car(idCoche):
        model.delete_car(idCoche)
        return redirect(url_for("car.listar_coches"))


    return bp