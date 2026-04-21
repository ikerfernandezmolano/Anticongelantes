class GestorCoches:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        # Esta consulta lee de la tabla que subiste a Git
        return self.db.select("SELECT * FROM Coche")

    def añadir_favorito(self, id_usuario, id_coche):
        query = "INSERT OR IGNORE INTO Favorito (IDUsuario, idCoche) VALUES (?, ?)"
        return self.db.executeSQL(query, (id_usuario, id_coche))

    def get_favoritos_usuario(self, id_usuario):
        # Esta consulta busca los datos del coche, pero solo de los que están en la tabla Favorito para ESE usuario
        query = """
            SELECT C.* FROM Coche C
            JOIN Favorito F ON C.idCoche = F.idCoche
            WHERE F.IDUsuario = ?
        """
        return self.db.select(query, (id_usuario,))

    def eliminar_favorito(self, id_usuario, id_coche):
        query = "DELETE FROM Favorito WHERE IDUsuario = ? AND idCoche = ?"
        # Usamos executeSQL como antes
        return self.db.executeSQL(query, (id_usuario, id_coche))