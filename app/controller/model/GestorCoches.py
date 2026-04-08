class GestorCoches:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        # Esta consulta lee de la tabla que subiste a Git
        return self.db.select("SELECT * FROM Coche")