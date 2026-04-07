import os
from pokebase import cache
import pokebase as pb

os.environ["POKEBASE_DB"] = "dumb"

# Delete old cache to avoid dbm.gnu issues
if os.path.exists(cache.API_CACHE):
    os.remove(cache.API_CACHE)

class GestorEspecies:
    def __init__(self, db):
        self.db = db

    def initialize(self, limit=10):
        # Carga en la base de datos los pokemons de la API
        import os, requests
        res = self.db.execSQL("SELECT COUNT(*) AS TOTAL FROM Especie")
        # Carpeta pública
        sprites_dir = "app/static/sprites"
        os.makedirs(sprites_dir, exist_ok=True) 
        
        if res and res[0]["TOTAL"]==0:
            for i in range(1, limit):
                p = pb.pokemon(i)
                e = pb.pokemon_species(i)
                self.db.executeSQL("INSERT INTO Especie VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",[p.id,p.name,e.is_legendary, e.generation.url.rstrip('/').split('/')[-1],p.sprites.front_default,"Prueba","Prueba",p.height,p.weight,"Prueba",1,0])
        
                sprite_url = p.sprites.front_default
                filepath = os.path.join(sprites_dir, f"pokemon_{p.id}.png")

                # Descargar solo si no existe
                if sprite_url and sprite_url.startswith("http") and not os.path.exists(filepath):
                    response = requests.get(sprite_url)
                    response.raise_for_status()
                    with open(filepath, "wb") as f:
                        f.write(response.content)

    def get_all(self):
        # Devuelve una lista con todos los pokemons y sus atributos
        rows = self.db.execSQL("SELECT * FROM Especie")
        return [dict(row) for row in rows]

    def getPokemonPorNombre(self, pNombre: str):
        rows = self.db.execSQL(
            sql="SELECT * FROM Pokemon WHERE LOWER(Nombre) = LOWER(?) LIMIT 1",
            parameters=[pNombre],
        )
        if not rows:
            return None
        return dict(rows[0])

    def getEspeciePorNombre(self, pNombre: str):
        rows = self.db.execSQL(
            sql="SELECT * FROM Especie WHERE LOWER(Nombre) = LOWER(?) LIMIT 1",
            parameters=[pNombre],
        )
        return dict(rows[0]) if rows else None

    def getTiposPorNombreEspecie(self, pNombreEspecie: str):
        rows = self.db.execSQL(
            sql="SELECT t.Nombre AS Tipo FROM Especie e JOIN REspecieTipo ret ON ret.PokedexID = e.PokedexID JOIN Tipo t ON t.Nombre = ret.NombreTipo WHERE LOWER(e.Nombre) = LOWER(?)",
            parameters=[pNombreEspecie],
        )
        return [r["Tipo"] for r in rows] if rows else []

    def getDebilidadesYFortalezasPorEspecie(self, nombre_especie: str):
        e = self.getEspeciePorNombre(nombre_especie)
        if not e:
            return None

        tipos = self.getTiposPorNombreEspecie(nombre_especie)

        debiles = set()
        fuertes = set()

        for t in tipos:
            rows = self.db.execSQL(
                "SELECT NombreTipoFuerte AS T FROM Debil WHERE NombreTipoDebil = ?",
                [t],
            )
            for r in rows:
                debiles.add(r["T"])

            rows = self.db.execSQL(
                "SELECT NombreTipoDebil AS T FROM Debil WHERE NombreTipoFuerte = ?",
                [t],
            )
            for r in rows:
                fuertes.add(r["T"])

        return {
            "tipos": tipos,
            "debilidades": sorted(debiles),
            "fortalezas": sorted(fuertes),
        }

    def getCadenaEvolutivaPorEspecie(self, nombre_especie: str):
        e = self.getEspeciePorNombre(nombre_especie)
        if not e:
            return None

        if not e.get("TieneEvolucion"):
            return []

        especie_id = e["PokedexID"]

        # subir hacia preevolución (con protección anti-bucle)
        ids = []
        actual = especie_id
        visitados = set()

        while True:
            if actual in visitados:
                break
            visitados.add(actual)
            ids.append(actual)

            prev = self.db.execSQL(
                "SELECT Prevolucion FROM Especie WHERE PokedexID = ? LIMIT 1",
                [actual],
            )
            if not prev:
                break

            pre = prev[0]["Prevolucion"]
            if pre is None or pre == actual:
                break

            actual = pre

        ids = list(reversed(ids))

        # bajar hacia evoluciones (si hay varias ramas, cogemos la primera)
        actual = especie_id
        visitados = set(ids)

        while True:
            nxt = self.db.execSQL(
                "SELECT PokedexID FROM Especie WHERE Prevolucion = ? LIMIT 1",
                [actual],
            )
            if not nxt:
                break

            actual = nxt[0]["PokedexID"]
            if actual in visitados:
                break
            visitados.add(actual)
            ids.append(actual)

        # ids -> nombres
        nombres = []
        for pid in ids:
            r = self.db.execSQL(
                "SELECT Nombre FROM Especie WHERE PokedexID = ? LIMIT 1",
                [pid],
            )
            if r:
                nombres.append(r[0]["Nombre"])

        return [] if len(nombres) <= 1 else nombres
