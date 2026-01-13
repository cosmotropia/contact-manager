"use client";

import { useState, useEffect } from "react";
import { Plus, X } from "lucide-react";
import { Contact } from "@/lib/types";

interface AddContactDialogProps {
  onAdd: (contact: any) => void;
  onEdit?: (id: string, contact: any) => void;
  themeColor: string;
  editingContact?: Contact | null;
  onCloseEdit?: () => void;
}

export function AddContactDialog({ 
  onAdd, 
  onEdit, 
  themeColor, 
  editingContact = null,
  onCloseEdit 
}: AddContactDialogProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    company: "",
    position: "",
    linkedin: "",
    tags: "",
    notes: "",
  });

  const isEditMode = !!editingContact;

  // Load data when editing
  useEffect(() => {
    if (editingContact) {
      setFormData({
        name: editingContact.name,
        email: editingContact.email,
        phone: editingContact.phone,
        company: editingContact.company || "",
        position: editingContact.position || "",
        linkedin: editingContact.linkedin || "",
        tags: editingContact.tags ? editingContact.tags.join(", ") : "",
        notes: editingContact.notes || "",
      });
    }
  }, [editingContact]);

  // Listen for custom event to open dialog
  useEffect(() => {
    const handleOpen = () => setIsOpen(true);
    window.addEventListener('openAddContactDialog', handleOpen);
    return () => window.removeEventListener('openAddContactDialog', handleOpen);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const tagList = formData.tags
      ? formData.tags.split(",").map((t) => t.trim())
      : [];

    const contactData = {
      ...formData,
      tags: tagList,
    };

    if (isEditMode && editingContact && onEdit) {
      onEdit(editingContact.id, contactData);
      onCloseEdit?.();
    } else {
      onAdd(contactData);
      setIsOpen(false);
    }

    // Reset form
    setFormData({
      name: "",
      email: "",
      phone: "",
      company: "",
      position: "",
      linkedin: "",
      tags: "",
      notes: "",
    });
  };

  const handleClose = () => {
    if (isEditMode) {
      onCloseEdit?.();
    } else {
      setIsOpen(false);
    }
    // Reset form
    setFormData({
      name: "",
      email: "",
      phone: "",
      company: "",
      position: "",
      linkedin: "",
      tags: "",
      notes: "",
    });
  };

  // Don't show button when in edit mode
  if (!isOpen && !isEditMode) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        style={{ backgroundColor: themeColor }}
        className="flex items-center gap-2 px-4 py-2 text-white rounded-lg hover:opacity-90 transition-opacity"
      >
        <Plus className="w-5 h-5" />
        Añadir Contacto
      </button>
    );
  }

  if (!isOpen && !isEditMode) return null;

  return (
    <div className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">
            {isEditMode ? "Editar Contacto" : "Añadir Nuevo Contacto"}
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nombre *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email * (obligatorio)
            </label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Teléfono * (obligatorio)
            </label>
            <input
              type="tel"
              required
              value={formData.phone}
              onChange={(e) =>
                setFormData({ ...formData, phone: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Company
            </label>
            <input
              type="text"
              value={formData.company}
              onChange={(e) =>
                setFormData({ ...formData, company: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Cargo
            </label>
            <input
              type="text"
              value={formData.position}
              onChange={(e) =>
                setFormData({ ...formData, position: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Perfil de LinkedIn
            </label>
            <input
              type="url"
              value={formData.linkedin}
              onChange={(e) =>
                setFormData({ ...formData, linkedin: e.target.value })
              }
              placeholder="https://linkedin.com/in/..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tags (separados por comas)
            </label>
            <input
              type="text"
              placeholder="client, vip, tech"
              value={formData.tags}
              onChange={(e) =>
                setFormData({ ...formData, tags: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notas
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) =>
                setFormData({ ...formData, notes: e.target.value })
              }
              rows={3}
              placeholder="Añade cualquier nota sobre este contacto..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {isEditMode ? (
            <div className="flex gap-3">
              <button
                type="button"
                onClick={handleClose}
                className="flex-1 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
              >
                Cancelar
              </button>
              <button
                type="submit"
                style={{ backgroundColor: themeColor }}
                className="flex-1 py-3 text-white rounded-lg hover:opacity-90 transition-opacity font-medium"
              >
                Guardar Cambios
              </button>
            </div>
          ) : (
            <button
              type="submit"
              style={{ backgroundColor: themeColor }}
              className="w-full py-3 text-white rounded-lg hover:opacity-90 transition-opacity font-medium"
            >
              Añadir Contacto
            </button>
          )}
        </form>
      </div>
    </div>
  );
}