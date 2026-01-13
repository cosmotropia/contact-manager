import { Mail, Phone, Building2, Briefcase, Tag } from "lucide-react";

interface ContactChatCardProps {
  contact: {
    id: string;
    name: string;
    email: string;
    phone: string;
    company?: string;
    position?: string;
    tags: string[];
    notes: string;
  };
}

export function ContactChatCard({ contact }: ContactChatCardProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-semibold text-lg text-gray-900">{contact.name}</h3>
      </div>
      
      <div className="space-y-2 text-sm">
        <div className="flex items-center gap-2 text-gray-600">
          <Mail className="w-4 h-4" />
          <span>{contact.email}</span>
        </div>
        
        <div className="flex items-center gap-2 text-gray-600">
          <Phone className="w-4 h-4" />
          <span>{contact.phone}</span>
        </div>
        
        {contact.company && (
          <div className="flex items-center gap-2 text-gray-600">
            <Building2 className="w-4 h-4" />
            <span>{contact.company}</span>
          </div>
        )}
        
        {contact.position && (
          <div className="flex items-center gap-2 text-gray-600">
            <Briefcase className="w-4 h-4" />
            <span>{contact.position}</span>
          </div>
        )}
        
        {contact.tags.length > 0 && (
          <div className="flex items-center gap-2 flex-wrap mt-2">
            <Tag className="w-4 h-4 text-gray-600" />
            {contact.tags.map((tag) => (
              <span
                key={tag}
                className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
        
        {contact.notes && (
          <div className="mt-2 pt-2 border-t border-gray-100">
            <p className="text-gray-600 text-xs italic">{contact.notes}</p>
          </div>
        )}
      </div>
    </div>
  );
}