import sqlite3

class GestorEquipos:

    def __init__(self, db):
        # Guardamos la referencia a la base de datos
        self.db = db

    def getEquiposUsuario(self, idUsuario):
        # Devuelve todos los equipos asociados a un usuario
        return self.db.select(
            "SELECT IDEquipo, Nombre FROM Equipo WHERE IDUsuario = ?",
            [idUsuario]
        )

    def getPokemonEquipo(self, idEquipo):
        # Obtiene los Pokémon de un equipo junto con su slot y sprite
        return self.db.select(
            """
            SELECT
                rep.Slot,
                p.IDPokemon,
                p.Nombre,
                e.Sprite AS Sprite
            FROM REquipoPokemon rep
            JOIN Pokemon p ON p.IDPokemon = rep.IDPokemon
            JOIN Especie e ON e.PokedexID = p.IDEspecie
            WHERE rep.IDEquipo = ?
            ORDER BY rep.Slot
            """,
            (idEquipo,)
        )

    def getPokedex(self):
        # Devuelve los Pokémon capturados que pueden añadirse a un equipo
        return self.db.select(
            """
            SELECT
                p.IDPokemon,
                p.Nombre
            FROM Pokemon p
            """
        )

    def saveNewEquipo(self, idUsuario, nombre):
        # Comprueba que el usuario no tenga ya un equipo con ese nombre
        equipos = self.getEquiposUsuario(idUsuario)
        if any(e['Nombre'] == nombre for e in equipos):
            return None

        # Inserta un nuevo equipo en la base de datos
        try:
            return self.db.insert(
                "INSERT INTO Equipo (Nombre, IDUsuario) VALUES (?, ?)",
                (nombre, idUsuario)
            )
        except sqlite3.IntegrityError:
            return None

    def insertPokemon(self, idEquipo, idPokemon, slot):
        # Inserta un Pokémon en un slot concreto del equipo
        try:
            self.db.insert(
                "INSERT INTO REquipoPokemon (IDEquipo, IDPokemon, Slot) VALUES (?, ?, ?)",
                (idEquipo, idPokemon, slot)
            )
        except sqlite3.IntegrityError:
            # Evita errores por restricciones de la base de datos
            return

    def deletePokemon(self, idEquipo, slot):
        # Elimina el Pokémon de un slot concreto del equipo
        self.db.delete(
            """
            DELETE FROM REquipoPokemon
            WHERE IDEquipo = ? AND Slot = ?
            """,
            (idEquipo, slot)
        )

    def deleteEquipo(self, idEquipo, slot=None):
        # Si se indica slot, elimina solo ese Pokémon del equipo
        if slot is not None:
            self.db.delete(
                "DELETE FROM REquipoPokemon WHERE IDEquipo = ? AND Slot = ?",
                (idEquipo, slot)
            )
        else:
            # Si no hay slot, elimina el equipo completo y sus relaciones
            self.db.delete(
                "DELETE FROM REquipoPokemon WHERE IDEquipo = ?",
                (idEquipo,)
            )
            self.db.delete(
                "DELETE FROM Equipo WHERE IDEquipo = ?",
                (idEquipo,)
            )

    def reemplazarPokemon(self, idEquipo, slot, idPokemon):
        # Reemplaza el Pokémon de un slot por otro
        pokemons = self.getPokemonEquipo(idEquipo)

        # Primero se vacía el slot
        self.deletePokemon(idEquipo, slot)

        # Controla que el equipo no tenga más de 6 Pokémon
        if len(pokemons) >= 6 and slot >= len(pokemons):
            return

        # Inserta el nuevo Pokémon en el slot
        self.insertPokemon(idEquipo, idPokemon, slot)

    def saveNewNombre(self, idEquipo, nuevoNombre):
        # Comprueba que el equipo exista
        equipo_actual = self.db.select(
            "SELECT IDUsuario FROM Equipo WHERE IDEquipo = ?",
            (idEquipo,)
        )
        if not equipo_actual:
            return False

        idUsuario = equipo_actual[0]['IDUsuario']

        # Comprueba que no exista otro equipo con el mismo nombre para el usuario
        existe = self.db.select(
            """
            SELECT IDEquipo
            FROM Equipo
            WHERE LOWER(Nombre) = LOWER(?)
              AND IDUsuario = ?
              AND IDEquipo != ?
            """,
            (nuevoNombre, idUsuario, idEquipo)
        )

        if existe:
            return False

        # Actualiza el nombre del equipo
        self.db.update(
            "UPDATE Equipo SET Nombre = ? WHERE IDEquipo = ?",
            (nuevoNombre, idEquipo)
        )
        return True

    def getEquipoPorNombre(self, nombre_equipo: str):
        # Busca un equipo por nombre (ignorando mayúsculas/minúsculas)
        rows = self.db.select(
            "SELECT IDEquipo, Nombre FROM Equipo WHERE LOWER(Nombre) = LOWER(?) LIMIT 1",
            [nombre_equipo]
        )
        return dict(rows[0]) if rows else None
