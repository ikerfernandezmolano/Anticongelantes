from flask import Blueprint, render_template, redirect, url_for
from app.controller.model.GestorUsuarios import GestorUsuarios
from app.controller.model.Sesion import Sesion

def manage_users_blueprint(db):
    # Creamos el Blueprint para agrupar las rutas de gestión de usuarios
    bp = Blueprint("manage_users", __name__)
    
    # Instanciamos el modelo de usuarios
    gestor = GestorUsuarios(db)

    @bp.route("/manage_users", methods=["GET"])
    def listar_usuarios():
        """
        Controlador para listar todos los usuarios del sistema.
        Exclusivo para el Administrador.
        """
        try:
            # Obtenemos el usuario de la sesión actual
            sesion_actual = Sesion()
            usuario_actual_id = sesion_actual.usuario.IDUsuario
            
            # Obtenemos la información del usuario desde la base de datos
            usuario_info = gestor.get_usuario(usuario_actual_id)
            
            # Verificamos si su Estado es 'Admin'. Si no lo es, por seguridad lo redirigimos al login o al index.
            if usuario_info.get("Estado") != "Admin":
                # Asumiendo que existe un endpoint de inicio ('home' o 'pokedex.index')
                return redirect("/")
        except Exception as e:
            print(f"[ERROR - Manage Users] Error validando sesión: {e}")
            return redirect("/")
            
        # Pedimos al modelo que nos traiga la lista de todos los usuarios
        usuarios = gestor.get_all()
        
        # Renderizamos la plantilla HTML y le pasamos los datos
        return render_template("manageUsers.html", usuarios=usuarios)

    return bp