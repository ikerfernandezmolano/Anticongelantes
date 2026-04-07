import os
import sqlite3
import sys
import time
import unittest

sys.path.insert(0, os.getcwd())

from app import create_app
from app.config import Config

TEST_DB = "test_pimpam.db"


class TestChatbot(unittest.TestCase):
    """
    Tests automáticos alineados al plan de pruebas:

    3.5.1 General: 1B-1F (1A y 1G manuales)
    3.5.2 /score_team: 2A-2C
    3.5.3 /stats: 3A-3E
    3.5.4 /weaknesses: 4A-4E
    3.5.5 /evolution: 5A-5G
    3.5.6 /compare: 6A-6H
    """

    def setUp(self):
        if os.path.exists(TEST_DB):
            try:
                os.remove(TEST_DB)
            except PermissionError:
                time.sleep(0.1)
                try:
                    os.remove(TEST_DB)
                except Exception:
                    pass

        Config.DB_PATH = TEST_DB

        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        self._ensure_schema_and_seed()

    def tearDown(self):
        self.client = None
        self.app = None
        if os.path.exists(TEST_DB):
            try:
                time.sleep(0.1)
                os.remove(TEST_DB)
            except PermissionError:
                time.sleep(0.2)
                try:
                    os.remove(TEST_DB)
                except Exception:
                    pass

    def _ensure_schema_and_seed(self):
        conn = sqlite3.connect(Config.DB_PATH, timeout=10)
        cur = conn.cursor()

        schema_path = os.path.join(os.getcwd(), "app", "database", "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            cur.executescript(f.read())

        seed_path = os.path.join(os.getcwd(), "app", "database", "seed_chatbot.sql")
        if not os.path.exists(seed_path):
            raise FileNotFoundError("Falta app/database/seed_chatbot.sql (necesario para tests deterministas).")

        with open(seed_path, "r", encoding="utf-8") as f:
            cur.executescript(f.read())

        conn.commit()
        conn.close()

    def _consultar(self, comando: str) -> str:
        res = self.client.post("/chatbot/consultar", json={"comando": comando})
        self.assertEqual(res.status_code, 200)
        data = res.get_json() or {}
        return data.get("respuesta", "")

    # =========================================================
    # 3.5.1 GENERAL (1B-1F)
    # =========================================================

    def test_1B_mensaje_vacio_o_espacios(self):
        self.assertEqual(self._consultar(""), "No se puede enviar.")
        self.assertEqual(self._consultar("   "), "No se puede enviar.")

    def test_1C_inicio_icono_comando_barra_sola(self):
        out = self._consultar("/")
        self.assertIn("Error de sintaxis. Falta el comando. Muestra los comandos posibles.", out)
        self.assertIn("/stats", out)

    def test_1D_comando_inexistente(self):
        self.assertEqual(self._consultar("/comandoInventado bulbasaur"), "Error de sintaxis. Comando no encontrado.")

    def test_1E_comando_sin_icono_barra(self):
        self.assertEqual(self._consultar("stats bulbasaur"), "Error de sintaxis. Falta el icono de inicio de comando '/'.")
        self.assertEqual(self._consultar("hola"), "Error de sintaxis. Falta el icono de inicio de comando '/'.")

    # =========================================================
    # 3.5.2 /score_team {Equipo} (2A-2C)
    # =========================================================

    def test_2C_score_team_falta_argumento(self):
        self.assertEqual(self._consultar("/score_team"), "Error de sintaxis. Falta el argumento.")

    def test_2B_score_team_equipo_inexistente(self):
        self.assertEqual(self._consultar("/score_team equipoInventado123"), "Equipo no encontrado.")

    def test_2A_score_team_equipo_existente(self):
        out = self._consultar("/score_team EquipoDemo")
        self.assertTrue(len(out) > 0)
        self.assertIn("Equipo", out)

    # =========================================================
    # 3.5.3 /stats {Pokemon} (3A-3E)
    # =========================================================

    def test_3E_stats_falta_argumento(self):
        self.assertEqual(self._consultar("/stats"), "Error de sintaxis. Falta el argumento.")

    def test_3D_stats_inexistente(self):
        self.assertEqual(self._consultar("/stats pokemoninventado123"), "Pokemon no encontrado.")

    def test_3A_stats_existente_letras(self):
        out = self._consultar("/stats bulbasaur")
        self.assertIn("bulbasaur", out.lower())
        self.assertTrue(("PS" in out) or ("Atq" in out) or ("Def" in out))

    def test_3B_stats_existente_caracteres_especiales(self):
        out = self._consultar("/stats porygon-z")
        self.assertIn("porygon-z", out.lower())

    def test_3C_stats_existente_espacios_extra(self):
        out = self._consultar("   /stats    bulbasaur    ")
        self.assertIn("bulbasaur", out.lower())

    # =========================================================
    # 3.5.4 /weaknesses {Pokemon} (4A-4E)
    # =========================================================

    def test_4E_weaknesses_falta_argumento(self):
        self.assertEqual(self._consultar("/weaknesses"), "Error de sintaxis. Falta el argumento.")

    def test_4D_weaknesses_inexistente(self):
        self.assertEqual(self._consultar("/weaknesses pokemoninventado123"), "Pokemon no encontrado.")

    def test_4A_weaknesses_existente(self):
        out = self._consultar("/weaknesses bulbasaur")
        self.assertTrue(len(out) > 0)
        self.assertTrue(("Débil" in out) or ("Fuerte" in out) or ("Tipos" in out))

    def test_4B_weaknesses_caracteres_especiales(self):
        out = self._consultar("/weaknesses porygon-z")
        self.assertTrue(len(out) > 0)

    def test_4C_weaknesses_espacios_extra(self):
        out = self._consultar("   /weaknesses    bulbasaur   ")
        self.assertTrue(len(out) > 0)

    # =========================================================
    # 3.5.5 /evolution {Pokemon} (5A-5G)
    # =========================================================

    def test_5G_evolution_falta_argumento(self):
        self.assertEqual(self._consultar("/evolution"), "Error de sintaxis. Falta el argumento.")

    def test_5F_evolution_inexistente(self):
        self.assertEqual(self._consultar("/evolution pokemoninventado123"), "Pokemon no encontrado.")

    def test_5A_evolution_con_evolucion(self):
        out = self._consultar("/evolution bulbasaur")
        self.assertTrue(("Cadena evolutiva" in out) and ("->" in out))

    def test_5B_evolution_caracteres_especiales(self):
        out = self._consultar("/evolution porygon-z")
        self.assertIn("cadena evolutiva", out.lower())

    def test_5C_evolution_sin_evolucion(self):
        out = self._consultar("/evolution pikachu")
        self.assertIn("No tiene cadena evolutiva.", out)

    def test_5D_evolution_con_espacios_extra_y_con_evolucion(self):
        out = self._consultar("   /evolution    bulbasaur   ")
        self.assertTrue(("Cadena evolutiva" in out) and ("->" in out))

    def test_5E_evolution_sin_evolucion_con_espacios_extra(self):
        out = self._consultar("   /evolution    pikachu   ")
        self.assertIn("No tiene cadena evolutiva.", out)

    # =========================================================
    # 3.5.6 /compare {Pokemon1} {Pokemon2} (6A-6H)
    # =========================================================

    def test_6H_compare_faltan_dos_argumentos(self):
        self.assertEqual(self._consultar("/compare"), "Error de sintaxis. Faltan los argumentos.")

    def test_6G_compare_falta_un_argumento(self):
        self.assertEqual(self._consultar("/compare bulbasaur"), "Error de sintaxis. Falta un argumento.")

    def test_6A_compare_ambos_existentes(self):
        out = self._consultar("/compare bulbasaur porygon-z")
        self.assertTrue(len(out) > 0)
        self.assertTrue(("Comparación" in out) or ("Total" in out) or ("Resultado" in out))

    def test_6B_compare_espacios_extra(self):
        out = self._consultar("   /compare    bulbasaur     pikachu   ")
        self.assertTrue(len(out) > 0)

    def test_6C_compare_un_inexistente(self):
        self.assertEqual(self._consultar("/compare bulbasaur pokemoninventado123"), "Pokemon 2 no encontrado.")

    def test_6D_compare_dos_inexistentes(self):
        self.assertEqual(self._consultar("/compare pokemoninventado1 pokemoninventado2"), "Pokémons no encontrados.")

    def test_6E_compare_un_inexistente_con_espacios_extra(self):
        self.assertEqual(self._consultar("   /compare   bulbasaur   pokemoninventado123   "), "Pokemon 2 no encontrado.")

    def test_6F_compare_dos_inexistentes_con_espacios_extra(self):
        self.assertEqual(self._consultar("   /compare   pokemoninventado1   pokemoninventado2   "), "Pokémons no encontrados.")


if __name__ == "__main__":
    unittest.main()
