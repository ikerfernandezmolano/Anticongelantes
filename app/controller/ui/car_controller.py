import os
from flask import Blueprint, session, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
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
        usuario_actual = Sesion().getSession()

        # Calculamos los máximos reales (si hay coches)
        if coches:
            max_precio_real = max(c['precio'] for c in coches)
            max_km_real = max(c['kilometraje'] for c in coches)
        else:
            max_precio_real = 600000
            max_km_real = 500000

        return render_template("catalogo.html", 
                               coches=coches, 
                               usuario=usuario_actual,
                               max_p=max_precio_real,
                               max_k=max_km_real)

    # GESTIONAR COCHES (VISTA ADMIN)
    @bp.route("/manage_cars")
    def manage_cars():
        usuario_actual = Sesion().getSession()
        if not usuario_actual or usuario_actual.get('Estado') != 'Admin':
            return redirect(url_for("car.listar_coches"))
            
        coches = model.get_all()
        return render_template("manage_cars.html", coches=coches, usuario=usuario_actual)

    # FORMULARIO AÑADIR
    @bp.route("/add_car", methods=["GET", "POST"])
    def add_car():
        usuario_actual = Sesion().getSession()
        # Verificamos que haya sesión y que sea Admin
        if not usuario_actual or usuario_actual.get('Estado') != 'Admin':
            return redirect(url_for("car.listar_coches"))
            
        if request.method == "POST":
            marca = request.form["marca"]
            modelo = request.form["modelo"]
            precio = request.form["precio"]
            kilometraje = request.form["kilometraje"]
            
            # Obtenemos el archivo de imagen subido
            imagen_file = request.files.get("imagen")
            if imagen_file and imagen_file.filename:
                filename = secure_filename(imagen_file.filename)
                ruta_destino = os.path.join("app", "static", filename)
                imagen_file.save(ruta_destino)
                imagen = filename
            else:
                imagen = "fondo.jpg" # Si ocurre algún error, ponemos una por defecto

            model.add_car(marca, modelo, precio, kilometraje, imagen)
            return redirect(url_for("car.listar_coches"))

        return render_template("add_car.html", usuario=usuario_actual)

    # ELIMINAR COCHE
    @bp.route("/delete_car/<int:idCoche>")
    def delete_car(idCoche):
        usuario_actual = Sesion().getSession()
        if not usuario_actual or usuario_actual.get('Estado') != 'Admin':
            return redirect(url_for("car.listar_coches"))
            
        model.delete_car(idCoche)
        return redirect(url_for("car.manage_cars"))

    # EDITAR COCHE
    @bp.route("/edit_car/<int:idCoche>", methods=["GET", "POST"])
    def edit_car(idCoche):
        usuario_actual = Sesion().getSession()
        if not usuario_actual or usuario_actual.get('Estado') != 'Admin':
            return redirect(url_for("car.listar_coches"))
            
        todos = model.get_all()
        coche = next((c for c in todos if c['idCoche'] == idCoche), None)
        if not coche:
            return "Vehículo no encontrado", 404
            
        if request.method == "POST":
            marca = request.form["marca"]
            modelo = request.form["modelo"]
            precio = request.form["precio"]
            kilometraje = request.form["kilometraje"]
            
            imagen_file = request.files.get("imagen")
            if imagen_file and imagen_file.filename:
                filename = secure_filename(imagen_file.filename)
                ruta_destino = os.path.join("app", "static", filename)
                imagen_file.save(ruta_destino)
                imagen = filename
            else:
                imagen = coche['imagen'] # Mantenemos la vieja si no sube una nueva
                
            model.update_car(idCoche, marca, modelo, precio, kilometraje, imagen)
            return redirect(url_for("car.manage_cars"))
            
        return render_template("edit_car.html", coche=coche, usuario=usuario_actual)

    # DETALLES DEL COCHE
    @bp.route('/detalles/<int:id_coche>')
    def detalles_coche(id_coche):
        todos = model.get_all()
        coche = next((c for c in todos if c['idCoche'] == id_coche), None)
        if not coche:
            return "Vehículo no encontrado", 404
        return render_template('detalles.html', coche=coche, usuario=Sesion().getSession())

    return bp
