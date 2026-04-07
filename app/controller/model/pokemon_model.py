#ESTO LO HAGO PERO ESTA MAL
class PokemonModel:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        return self.db.select(
            """
            SELECT p.IDPokemon, p.Nombre, e.Sprite
            FROM Pokemon p
            JOIN Especie e ON e.PokedexID = p.IDEspecie
            """
        )
