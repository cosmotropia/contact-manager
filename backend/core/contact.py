"""
Modelo de contacto y estructuras de datos.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Contact(BaseModel):
    """Modelo de contacto con campos esenciales."""
    id: str
    name: str
    email: EmailStr
    phone: str
    company: Optional[str] = None
    position: Optional[str] = None
    linkedin: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    notes: str = ""
    last_contact_date: Optional[str] = None
    relationship_status: str = "active"  # active, inactive, prospect


class ContactCreate(BaseModel):
    """Modelo para crear un nuevo contacto."""
    name: str
    email: EmailStr
    phone: str
    company: Optional[str] = None
    position: Optional[str] = None
    linkedin: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    notes: str = ""


class ContactUpdate(BaseModel):
    """Modelo para actualizar un contacto."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    linkedin: Optional[str] = None
    tags: Optional[list[str]] = None
    notes: Optional[str] = None
    last_contact_date: Optional[str] = None
    relationship_status: Optional[str] = None