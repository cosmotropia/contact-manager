import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.contact_manager import ContactManager

from app.api import router as contacts_router 
import app.api as contacts_module  


def _contact_payload(**overrides):
    payload = {
        "name": "Juan Pérez",
        "email": "juan@example.com",
        "phone": "+56911111111",
        "company": "Acme",
        "position": "Engineer",
        "linkedin": "https://www.linkedin.com/in/juanperez",
        "tags": ["tech", "client"],
        "notes": "Conocido en evento",
    }
    payload.update(overrides)
    return payload


class TestContactsAPI(unittest.TestCase):
    """
    Suite de tests para validar el funcionamiento de la API de contactos.
    Cada test utiliza una base de datos temporal que se limpia automáticamente.
    """
    def setUp(self):
        """
        Configuración inicial antes de cada test.
        Crea una base de datos temporal en memoria para aislar las pruebas.
        """
        # DB temporal por test class
        import tempfile
        from pathlib import Path

        self._tmpdir = tempfile.TemporaryDirectory()
        db_path = Path(self._tmpdir.name) / "contacts.db"

        # Reemplaza el manager global del router por uno apuntando a DB temporal
        contacts_module.manager = ContactManager(db_path=db_path)

        app = FastAPI()
        app.include_router(contacts_router, prefix="/api")
        self.client = TestClient(app)

    def tearDown(self):
        """
        Limpieza después de cada test.
        Elimina la base de datos temporal para evitar contaminación entre tests.
        """
        self._tmpdir.cleanup()

    def test_get_contacts_empty(self):
        """
        Test de obtención de contactos vacíos.
        Este test obtiene todos los contactos y verifica que la lista está vacía.
        """
        res = self.client.get("/api/contacts")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), [])

    def test_create_contact_success(self):
        """
        Test de creación de contacto exitosa.
        Este test crea un contacto y verifica que el contacto fue creado correctamente.
        """
        res = self.client.post("/api/contacts", json=_contact_payload())
        self.assertEqual(res.status_code, 201)

        data = res.json()
        self.assertTrue(isinstance(data["id"], str) and len(data["id"]) > 0)
        self.assertEqual(data["name"], "Juan Pérez")
        self.assertEqual(data["email"], "juan@example.com")
        self.assertEqual(data["phone"], "+56911111111")
        self.assertEqual(data["relationship_status"], "active")
        self.assertIsNone(data["last_contact_date"])

    def test_create_contact_duplicate_email_returns_400(self):
        """
        Test de creación de contacto con email duplicado.
        Este test crea un contacto con un email duplicado y verifica que se lanza una excepción HTTP 400.
        """
        payload = _contact_payload(email="dup@example.com")
        r1 = self.client.post("/api/contacts", json=payload)
        self.assertEqual(r1.status_code, 201)

        r2 = self.client.post("/api/contacts", json=payload)
        self.assertEqual(r2.status_code, 400)
        body = r2.json()
        self.assertIn("detail", body)

    def test_get_contact_by_id_success(self):
        """
        Test de obtención de contacto por id exitosa.
        Este test crea un contacto y luego obtiene el contacto por su id.
        Verifica que el contacto fue creado correctamente y que se puede obtener por su id.
        """
        create = self.client.post("/api/contacts", json=_contact_payload(email="a@a.com"))
        contact_id = create.json()["id"]

        res = self.client.get(f"/api/contacts/{contact_id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["id"], contact_id)

    def test_get_contact_by_id_not_found_404(self):
        """
        Test de obtención de contacto por id no encontrado.
        Este test intenta obtener un contacto que no existe y verifica que se lanza una excepción HTTP 404.
        """
        res = self.client.get("/api/contacts/non-existent-id")
        self.assertEqual(res.status_code, 404)
        self.assertIn("detail", res.json())

    def test_update_contact_success(self):
        """
        Test de actualización de contacto exitosa.
        Este test crea un contacto y luego actualiza sus notas, tags, fecha de último contacto, estado de relación y empresa.
        Verifica que el contacto fue actualizado correctamente.
        """
        create = self.client.post("/api/contacts", json=_contact_payload(email="upd@a.com"))
        contact_id = create.json()["id"]

        update_payload = {
            "notes": "Nuevo note",
            "tags": ["vip", "tech"],
            "last_contact_date": "2026-01-11",
            "relationship_status": "prospect",
            "company": "NewCo",
        }

        res = self.client.put(f"/api/contacts/{contact_id}", json=update_payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["id"], contact_id)
        self.assertEqual(data["notes"], "Nuevo note")
        self.assertEqual(data["tags"], ["vip", "tech"])
        self.assertEqual(data["last_contact_date"], "2026-01-11")
        self.assertEqual(data["relationship_status"], "prospect")
        self.assertEqual(data["company"], "NewCo")

    def test_update_contact_not_found_404(self):
        """
        Test de actualización de contacto no encontrado.
        Este test intenta actualizar un contacto que no existe y verifica que se lanza una excepción HTTP 404.
        """
        res = self.client.put("/api/contacts/does-not-exist", json={"notes": "x"})
        self.assertEqual(res.status_code, 404)

    def test_delete_contact_success(self):
        """
        Test de eliminación de contacto exitosa.
        Este test crea un contacto y luego lo elimina.
        Verifica que el contacto fue eliminado correctamente.
        """
        create = self.client.post("/api/contacts", json=_contact_payload(email="del@a.com"))
        contact_id = create.json()["id"]

        res = self.client.delete(f"/api/contacts/{contact_id}")
        self.assertEqual(res.status_code, 200)
        self.assertIn("message", res.json())

        get_res = self.client.get(f"/api/contacts/{contact_id}")
        self.assertEqual(get_res.status_code, 404)

    def test_delete_contact_not_found_404(self):
        """
        Test de eliminación de contacto no encontrado.
        Este test intenta eliminar un contacto que no existe y verifica que se lanza una excepción HTTP 404.
        """
        res = self.client.delete("/api/contacts/does-not-exist")
        self.assertEqual(res.status_code, 404)

    def test_search_filter_by_name_case_insensitive(self):
        """
        Test de búsqueda de contacto por nombre insensible a mayúsculas y minúsculas.
        Este test crea dos contactos con nombres diferentes y luego filtra por nombre.
        Verifica que el contacto con nombre "María García" fue filtrado correctamente.
        """
        self.client.post("/api/contacts", json=_contact_payload(name="María García", email="maria@a.com", tags=["tech"]))
        self.client.post("/api/contacts", json=_contact_payload(name="Pedro", email="pedro@a.com", tags=["sales"]))

        res = self.client.get("/api/contacts", params={"search": "maría"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "María García")

    def test_filter_by_tag(self):
        """
        Test de filtrado de contactos por tag.
        Este test crea dos contactos con tags diferentes y luego filtra por tag.
        Verifica que el contacto con tag "tech" fue filtrado correctamente.
        """
        self.client.post("/api/contacts", json=_contact_payload(email="t1@a.com", tags=["tech"]))
        self.client.post("/api/contacts", json=_contact_payload(email="t2@a.com", tags=["sales"]))

        res = self.client.get("/api/contacts", params={"search": "tech"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertIn("tech", data[0]["tags"])
    
    if __name__ == '__main__':
        # Ejecutar tests con output verboso para ver los detalles de los tests
        unittest.main(verbosity=2)
