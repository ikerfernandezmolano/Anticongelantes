from flask import Blueprint, render_template, redirect, url_for, request
# Importamos los modelos necesarios para la gestión de datos
from app.controller.model.GestorEquipos import GestorEquipos
from app.controller.model.changelog_controller import ChangelogController
# Importamos la clase de Sesión personalizada (del código de tu amiga)
from app.controller.model.Sesion import Sesion 

def equipos_blueprint(db):
    # Se crea el blueprint de equipos para gestionar las rutas
    bp = Blueprint("equipos", __name__)
    
    # Inicializamos el gestor de equipos
    gestor = GestorEquipos(db)
    
    # Intentamos cargar el controlador del changelog para las notificaciones
    try:
        changelog = ChangelogController(db)
    except Exception as e:
        print(f"Error al cargar Changelog: {e}")

    def obtener_id_usuario():
        """
        Método para obtener el ID del usuario actual usando la clase Sesion personalizada.
        Si la sesión está vacía o falla, devuelve 1 (Admin) por seguridad.
        """
        try:
            sesion_actual = Sesion()
            # Accedemos a la propiedad usuario de la clase Sesion
            id_actual = sesion_actual.usuario.IDUsuario
            
            if id_actual and id_actual != 0:
                return id_actual
            
            # Si el ID es 0, asumimos Admin para evitar errores en pruebas
            return 1 
        except:
            return 1


    @bp.route("/equipos")
    def cargar_equipos():
        """
        Carga la página principal de equipos.
        Muestra la lista de equipos del usuario y el contenido del equipo activo.
        """
        # Obtenemos el usuario conectado
        idUsuario = obtener_id_usuario()
        
        # Verificamos si hay un equipo seleccionado en la URL
        equipo_activo_id = request.args.get("equipo_id", type=int)
        
        # Recuperamos los equipos de la base de datos
        equipos_db = gestor.getEquiposUsuario(idUsuario)
        equipos = []

        # Formateamos los equipos y añadimos sus pokémons
        for fila in equipos_db:
            equipo = dict(fila)
            equipo["pokemon"] = gestor.getPokemonEquipo(equipo["IDEquipo"])
            equipos.append(equipo)

        # Si el usuario no tiene equipos, mostramos la página vacía
        if not equipos:
            return render_template("equipos.html", equipos=[], equipo_activo=None, pokedex=[])

        # Determinamos cuál es el equipo activo para mostrarlo en el centro
        if equipo_activo_id:
            # Buscamos el equipo por ID
            equipo_activo = next((e for e in equipos if e["IDEquipo"] == equipo_activo_id), equipos[0])
        else:
            # Por defecto mostramos el primero
            equipo_activo = equipos[0]

        # Cargamos la Pokédex para poder elegir Pokémons
        pokedex = gestor.getPokedex()
        
        return render_template("equipos.html", equipos=equipos, equipo_activo=equipo_activo, pokedex=pokedex)

    @bp.route("/equipos/crear", methods=["POST"])
    def create_equipo():
        """
        Crea un nuevo equipo con el nombre proporcionado por el formulario.
        """
        idUsuario = obtener_id_usuario()
        nombre = request.form["nombre"]
        
        # Guardamos el nuevo equipo en la base de datos
        idEquipo = gestor.saveNewEquipo(idUsuario, nombre)

    
        # Registramos que el usuario ha creado un equipo nuevo
        try:
            mensaje = f"ha creado un nuevo equipo de combate: {nombre}."
            changelog.agregar_mensaje(idUsuario, mensaje)
        except Exception as e:
            print(f"Error registrando creación de equipo: {e}")
       

        return redirect(url_for("equipos.cargar_equipos", equipo_id=idEquipo))

    @bp.route("/equipos/eliminar/<int:idEquipo>", methods=["POST"])
    def deleteEquipo(idEquipo):
        """
        Elimina un equipo completo.
        """
        # 1. Recuperamos el nombre del equipo ANTES de borrarlo para el mensaje
        nombre_equipo = "un equipo"
        try:
            resultado = db.select("SELECT Nombre FROM Equipo WHERE IDEquipo = ?", [idEquipo])
            if resultado:
                nombre_equipo = resultado[0]["Nombre"]
        except:
            pass

        # 2. Ejecutamos el borrado
        gestor.deleteEquipo(idEquipo)
        
        
        try:
            idUsuario = obtener_id_usuario()
            mensaje = f"ha eliminado el equipo '{nombre_equipo}'."
            changelog.agregar_mensaje(idUsuario, mensaje)
        except Exception as e:
            print(f"Error registrando eliminación de equipo: {e}")
       

        return redirect(url_for("equipos.cargar_equipos"))

    @bp.route("/equipos/<int:idEquipo>/modificar_nombre", methods=["POST"])
    def modifyName(idEquipo):
        """
        Modifica el nombre de un equipo existente.
        """
        nombre_nuevo = request.form["nombre"]
        gestor.saveNewNombre(idEquipo, nombre_nuevo)
        
      
        try:
            idUsuario = obtener_id_usuario()
            mensaje = f"ha cambiado el nombre de su equipo a '{nombre_nuevo}'."
            changelog.agregar_mensaje(idUsuario, mensaje)
        except Exception as e:
            print(f"Error registrando cambio de nombre: {e}")

        return redirect(url_for("equipos.cargar_equipos", equipo_id=idEquipo))

    @bp.route("/equipos/<int:idEquipo>/pokemon", methods=["POST"])
    def OpcionesModificarPokemon(idEquipo):
        """
        Gestiona la adición, reemplazo o eliminación de un Pokémon en un slot del equipo.
        """
        slot = int(request.form["slot"])
        idPokemon = request.form.get("idPokemon")
        idUsuario = obtener_id_usuario()

       
        nombre_equipo = "su equipo"
        try:
            res_equipo = db.select("SELECT Nombre FROM Equipo WHERE IDEquipo = ?", [idEquipo])
            if res_equipo:
                nombre_equipo = res_equipo[0]["Nombre"]
        except:
            pass
        

        if idPokemon == "__empty__":
            # === CASO 1: ELIMINAR POKÉMON ===
            # Si el ID es __empty__, borramos el Pokémon de esa posición.
            
            # A) Averiguamos el nombre del Pokémon QUE VAMOS A BORRAR (ej: Pikachu)
            nombre_borrado = "un Pokémon"
            try:
                # Hacemos un JOIN para ver qué bicho hay en ese slot antes de cargárnoslo
                sql_buscar = """
                    SELECT E.Nombre 
                    FROM Especie E
                    JOIN EquipoPokemon EP ON E.PokedexID = EP.PokedexID
                    WHERE EP.IDEquipo = ? AND EP.Slot = ?
                """
                resultado = db.select(sql_buscar, [idEquipo, slot])
                if resultado:
                    nombre_borrado = resultado[0]["Nombre"]
            except Exception as e:
                print(f" Error buscando nombre del pokemon a borrar: {e}")

            # B) Borramos el Pokémon
            gestor.deleteEquipo(idEquipo, slot)

            # C) Notificamos al Changelog
            try:
                mensaje = f"ha eliminado a {nombre_borrado} del equipo '{nombre_equipo}'."
                changelog.agregar_mensaje(idUsuario, mensaje)
            except Exception as e:
                print(f" Error registrando borrado de pokemon: {e}")

        else:
            # === CASO 2: AÑADIR O REEMPLAZAR POKÉMON ===
            # Si hay ID, reemplazamos o añadimos el Pokémon.
            
            # A) Realizamos la inserción/actualización en la BD
            gestor.reemplazarPokemon(idEquipo, slot, int(idPokemon))

            # B) Notificamos al Changelog buscando el nombre del NUEVO Pokémon
            try:
                # Buscamos el nombre del Pokémon en la tabla Especie usando su ID
                resultado = db.select("SELECT Nombre FROM Especie WHERE PokedexID = ?", [int(idPokemon)])
                
                if resultado:
                    nombre_pokemon = resultado[0]["Nombre"]
                    # Creamos el mensaje específico (Ej: "ha añadido a Charizard al equipo 'Fuego'")
                    mensaje = f"ha añadido a {nombre_pokemon} al equipo '{nombre_equipo}'."
                    changelog.agregar_mensaje(idUsuario, mensaje)
                else:
                    print(f" No se encontró el nombre para el Pokémon ID {idPokemon}")
            except Exception as e:
                print(f"Error registrando nuevo pokemon: {e}")

        return redirect(url_for("equipos.cargar_equipos", equipo_id=idEquipo))

    return bp