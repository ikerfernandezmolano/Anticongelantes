from flask import Blueprint, request, redirect, render_template, flash, url_for
from app.controller.model.GestorUsuarios import GestorUsuarios
from app.controller.model.GestorEspecies import GestorEspecies
from app.controller.model.GestorCoches import GestorCoches
from flask import get_flashed_messages

def home_blueprint():
    bp = Blueprint('home', __name__)

    @bp.route('/')
    def root():
        return redirect(url_for('home.index'))

    @bp.route('/home')
    def index():
        return render_template('home.html')

    return bp
    
def db_blueprint(db):
    bp = Blueprint('db', __name__)
    service = GestorUsuarios(db)
    service2 = GestorEspecies(db)

    @bp.route('/db')
    def bd():
        users = service.get_all()
        usuario_sesion = service.getSession()  # puede ser None si nadie ha iniciado sesión
        especies = service2.get_all()
        return render_template('db.html', usuarios=users, usuario_sesion=usuario_sesion, especies=especies)

    return bp

def registro_blueprint(db):
    bp = Blueprint('registro', __name__)
    service = GestorUsuarios(db)

    @bp.route('/registro', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            user = request.form.get('user')
            email = request.form.get('email')
            password = request.form.get('password', '').strip()
            password_confirm = request.form.get('confirm_password', '').strip()

            if password != password_confirm:
                flash("LAS CONTRASEÑAS NO COINCIDEN", "error")
            else:
                status = service.añadirUsuario(user, email, password)
                if status == 0:
                    flash("SOLICITUD DE REGISTRO ENVIADA", "success")
                elif status == 1:
                    flash("USUARIO YA EXISTE", "error")
                elif status == 2:
                    flash("CORREO PREVIAMENTE REGISTRADO", "error")
                elif status == 3:
                    flash("ERROR DESCONOCIDO INTÉNTALO MÁS TARDE", "error")
        mensajes = get_flashed_messages(with_categories=True)
        return render_template('registro.html', mensajes=mensajes)

    return bp

def inicioSesion_blueprint(db):
    bp = Blueprint('inicioSesion', __name__)
    service = GestorUsuarios(db)

    @bp.route('/inicioSesion', methods=['GET', 'POST'])
    def iniciarSesion():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password', '').strip()
            status = service.iniciarSesion(email,password)
            if status == 0:
                return redirect(url_for('pokedex.index'))
            elif status == 1:
                flash("EL USUARIO NO EXISTE", "error")
            elif status == 2:
                flash("CONTRASEÑA INCORRECTA", "error")
            elif status == 3:
                flash("USUARIO AÚN NO ACEPTADO", "error")
            else:
                flash("ERROR DESCONOCIDO, INTÉNTALO MÁS TARDE", "error")

        mensajes = get_flashed_messages(with_categories=True)
        return render_template('inicioSesion.html', mensajes=mensajes)

    return bp

def catalogo_blueprint(db):
    bp = Blueprint('catalogo', __name__)
    service = GestorCoches(db)

    @bp.route('/catalogo')
    def mostrar_catalogo():
        lista_vehiculos = service.get_all()
        return render_template('catalogo.html', coches=lista_vehiculos)

    return bp


def amigos_blueprint(db):
    bp = Blueprint('amigos', __name__)
    service = GestorUsuarios(db)

    @bp.route('/amigos', methods=['GET', 'POST'])
    def amigos():
        sesion = service.getSession()
        if request.method == 'POST':
            user_id = request.form.get('user_id')
            accion = request.form.get('accion')

            if accion == 'dejarseguir':
                service.dejarseguir(sesion['IDUsuario'],user_id)
            elif accion == 'seguir':
                service.seguir(sesion['IDUsuario'],user_id)

            # Redirige a la misma página para recargar la lista
            return redirect(url_for('amigos.amigos'))

            # GET: mostramos usuarios
        usuarios1 = service.get_amigos(sesion['IDUsuario'])
        usuarios2 = service.get_solicitud(sesion['IDUsuario'])
        usuarios3 = service.get_noamigos(sesion['IDUsuario'])
        usuarios4 = service.get_esperandoamigo(sesion['IDUsuario'])
        return render_template('amigos.html', usuarios1=usuarios1, usuarios2=usuarios2, usuarios3=usuarios3, usuarios4=usuarios4)
    return bp
    
def modificarDatos_blueprint(db):
    bp = Blueprint('modifyUser', __name__)
    service = GestorUsuarios(db)
    service2 = GestorEspecies(db)

    @bp.route('/modificarDatos', methods=['GET', 'POST'])
    def modificarDatos():
        if request.method == 'POST':
            email = request.form.get('email')
            password_old = request.form.get('password_old', '').strip()
            password_new = request.form.get('password_new', '').strip()
            
            status = service.modificarDatos(email,password_old,password_new)
            if status == 0:
                flash("CAMBIOS REALIZADOS CORRECTAMENTE", "success")
            elif status == 1:
                flash("CONTRASEÑA ACTUAL INCORRECTA", "error")
            elif status == 2:
                flash("CORREO YA REGISTRADO", "error")
            elif status == 3:
                flash("COMPLETA TODOS LOS CAMPOS", "error")
            else:
                flash("CAMBIOS NO REALIZADOS CORRECTAMENTE", "error")
                
        usuario_sesion = service.getSession() # puede ser None si nadie ha iniciado sesión
        lista_pokemons = service2.get_all()
        mensajes = get_flashed_messages(with_categories=True)
        return render_template('modificarDatos.html', mensajes=mensajes, usuario_sesion=usuario_sesion, lista_pokemons=lista_pokemons)

    return bp
    
def modificarDatosAdmin_blueprint(db):
    bp = Blueprint('modifyUserAdmin', __name__)
    service = GestorUsuarios(db)
    service2 = GestorEspecies(db)
    
    @bp.route('/modificarDatosAdmin', methods=['GET', 'POST'])
    def modificarDatosAdmin():
        sesion = service.getSession()['Estado']
        if sesion and sesion != 'Admin':
            return "No tienes los permisos necesarios para utilizar esta interfaz", 400
        else:
            # Coger el parámetro 'id' de la URL
            user_id = request.args.get('id')  # Devuelve str o None si no existe

            if user_id is None:
                return "No se proporcionó ID de usuario", 400  # Código de error si falta

            # Convertir a int si quieres usarlo como número
            try:
                user_id = int(user_id)
                if request.method == 'POST':
                    email = request.form.get('email')
                    password = request.form.get('password', '').strip()
                    
                    status = service.modificarDatosAdmin(email,password,user_id)
                    if status == 0:
                        flash("CAMBIOS REALIZADOS CORRECTAMENTE", "success")
                    elif status == 1:
                        flash("CORREO YA REGISTRADO", "error")
                    elif status == 2:
                        return "No tienes los permisos necesarios para utilizar esta interfaz", 400
                    else:
                        flash(status,"error")
                
            except ValueError:
                return "ID de usuario inválido", 400

            # Ahora puedes usar user_id para buscar el usuario en la base de datos
            usuario = service.get_usuario(user_id)  # ejemplo de función de tu servicio
            lista_pokemons = service2.get_all()
            mensajes = get_flashed_messages(with_categories=True)
            return render_template('modificarDatosAdmin.html', usuario=usuario, lista_pokemons=lista_pokemons, mensajes=mensajes)
    
    return bp
    
def gestionUsuarios_blueprint(db):
    bp = Blueprint('gestionUsuarios', __name__)
    service = GestorUsuarios(db)

    @bp.route('/gestionUsuarios', methods=['GET', 'POST'])
    def gestionUsuarios():
        sesion = service.getSession()['Estado']
        if sesion and sesion != 'Admin':
            return "No tienes los permisos necesarios para utilizar esta interfaz", 400
        else:
            if request.method == 'POST':
                user_id = int(request.form.get('user_id'))
                accion = request.form.get('accion')

                if accion == 'aceptar':
                    service.aceptar(user_id)
                elif accion == 'rechazar':
                    service.rechazar(user_id)
                elif accion == 'eliminar':
                    service.eliminar(user_id) 

                # Redirige a la misma página para recargar la lista
                return redirect(url_for('gestionUsuarios.gestionUsuarios'))

            # GET: mostramos usuarios
            usuarios1 = service.get_aceptados()
            usuarios2 = service.get_espera()
            return render_template('gestionUsuarios.html', usuarios1=usuarios1, usuarios2=usuarios2)
    return bp
    

    

