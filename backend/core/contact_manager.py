"""
ContactManager - Lógica de negocio para el manejo de contactos.

Responsabilidades:
- Manejo del ciclo de vida de los contactos (CRUD)
- Aplicar reglas de negocio
- Mantenerse independiente del framework
- Gestión de datos en memoria usando listas y diccionarios
- Persistencia local usando SQLite
"""

import sqlite3
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from core.contact import Contact, ContactCreate, ContactUpdate


# ==========================================
# Exceptions
# ==========================================

class DuplicateContactError(Exception):
    """Lanzada cuando se intenta crear un contacto duplicado."""
    pass


class ContactNotFoundError(Exception):
    """Lanzada cuando un contacto no es encontrado."""
    pass


# ==========================================
# ContactManager
# ==========================================

class ContactManager:
    """
    Maneja las operaciones CRUD de los contactos.

    Utiliza:
    - Diccionarios para acceso rápido por ID
    - Listas para iteración y filtrado
    - SQLite como persistencia local
    """

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "db" / "contacts.db"

        self.db_path = db_path

        # In-memory structures
        self._contacts_by_id: Dict[str, Contact] = {}
        self._contacts_list: List[Contact] = []

        self._init_db()
        self._load_contacts_into_memory()

    # ==========================================
    # DB helpers
    # ==========================================

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            company TEXT,
            position TEXT,
            linkedin TEXT,
            tags TEXT,
            notes TEXT,
            last_contact_date TEXT,
            relationship_status TEXT DEFAULT 'active'
        )
        """)

        conn.commit()
        conn.close()

    def _load_contacts_into_memory(self):
        """Carga todos los contactos desde SQLite a memoria."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM contacts")
        rows = cursor.fetchall()
        conn.close()

        self._contacts_by_id.clear()
        self._contacts_list.clear()

        for row in rows:
            contact = self._row_to_contact(row)
            self._contacts_by_id[contact.id] = contact
            self._contacts_list.append(contact)

    # ==========================================
    # CREATE
    # ==========================================

    def add_contact(self, data: ContactCreate) -> Contact:
        """Crea y almacena un nuevo contacto."""
        if self._email_exists(data.email):
            raise DuplicateContactError("El contacto con este email ya existe.")

        contact = Contact(
            id=str(uuid.uuid4()),
            **data.model_dump()
        )

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO contacts (
            id, name, email, phone, company, position,
            linkedin, tags, notes, last_contact_date, relationship_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contact.id,
            contact.name,
            contact.email,
            contact.phone,
            contact.company,
            contact.position,
            contact.linkedin,
            ",".join(contact.tags),
            contact.notes,
            contact.last_contact_date,
            contact.relationship_status
        ))

        conn.commit()
        conn.close()

        # Update in-memory structures
        self._contacts_by_id[contact.id] = contact
        self._contacts_list.append(contact)

        return contact

    # ==========================================
    # READ
    # ==========================================

    def get(self, contact_id: str) -> Contact:
        """Obtiene un contacto por su ID."""
        contact = self._contacts_by_id.get(contact_id)
        if not contact:
            raise ContactNotFoundError("El contacto no existe.")
        return contact

    def get_all(
        self,
        tag: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Contact]:
        """Obtiene todos los contactos con filtrado opcional."""
        results = self._contacts_list

        if search:
            search_lower = search.lower()
            results = [
                c for c in results
                if search_lower in c.name.lower()
                or search_lower in c.phone
                or search_lower in c.email.lower()
                or search_lower in (c.company or "").lower()
                or search_lower in (c.position or "").lower()
                or search_lower in (c.linkedin or "").lower()
                or search_lower in c.notes.lower()
                or any(search_lower in t.lower() for t in c.tags) # Check if any tag contains the search
            ]

        return results

    # ==========================================
    # UPDATE
    # ==========================================

    def update(self, contact_id: str, data: ContactUpdate) -> Contact:
        """Actualiza un contacto existente."""
        contact = self.get(contact_id)

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return contact

        for field, value in update_data.items():
            setattr(contact, field, value)

        conn = self._get_connection()
        cursor = conn.cursor()

        fields = []
        values = []

        for field, value in update_data.items():
            if field == "tags" and value is not None:
                value = ",".join(value)
            fields.append(f"{field} = ?")
            values.append(value)

        values.append(contact_id)

        cursor.execute(
            f"UPDATE contacts SET {', '.join(fields)} WHERE id = ?",
            values
        )

        conn.commit()
        conn.close()

        return contact

    # ==========================================
    # DELETE
    # ==========================================

    def delete(self, contact_id: str) -> None:
        """Elimina un contacto."""
        contact = self._contacts_by_id.pop(contact_id, None)
        if not contact:
            raise ContactNotFoundError("El contacto no existe.")

        self._contacts_list = [
            c for c in self._contacts_list if c.id != contact_id
        ]

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        conn.commit()
        conn.close()

    # ==========================================
    # INTERNAL HELPERS
    # ==========================================

    def _email_exists(self, email: str) -> bool:
        return any(c.email == email for c in self._contacts_list)

    def _row_to_contact(self, row) -> Contact:
        return Contact(
            id=row[0],
            name=row[1],
            email=row[2],
            phone=row[3],
            company=row[4],
            position=row[5],
            linkedin=row[6],
            tags=row[7].split(",") if row[7] else [],
            notes=row[8] or "",
            last_contact_date=row[9],
            relationship_status=row[10] or "active"
        )

