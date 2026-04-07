from datetime import datetime

class ChangelogController:
    """
    Controlador que encapsula la lógica de acceso a datos para el módulo de Changelog.
    Gestiona la inserción, recuperación y filtrado de los mensajes de actividad de los usuarios.
    """

    def __init__(self, db):
        # Constructor que recibe la instancia del gestor de base de datos
        self.db = db

    def agregar_mensaje(self, id_usuario, texto):
        """
        Registra un nuevo evento en la tabla 'Mensaje' asociado a un usuario.
        Se utiliza para auditar acciones como crear equipos o añadir Pokémon.
        """
        # Generamos la marca de tiempo actual en formato SQL estándar
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # Ejecutamos la inserción parametrizada para prevenir inyección SQL
            self.db.insert(
                "INSERT INTO Mensaje (Fecha, IDUsuario, Texto) VALUES (?, ?, ?)",
                [fecha_actual, id_usuario, texto]
            )
            return True
        except Exception as e:
            # Captura de errores durante la inserción para evitar paradas del servidor
            print(f"[ERROR - ChangelogController] Fallo al insertar mensaje: {e}")
            return False

    def obtener_feed_amigos(self, id_usuario_actual):
        """
        Recupera el listado de actividad para el 'feed' principal.
        La consulta devuelve los mensajes del propio usuario y de las personas a las que sigue.
        """
        
        # Consulta SQL que realiza las siguientes operaciones:
        # 1. JOIN con la tabla Usuario para obtener el nombre del autor.
        # 2. LEFT JOIN con la tabla Especie para obtener el sprite del Pokémon favorito (si existe).
        # 3. Subconsulta en el WHERE para filtrar solo usuarios que se encuentran en la tabla 'Seguidor'.
        sql = """
            SELECT m.Fecha, m.Texto, u.Nombre as NombreUsuario, e.Sprite
            FROM Mensaje m
            JOIN Usuario u ON m.IDUsuario = u.IDUsuario
            LEFT JOIN Especie e ON u.IDFavorito = e.PokedexID
            WHERE m.IDUsuario IN (
                SELECT IDUsuarioSeguido 
                FROM Seguidor 
                WHERE IDUsuarioSeguidor = ?
            ) OR m.IDUsuario = ?
            ORDER BY m.Fecha DESC
        """
        
        # Se pasa el ID dos veces: una para la subconsulta de amigos y otra para incluir al propio usuario
        return self.db.select(sql, [id_usuario_actual, id_usuario_actual])

    def filtrar_mensajes_por_usuario(self, nombre_usuario):
        """
        Realiza una búsqueda de mensajes filtrando por nombre de usuario.
        Utiliza el operador LIKE para permitir coincidencias parciales.
        """
        sql = """
            SELECT m.Fecha, m.Texto, u.Nombre as NombreUsuario, e.Sprite
            FROM Mensaje m
            JOIN Usuario u ON m.IDUsuario = u.IDUsuario
            LEFT JOIN Especie e ON u.IDFavorito = e.PokedexID
            WHERE u.Nombre LIKE ?
            ORDER BY m.Fecha DESC
        """
        # Añadimos los comodines % para la búsqueda parcial
        return self.db.select(sql, [f"%{nombre_usuario}%"])

    def esta_vacio(self):
        """
        Método auxiliar para verificar si existen registros en el historial.
        Útil para gestionar estados iniciales de la interfaz gráfica.
        """
        rows = self.db.select("SELECT count(*) as total FROM Mensaje")
        return rows[0]["total"] == 0