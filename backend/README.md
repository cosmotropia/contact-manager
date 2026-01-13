# Backend – Contact Manager API

Este directorio contiene el backend del sistema de gestión de contactos.
Está implementado en **Python con FastAPI** y expone una **API REST** que
centraliza la lógica de negocio y la persistencia de datos.

El backend es consumido tanto por el frontend (Next.js) como por el agente
conversacional, actuando como **única fuente de verdad** del sistema.

---

## 🧩 Responsabilidades

- Exponer endpoints REST para operaciones CRUD de contactos  
- Validar datos de entrada con **Pydantic**  
- Encapsular la lógica de negocio en una capa dedicada  
- Persistir información utilizando **SQLite**  
- Proveer documentación automática vía **OpenAPI / Swagger**

---

## 🏗️ Estructura del Proyecto

```text
backend/
├── app/
│   ├── api.py              # Definición de endpoints REST
│   └── main.py             # Punto de entrada FastAPI
├── core/
│   ├── contact.py          # Modelos Pydantic
│   └── contact_manager.py # Lógica de negocio y acceso a SQLite
├── db/
│   └── contacts.db         # Base de datos SQLite
├── tests/
│   ├── test_api.py
│   └── test_contact_manager.py
├── requirements.txt
└── README.md
