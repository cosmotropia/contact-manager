"use client";

import { ContactsCard } from "@/components/contacts-card";
import { AddContactDialog } from "@/components/add-contact-dialog";
import { ContactChatCard } from "@/components/contact-chat-card";
import { contactsApi, Contact } from "@/app/api/api";
import { CopilotKitCSSProperties, CopilotSidebar } from "@copilotkit/react-ui";
import { useCoAgent, useFrontendTool, useCopilotAction } from "@copilotkit/react-core";
import { useState, useEffect, useRef } from "react";

export default function CopilotKitPage() {
  const [themeColor, setThemeColor] = useState("#6366f1");
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingContact, setEditingContact] = useState<Contact | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const debounceRef = useRef<number | null>(null);

  useEffect(() => {
    loadContacts("");
  }, []);
  
  const loadContacts = async (query?: string) => {
    try {
      setIsLoading(true);
      const q = (query ?? "").trim();
      const data = q ? await contactsApi.search(q) : await contactsApi.getAll();
      setContacts(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error loading contacts:", error);
      setContacts([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearchChange = (query: string) => {
    setSearchQuery(query);
    if (debounceRef.current) window.clearTimeout(debounceRef.current);
    debounceRef.current = window.setTimeout(() => {
      loadContacts(query);
    }, 250);
  };

  const handleAddContact = async (contactData: any) => {
    try {
      await contactsApi.create(contactData);
      await loadContacts();
    } catch (error) {
      console.error("Error adding contact:", error);
    }
  };

  const handleEditContact = async (id: string, contactData: any) => {
    try {
      await contactsApi.update(id, contactData);
      await loadContacts();
    } catch (error) {
      console.error("Error editing contact:", error);
    }
  };

  const handleDeleteContact = async (id: string) => {
    try {
      await contactsApi.delete(id);
      await loadContacts();
    } catch (error) {
      console.error("Error deleting contact:", error);
    }
  };

  const { state } = useCoAgent<{ messages: any[] }>({
    name: "sample_agent",
    initialState: {
      messages: []
    },
  });
  
  //Refrescar contactos luego de una accion del agente
  useFrontendTool({
    name: "refreshContacts",
    parameters: [],
    handler: () => {
      loadContacts(searchQuery);
    },
  });

  //Acciones para el agente
  useCopilotAction({
    name: "displayContacts",
    description: "Displays contacts as visual cards in the chat interface",
    parameters: [
      {
        name: "contacts",
        type: "object[]",
        description: "Array of contact objects to display",
        required: true,
      }
    ],
    handler: async ({ contacts }) => {
      return `Displaying ${contacts.length} contacts`;
    },
    render: ({ status, args }) => {
      if (status === "complete" && args.contacts) {
        return (
          <div className="space-y-3 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm font-medium text-gray-700 mb-3">
              📋 {args.contacts.length} contacto{args.contacts.length !== 1 ? 's' : ''} encontrado{args.contacts.length !== 1 ? 's' : ''}
            </p>
            <div className="space-y-3">
              {args.contacts.map((contact: Contact) => (
                <ContactChatCard key={contact.id} contact={contact} />
              ))}
            </div>
          </div>
        );
      }
      return <div className="text-gray-500 italic">Cargando contactos...</div>;
    },
  });

  return (
    <main
      style={{ "--copilot-kit-primary-color": themeColor } as CopilotKitCSSProperties}
    >
      <CopilotSidebar
        disableSystemMessage={true}
        clickOutsideToClose={false}
        defaultOpen={true}
        labels={{
          title: "Gestión de Contactos",
          initial: "👋 Hola! soy tu asistente de gestión de contactos. Puedo ayudarte con algunas tareas básicas.",
        }}
        suggestions={[
          {
            title: "Añadir",
            message:
              "Añade un contacto: Nombre: Juan Pérez, Email: juan.perez@innovaai.com, Teléfono: +15145559876, Empresa: InnovaAI, Cargo: AI Engineer, LinkedIn: https://www.linkedin.com/in/juanperez, Tags: prospect, ai, startup, montreal, Notes: Contactado por LinkedIn. Interesado en colaborar en un proyecto piloto de IA aplicada",
          },
          {
            title: "Buscar",
            message: "Muestra mis contactos relacionados con tecnología y su estado",
          },
          {
            title: "Analizar",
            message:
              "Analiza mis contactos: 1) agrúpalos por tags, 2) dime cuáles parecen de tecnología (por empresa/cargo/tags), 3) sugiere 5 siguientes acciones (ej: pedir reunión, enviar follow-up) basadas en notes",
          },
          {
            title: "Priorizar",
            message:
              "Revisa mis contactos y dime cuáles debería priorizar esta semana considerando: últimos contactos, tags, cargo y notes. Dame una lista corta (máx. 3) con el porqué de cada uno.",
          },
          {
            title: "Oportunidades",
            message:
              "Revisa mis contactos y detecta posibles oportunidades comerciales o colaboraciones basándote en cargo, empresa y notes. Devuélveme hasta 3 insights."
          }
        ]}
      >
        <div
          style={{ backgroundColor: `${themeColor}10` }}
          className="min-h-screen flex flex-col items-center p-8 transition-colors duration-300"
        >
          <div className="w-full max-w-6xl mb-6 flex justify-between items-center">
            <h1 className="text-2xl font-bold">Contact Manager AI </h1>
            <AddContactDialog 
              onAdd={handleAddContact} 
              onEdit={handleEditContact}
              themeColor={themeColor}
              editingContact={editingContact ?? null}
              onCloseEdit={() => setEditingContact(null)}
            />
          </div>

          <ContactsCard
            contacts={contacts ?? []}
            themeColor={themeColor}
            onDelete={handleDeleteContact}
            onAdd={handleAddContact}
            onEdit={handleEditContact}
            editingContact={editingContact ?? null}
            onStartEdit={setEditingContact}
            onCancelEdit={() => setEditingContact(null)}
            searchQuery={searchQuery}
            onSearchChange={handleSearchChange}
            isLoading={isLoading}
          />
        </div>
      </CopilotSidebar>
    </main>
  );
}