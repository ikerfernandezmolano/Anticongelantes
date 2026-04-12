class CarModel:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        return self.db.execSQL("SELECT * FROM Coche")

    def add_car(self, marca, modelo, precio, kilometraje, imagen):
        self.db.executeSQL(
            "INSERT INTO Coche (marca, modelo, precio, kilometraje, imagen) VALUES (?, ?, ?, ?, ?)",
            (marca, modelo, precio, kilometraje, imagen)
        )

    def delete_car(self, idCoche):
        query = "DELETE FROM Coche WHERE idCoche = ?"
        self.db.executeSQL(query, (idCoche,))
