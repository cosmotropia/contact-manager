"use client";

import { Contact } from "@/lib/types";
import { Mail, Phone, Building2, Briefcase, Linkedin, Tag, Trash2, Edit2, List, Grid3x3, Search, Plus } from "lucide-react";
import { useEffect, useState } from "react";

interface ContactsCardProps {
  contacts: Contact[];
  themeColor: string;
  onDelete: (id: string) => void;
  onAdd: (contact: any) => void;
  onEdit: (id: string, contact: any) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  editingContact: Contact | null;
  onStartEdit: (contact: Contact) => void;
  onCancelEdit: () => void;
  isLoading: boolean;
}

export function ContactsCard({
    contacts,
    themeColor,
    onDelete,
    onAdd,
    onEdit,
    editingContact,
    onStartEdit,
    onCancelEdit,
    searchQuery,
    onSearchChange,
    isLoading,
  }: ContactsCardProps) {
    const safeContacts = contacts || [];
    const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
    
    const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        onSearchChange(e.target.value);
    }

    const filteredContacts = safeContacts;

    return (
        <div className="w-full max-w-6xl bg-white rounded-2xl shadow-2xl p-8">
        <div className="mb-8">
            <div className="flex justify-between items-center mb-4">
            <div>
                <h1 className="text-xl font-bold text-gray-900">Tus Contactos </h1>
                <p className="text-gray-600 mt-2">
                    {safeContacts.length} contacto{safeContacts.length !== 1 ? "s" : ""} en tu red
                    {isLoading ? " • Buscando..." : ""}
                </p>
            </div>

            {safeContacts.length > 0 && (
                <div className="flex items-center gap-2">
                <button
                    onClick={() => setViewMode("grid")}
                    className={`p-2 rounded-lg transition-colors ${
                    viewMode === "grid"
                        ? "bg-blue-100 text-blue-600"
                        : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                    }`}
                    title="Grid view"
                >
                    <Grid3x3 className="w-5 h-5" />
                </button>
                <button
                    onClick={() => setViewMode("list")}
                    className={`p-2 rounded-lg transition-colors ${
                    viewMode === "list"
                        ? "bg-blue-100 text-blue-600"
                        : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                    }`}
                    title="List view"
                >
                    <List className="w-5 h-5" />
                </button>
                </div>
            )}
            </div>

            {/* Search Bar */}
            {(safeContacts.length > 0 || searchQuery.trim().length > 0) && (
            <div className="relative">
                <input
                type="text"
                placeholder="Buscar por nombre, email, teléfono, empresa o tags..."
                value={searchQuery}
                onChange={handleSearchChange}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
            </div>
            )}
        </div>

        {safeContacts.length === 0 && !searchQuery ? (
            <div className="text-center py-16">
            <div className="text-gray-500 mb-6">
                <p className="text-lg mb-2">No hay contactos aún. Comienza añadiendo tu primer contacto!</p>
                <p className="text-sm">Puedes añadir contactos usando el asistente o el botón abajo.</p>
            </div>
            <button
                onClick={() => {
                const event = new CustomEvent('openAddContactDialog');
                window.dispatchEvent(event);
                }}
                style={{ backgroundColor: themeColor }}
                className="inline-flex items-center gap-2 px-6 py-3 text-white rounded-lg hover:opacity-90 transition-opacity font-medium"
            >
                <Plus className="w-5 h-5" />
                Añade tu primer contacto
            </button>
            </div>
        ) : filteredContacts.length === 0 ? (
            <div className="text-center py-16 text-gray-500">
                <p className="text-lg">
                    No se encontraron contactos que coincidan con "{searchQuery}"
                </p>
                <button
                    onClick={() => onSearchChange("")}
                    className="mt-4 text-blue-600 hover:underline"
                >
                    Limpiar búsqueda
                </button>
            </div>
        ) : viewMode === "grid" ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredContacts.map((contact) => (
                <ContactCardItem
                key={contact.id}
                contact={contact}
                themeColor={themeColor}
                onDelete={onDelete}
                onEdit={onStartEdit}
                />
            ))}
            </div>
        ) : (
            <div className="space-y-3">
            {filteredContacts.map((contact) => (
                <ContactListItem
                key={contact.id}
                contact={contact}
                themeColor={themeColor}
                onDelete={onDelete}
                onEdit={onStartEdit}
                />
            ))}
            </div>
        )}
        </div>
    );
    }

    // Grid Card View
    function ContactCardItem({
    contact,
    themeColor,
    onDelete,
    onEdit,
    }: {
    contact: Contact;
    themeColor: string;
    onDelete: (id: string) => void;
    onEdit: (contact: Contact) => void;
    }) {
    return (
        <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
        <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">{contact.name}</h3>
            {contact.position && (
                <p className="text-sm text-gray-600 flex items-center gap-1 mt-1">
                <Briefcase className="w-3 h-3" />
                {contact.position}
                </p>
            )}
            </div>
            <div className="flex items-center gap-2">
            <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: themeColor }}
            />
            <button
                onClick={() => onEdit(contact)}
                className="text-gray-400 hover:text-blue-500 transition-colors"
                title="Edit contact"
            >
                <Edit2 className="w-4 h-4" />
            </button>
            <button
                onClick={() => {
                if (window.confirm(`Delete ${contact.name}?`)) {
                    onDelete(contact.id);
                }
                }}
                className="text-gray-400 hover:text-red-500 transition-colors"
                title="Delete contact"
            >
                <Trash2 className="w-4 h-4" />
            </button>
            </div>
        </div>

        <div className="space-y-2 text-sm">
            <div className="flex items-center gap-2 text-gray-700">
            <Mail className="w-4 h-4 text-gray-400" />
            <a href={`mailto:${contact.email}`} className="hover:underline truncate">
                {contact.email}
            </a>
            </div>

            <div className="flex items-center gap-2 text-gray-700">
            <Phone className="w-4 h-4 text-gray-400" />
            <a href={`tel:${contact.phone}`} className="hover:underline">
                {contact.phone}
            </a>
            </div>

            {contact.company && (
            <div className="flex items-center gap-2 text-gray-700">
                <Building2 className="w-4 h-4 text-gray-400" />
                <span className="truncate">{contact.company}</span>
            </div>
            )}

            {contact.linkedin && (
            <div className="flex items-center gap-2">
                <Linkedin className="w-4 h-4 text-gray-400" />
                <a
                href={contact.linkedin}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline text-sm truncate"
                >
                Perfil de LinkedIn
                </a>
            </div>
            )}
        </div>

        {contact.tags && contact.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-4">
            {contact.tags.map((tag) => (
                <span
                key={tag}
                className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full flex items-center gap-1"
                >
                <Tag className="w-3 h-3" />
                {tag}
                </span>
            ))}
            </div>
        )}

        {contact.notes && (
            <div className="mt-4 pt-4 border-t border-gray-100">
            <p className="text-xs text-gray-600 italic line-clamp-2">{contact.notes}</p>
            </div>
        )}
        </div>
    );
    }

    // List View
    function ContactListItem({
    contact,
    themeColor,
    onDelete,
    onEdit,
    }: {
    contact: Contact;
    themeColor: string;
    onDelete: (id: string) => void;
    onEdit: (contact: Contact) => void;
    }) {
    return (
        <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 flex-1 min-w-0">
            <div
                className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0"
                style={{ backgroundColor: themeColor }}
            >
                {contact.name.charAt(0).toUpperCase()}
            </div>

            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                <h3 className="font-semibold text-gray-900 truncate">{contact.name}</h3>
                {contact.position && (
                    <span className="text-xs text-gray-500 truncate">• {contact.position}</span>
                )}
                </div>

                <div className="flex items-center gap-4 text-sm text-gray-600">
                <a href={`mailto:${contact.email}`} className="hover:underline truncate">
                    {contact.email}
                </a>
                <span>•</span>
                <a href={`tel:${contact.phone}`} className="hover:underline">
                    {contact.phone}
                </a>
                {contact.company && (
                    <>
                    <span>•</span>
                    <span className="truncate">{contact.company}</span>
                    </>
                )}
                </div>

                {contact.tags && contact.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                    {contact.tags.map((tag) => (
                    <span
                        key={tag}
                        className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full"
                    >
                        {tag}
                    </span>
                    ))}
                </div>
                )}
            </div>
            </div>

            <div className="flex items-center gap-2 ml-4">
            <button
                onClick={() => onEdit(contact)}
                className="text-gray-400 hover:text-blue-500 transition-colors p-2"
                title="Edit contact"
            >
                <Edit2 className="w-4 h-4" />
            </button>
            <button
                onClick={() => {
                if (window.confirm(`Delete ${contact.name}?`)) {
                    onDelete(contact.id);
                }
                }}
                className="text-gray-400 hover:text-red-500 transition-colors p-2"
                title="Delete contact"
            >
                <Trash2 className="w-4 h-4" />
            </button>
            </div>
        </div>
        </div>
    );
    }