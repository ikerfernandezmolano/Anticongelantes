import unittest
import sys
import os

# Esto es para que Python encuentre la carpeta 'app' correctamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.controller.model.GestorCoches import GestorCoches
from app.database.SGBD import SGBD


class TestFavoritos(unittest.TestCase):
    def setUp(self):
        # Corregido: SGBD() sin argumentos para evitar el TypeError
        self.db = SGBD()
        self.gestor = GestorCoches(self.db)

        # Asegúrate de que el usuario 1 y el coche 1 existan en tu DB
        self.id_usuario = 1
        self.id_coche = 1

    def test_1_añadir_favorito(self):
        """Prueba que se puede añadir un favorito"""
        # Ejecutamos la acción
        self.gestor.añadir_favorito(self.id_usuario, self.id_coche)
        # En lugar de mirar el resultado de la función, miramos si el coche está en la DB
        lista = self.gestor.get_favoritos_usuario(self.id_usuario)
        encontrado = any(c['idCoche'] == self.id_coche for c in lista)
        self.assertTrue(encontrado, "El coche debería aparecer en la lista de favoritos")

    def test_2_listar_favoritos(self):
        """Prueba que el usuario tiene el coche en su lista"""
        lista = self.gestor.get_favoritos_usuario(self.id_usuario)
        self.assertTrue(len(lista) > 0, "La lista no debería estar vacía")
        # Comprobamos que el ID coincide
        self.assertEqual(lista[0]['idCoche'], self.id_coche)

    def test_3_eliminar_favorito(self):
        """Prueba que se puede quitar un favorito"""
        self.gestor.eliminar_favorito(self.id_usuario, self.id_coche)
        lista = self.gestor.get_favoritos_usuario(self.id_usuario)
        # Comprobamos que el coche ya no esté en la lista
        encontrado = any(c['idCoche'] == self.id_coche for c in lista)
        self.assertFalse(encontrado, "El coche debería haber sido eliminado")


if __name__ == '__main__':
    unittest.main()