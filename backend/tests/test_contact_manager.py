import unittest
from pathlib import Path
import tempfile

from core.contact_manager import ContactManager, DuplicateContactError, ContactNotFoundError
from core.contact import ContactCreate, ContactUpdate


class TestContactManager(unittest.TestCase):
    """
    Suite de tests para validar el funcionamiento del ContactManager.
    Cada test utiliza una base de datos temporal que se limpia automáticamente.
    """
    def setUp(self):
        """
        Configuración inicial antes de cada test.
        Crea una base de datos temporal en memoria para aislar las pruebas.
        """
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "contacts.db"
        self.m = ContactManager(db_path=self.db_path)

    def tearDown(self):
        """
        Limpieza después de cada test.
        Elimina la base de datos temporal para evitar contaminación entre tests.
        """
        self._tmpdir.cleanup()

    def test_add_and_get_all(self):
        """
        Test de adición y obtención de todos los contactos.
        Este test agrega un contacto y luego obtiene todos los contactos.
        Verifica que el contacto fue agregado y que el número de contactos es 1.
        También verifica que el id del contacto agregado es el mismo que el id del contacto obtenido.
        """
        c = self.m.add_contact(ContactCreate(
            name="Juan",
            email="juan@a.com",
            phone="123",
            tags=["tech"],
            notes="hola"
        ))
        all_contacts = self.m.get_all()
        self.assertEqual(len(all_contacts), 1)
        self.assertEqual(all_contacts[0].id, c.id)

    def test_duplicate_email(self):
        """
        Test de duplicado de email.
        Este test agrega un contacto con un email duplicado y verifica que se lanza una excepción DuplicateContactError.
        """
        self.m.add_contact(ContactCreate(name="A", email="dup@a.com", phone="1"))
        with self.assertRaises(DuplicateContactError):
            self.m.add_contact(ContactCreate(name="B", email="dup@a.com", phone="2"))

    def test_get_not_found(self):
        """
        Test de obtención de un contacto que no existe.
        Este test intenta obtener un contacto que no existe y verifica que se lanza una excepción ContactNotFoundError.
        """
        with self.assertRaises(ContactNotFoundError):
            self.m.get("nope")

    def test_update(self):
        """
        Test de actualización de un contacto.
        Este test agrega un contacto y luego actualiza sus notas y tags.
        Verifica que las notas y tags fueron actualizadas correctamente.
        """
        c = self.m.add_contact(ContactCreate(name="A", email="a@a.com", phone="1", tags=["x"]))
        updated = self.m.update(c.id, ContactUpdate(notes="nuevo", tags=["vip", "x"]))
        self.assertEqual(updated.notes, "nuevo")
        self.assertEqual(updated.tags, ["vip", "x"])

    def test_delete(self):
        """
        Test de eliminación de un contacto.
        Este test agrega un contacto y luego lo elimina.
        Verifica que el contacto fue eliminado correctamente.
        """
        c = self.m.add_contact(ContactCreate(name="A", email="a@a.com", phone="1"))
        self.m.delete(c.id)
        with self.assertRaises(ContactNotFoundError):
            self.m.get(c.id)

    def test_filters(self):
        """
        Test de filtros de búsqueda.
        Este test agrega dos contactos con tags diferentes y luego filtra.
        Verifica que el contacto con tag "tech" fue filtrado correctamente.
        """
        self.m.add_contact(ContactCreate(name="María", email="m@a.com", phone="111", tags=["tech"]))
        self.m.add_contact(ContactCreate(name="Pedro", email="p@a.com", phone="222", tags=["sales"]))

        by_search = self.m.get_all(search="pedro")
        self.assertEqual(len(by_search), 1)
        self.assertEqual(by_search[0].email, "p@a.com")

        by_search_2 = self.m.get_all(search="tech")
        self.assertEqual(len(by_search), 1)
        self.assertEqual(by_search_2[0].name, "María")
    
if __name__ == '__main__':
    # Ejecutar tests con output verboso para ver los detalles de los tests
    unittest.main(verbosity=2)
