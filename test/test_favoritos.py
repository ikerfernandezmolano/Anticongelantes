import unittest
from app.controller.model.GestorCoches import GestorCoches
from app.database.SGBD import SGBD


class TestFavoritos(unittest.TestCase):
    def setUp(self):
        # Conectamos a la base de datos de test
        self.db = SGBD("test_anticongelantes_coches.db")
        self.gestor = GestorCoches(self.db)

        # Datos de prueba (asegúrate de que el usuario 1 y el coche 1 existen)
        self.id_usuario = 1
        self.id_coche = 1

    def test_1_añadir_favorito(self):
        """Prueba que se puede añadir un favorito"""
        resultado = self.gestor.añadir_favorito(self.id_usuario, self.id_coche)
        # Si devuelve algo que no sea None o error, es que ha funcionado
        self.assertIsNotNone(resultado, "El favorito debería haberse añadido")

    def test_2_listar_favoritos(self):
        """Prueba que el usuario tiene el coche en su lista"""
        lista = self.gestor.get_favoritos_usuario(self.id_usuario)
        # Comprobamos que la lista no está vacía y que contiene el coche
        self.assertTrue(len(lista) > 0, "La lista de favoritos no debería estar vacía")
        self.assertEqual(lista[0]['idCoche'], self.id_coche)

    def test_3_eliminar_favorito(self):
        """Prueba que se puede quitar un favorito"""
        self.gestor.eliminar_favorito(self.id_usuario, self.id_coche)
        lista = self.gestor.get_favoritos_usuario(self.id_usuario)
        # Comprobamos que el coche ya no está (buscando por id)
        encontrado = any(c['idCoche'] == self.id_coche for c in lista)
        self.assertFalse(encontrado, "El coche debería haber sido eliminado de favoritos")


if __name__ == '__main__':
    unittest.main()