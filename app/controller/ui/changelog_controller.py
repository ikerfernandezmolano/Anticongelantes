from flask import Blueprint, render_template, request, redirect, url_for
from app.controller.model.changelog_controller import ChangelogController
# Importamos la clase Sesion personalizada para gestionar quién está conectado
from app.controller.model.Sesion import Sesion
from app.controller.model.GestorUsuarios import GestorUsuarios

def changelog_blueprint(db):
    # Creamos el Blueprint para agrupar las rutas relacionadas con el historial
    bp = Blueprint("changelog", __name__)
    
    # Instanciamos el controlador que contiene la lógica de base de datos
    model = ChangelogController(db) 
    gestor_usuarios = GestorUsuarios(db)

    @bp.route("/changelog", methods=["GET", "POST"])
    def ver_changelog():
        """
        Controlador principal de la vista Changelog.
        - GET: Muestra el feed de actividad de los amigos y del propio usuario.
        - POST: Filtra los mensajes si el usuario realiza una búsqueda.
        """
        
        try:
            # Obtenemos la instancia única de la sesión actual
            sesion_actual = Sesion()
            usuario_actual_id = sesion_actual.usuario.IDUsuario
            
            # Verificamos si hay un usuario real conectado.
            # Si el ID es 0 (sesión vacía), asignamos el ID 1 (Admin) por defecto
            # para evitar errores visuales si se accede sin login.
            if usuario_actual_id == 0:
                usuario_actual_id = 1
        except:
            # En caso de cualquier error leyendo la sesión, aseguramos el funcionamiento con el usuario 1
            usuario_actual_id = 1
        
        # --- ACTUALIZADO: DETERMINAMOS SI ES ADMIN ---
        # Buscamos en la base de datos si el Estado del usuario es 'Admin'
        try:
            usuario_info = gestor_usuarios.get_usuario(usuario_actual_id)
            soy_el_admin = (usuario_info.get("Estado") == "Admin")
        except:
            soy_el_admin = False
        # ---------------------------------------

        mensajes = []
        busqueda = "" 

        # Lógica de visualización según la acción del usuario
        if request.method == "POST":
            # CASO BÚSQUEDA: Si el usuario envía el formulario de buscar
            busqueda = request.form.get("busqueda", "")
            # Pedimos al modelo que filtre los mensajes por nombre de usuario
            mensajes = model.filtrar_mensajes_por_usuario(busqueda)
        else:
            # CASO FEED (Carga normal):
            # Pedimos al modelo que traiga las últimas novedades de mis amigos y mías
            mensajes = model.obtener_feed_amigos(usuario_actual_id)

        # Renderizamos la plantilla pasando la lista de mensajes y la variable es_admin
        return render_template("changelog.html", 
                               mensajes=mensajes, 
                               es_admin=soy_el_admin) # <--- ¡AQUÍ ESTÁ LA SOLUCIÓN!

    return bp