const API_URL = "http://localhost:8001/api";

// ==============================
// Types
// ==============================

import type { Contact, ContactCreate } from "@/lib/types";

// ==============================
// Helpers
// ==============================

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const error = await res.text();
    throw new Error(error || `HTTP error ${res.status}`);
  }
  return res.json();
}

function normalizeContacts(data: any): Contact[] {
  // Backend puede devolver [] o { contacts: [] }
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.contacts)) return data.contacts;
  return [];
}

// ==============================
// API
// ==============================

export const contactsApi = {
  // Get all contacts
  async getAll(): Promise<Contact[]> {
    const res = await fetch(`${API_URL}/contacts`);
    const data = await handleResponse<any>(res);

    const contacts = normalizeContacts(data);
    console.log("📇 Contacts loaded:", contacts.length);

    return contacts;
  },

  // Create contact
  async create(contact: ContactCreate): Promise<Contact> {
    const res = await fetch(`${API_URL}/contacts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(contact),
    });

    const data = await handleResponse<any>(res);

    // Backend devuelve contacto directo
    return data.contact ?? data;
  },

  // Update contact
  async update(
    id: string,
    updates: Partial<ContactCreate>
  ): Promise<Contact> {
    const res = await fetch(`${API_URL}/contacts/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    });

    const data = await handleResponse<any>(res);
    return data.contact ?? data;
  },

  // Delete contact
  async delete(id: string): Promise<void> {
    const res = await fetch(`${API_URL}/contacts/${id}`, {
      method: "DELETE",
    });

    if (!res.ok) {
      const error = await res.text();
      throw new Error(error || "Failed to delete contact");
    }
  },

  // Search contacts
  async search(query: string): Promise<Contact[]> {
    const res = await fetch(
      `${API_URL}/contacts?search=${encodeURIComponent(query)}`
    );

    const data = await handleResponse<any>(res);
    return normalizeContacts(data);
  },

  // Search contacts by tag
  async searchByTag(tag: string): Promise<Contact[]> {
    const res = await fetch(
      `${API_URL}/contacts?tag=${encodeURIComponent(tag)}`
    );

    const data = await handleResponse<any>(res);
    return normalizeContacts(data);
  },
};

export type { Contact, ContactCreate };