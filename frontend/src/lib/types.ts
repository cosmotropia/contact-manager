// State of the agent, make sure this aligns with your agent's state.
export interface AgentState {
  contacts: Contact[];
}
export interface Contact {
  id: string;
  name: string;
  email: string;
  phone: string;
  company?: string;
  position?: string;
  linkedin?: string;
  tags: string[];
  notes: string;
  last_contact_date?: string;
  relationship_status: "active" | "inactive" | "prospect";
}

export interface ContactCreate {
  name: string;
  email: string;
  phone: string;
  company?: string;
  position?: string;
  linkedin?: string;
  tags?: string[];
  notes?: string;
}