"""
FastAPI endpoints for contact management.
Translates domain errors into HTTP responses.
"""
from fastapi import APIRouter, HTTPException, status

from core.contact import Contact, ContactCreate, ContactUpdate
from core.contact_manager import (
    ContactManager,
    DuplicateContactError,
    ContactNotFoundError,
)

router = APIRouter()
manager = ContactManager()


@router.post(
    "/contacts",
    response_model=Contact,
    status_code=status.HTTP_201_CREATED,
)
def create_contact(contact: ContactCreate):
    """Create a new contact."""
    try:
        return manager.add_contact(contact)
    except DuplicateContactError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/contacts", response_model=list[Contact])
def get_contacts(
    tag: str | None = None,
    search: str | None = None,
):
    """Get all contacts with optional filtering."""
    return manager.get_all(tag=tag, search=search)


@router.get("/contacts/{contact_id}", response_model=Contact)
def get_contact(contact_id: str):
    """Get a specific contact by ID."""
    try:
        return manager.get(contact_id)
    except ContactNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/contacts/{contact_id}", response_model=Contact)
def update_contact(contact_id: str, update: ContactUpdate):
    """Update a contact."""
    try:
        return manager.update(contact_id, update)
    except ContactNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_200_OK)
def delete_contact(contact_id: str):
    """Delete a contact."""
    try:
        manager.delete(contact_id)
        return {"message": "Contact deleted successfully"}
    except ContactNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
