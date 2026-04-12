from flask import Blueprint, render_template, redirect, url_for, request
from app.controller.model.GestorUsuarios import GestorUsuarios
from app.controller.model.Sesion import Sesion

def manage_users_blueprint(db):
    # Creamos el Blueprint para agrupar las rutas de gestión de usuarios
    bp = Blueprint("manage_users", __name__)
    
    # Instanciamos el modelo de usuarios
    gestor = GestorUsuarios(db)

    @bp.route("/admin_panel", methods=["GET"])
    def admin_dashboard():
        """
        Controlador para el menú general del administrador.
        """
        try:
            # Obtenemos el usuario de la sesión actual
            sesion_actual = Sesion()
            usuario_actual_id = sesion_actual.usuario.IDUsuario
            
            # Obtenemos la información del usuario desde la base de datos
            usuario_info = gestor.get_usuario(usuario_actual_id)
            
            # Verificamos si su Estado es 'Admin'
            if usuario_info.get("Estado") != "Admin":
                return redirect("/catalogo")
                
        except Exception as e:
            print(f"[ERROR - Admin Panel] Error validando sesión: {e}")
            return redirect("/catalogo")
            
        # Si es Admin, renderizamos el menú principal
        return render_template("admin_panel.html")


    @bp.route("/gestionUsuarios", methods=["GET", "POST"])
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
            if not usuario_info or usuario_info.get("Estado") != "Admin":
                return "No tienes los permisos necesarios", 400
        except Exception as e:
            print(f"[ERROR - Manage Users] Error validando sesión: {e}")
            return redirect("/")
            
        if request.method == "POST":
            accion = request.form.get("accion")
            
            if accion == "crear_usuario":
                nombre = request.form.get("nombre")
                email = request.form.get("email")
                password = request.form.get("password")
                try:
                    # Creamos el usuario y lo dejamos como 'Aceptado' por defecto al ser creado por el admin
                    db.executeSQL("INSERT INTO Usuario (Nombre, Email, Contrasena, Estado) VALUES (?, ?, ?, 'Aceptado')", (nombre, email, password))
                except Exception as e:
                    print(f"Error creando usuario: {e}")
                return redirect("/gestionUsuarios")

            user_id_str = request.form.get("user_id")
            if user_id_str:
                user_id = int(user_id_str)
                
                target_user = gestor.get_usuario(user_id)
                if target_user:
                    es_admin = target_user.get("Estado") == "Admin"
                    es_mismo = (user_id == usuario_actual_id)
                    
                    if accion == "aceptar":
                        db.executeSQL("UPDATE Usuario SET Estado = 'Aceptado' WHERE IDUsuario = ?", (user_id,))
                    elif accion in ["rechazar", "eliminar"] and (not es_admin or es_mismo):
                        db.executeSQL("UPDATE Usuario SET Estado = 'Rechazado' WHERE IDUsuario = ?", (user_id,))
                    elif accion == "espera" and not es_admin:
                        db.executeSQL("UPDATE Usuario SET Estado = 'Espera' WHERE IDUsuario = ?", (user_id,))
                    elif accion == "hacer_admin" and not es_admin:
                        db.executeSQL("UPDATE Usuario SET Estado = 'Admin' WHERE IDUsuario = ?", (user_id,))
                
            return redirect("/gestionUsuarios")

        # Pedimos al modelo que nos traiga la lista de todos los usuarios
        usuarios = gestor.get_all()
        usuarios1 = [u for u in usuarios if u.get("Estado") in ["Aceptado", "Admin"]]
        usuarios2 = [u for u in usuarios if u.get("Estado") in ["Espera", "Esperando"]]
        
        # Renderizamos la plantilla HTML y le pasamos los datos
        return render_template("gestionUsuarios.html", usuarios1=usuarios1, usuarios2=usuarios2, current_user_id=usuario_actual_id)

    return bp