"""
Agente
Interpreta, llama a la API del backend via HTTP.
"""
import httpx
from copilotkit import CopilotKitState
from langchain.tools import tool
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import Command

import logging

# --------------------------------------------------
# Configuración de Logging
# --------------------------------------------------
logger = logging.getLogger("contact_agent")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
)
handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)

# Backend API URL
BACKEND_API = "http://localhost:8001/api"


class AgentState(CopilotKitState):
    """Agent state - only for conversational context."""
    pass

# ==========================================
# FUNCIONES HELPER
# ==========================================

def _extract_contacts(result):
    """Extract contacts from backend response."""
    if isinstance(result, dict) and "contacts" in result and isinstance(result["contacts"], list):
        return result["contacts"]
    if isinstance(result, list):
        return result
    return None

# ==========================================
# TOOLS - El agente llama a la API del backend via HTTP
# ==========================================

@tool
def add_contact(name: str, email: str, phone: str, company: str = "", position: str = "", linkedin: str = "", tags: str = "", notes: str = ""):
    """
    Request backend to add a new contact.
    Tags should be comma-separated.
    """
    logger.info(f"Adding contact: {name}, {email}, {phone}, {company}, {position}, {linkedin}, {tags}")
    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    
    payload = {
        "name": name,
        "email": email,
        "phone": phone,
        "company": company or None,
        "position": position or None,
        "linkedin": linkedin or None,
        "tags": tag_list,
        "notes": notes or None
    }
    
    try:
        response = httpx.post(f"{BACKEND_API}/contacts", json=payload, timeout=10.0)
        result = response.json()
        
        if response.status_code == 201:
            logger.info("Contact created successfully")
            return result
        else:
            return f"❌ Error: {result.get('detail', 'Unknown error')}"
    except Exception as e:
        return f"❌ Error connecting to backend: {str(e)}"


@tool       
def get_all_contacts():
    """Request backend for all contacts."""
    logger.info("Getting all contacts")
    try:
        response = httpx.get(f"{BACKEND_API}/contacts", timeout=10.0)
        result = response.json()

        if response.status_code != 200:
            return f"❌ Error: {result.get('detail', 'Unknown error') if isinstance(result, dict) else 'Unknown error'}"

        contacts = _extract_contacts(result)
        if contacts is None:
            logger.error(f"Unexpected backend response: {result}")
            return "❌ Unexpected backend response format."

        if len(contacts) == 0:
            return "📭 No contacts in the system yet."

        logger.info(f"Retrieved {len(contacts)} contacts")
        return contacts

    except Exception as e:
        logger.exception("Failed to get contacts")
        return f"❌ Error connecting to backend: {str(e)}"


@tool
def search_contacts(query: str = "", tag: str = ""):
    """
    Request backend to search contacts by name, email, phone, or tag.
    """
    logger.info(f"Searching contacts: {query}, {tag}")
    try:
        params = {}
        if query:
            params["search"] = query
        if tag:
            params["tag"] = tag
        
        response = httpx.get(f"{BACKEND_API}/contacts", params=params, timeout=10.0)
        result = response.json()
        
        if response.status_code != 200:
            return f"❌ Error: {result.get('detail', 'Unknown error') if isinstance(result, dict) else 'Unknown error'}"

        contacts = _extract_contacts(result)
        if contacts is None:
            logger.error(f"Unexpected backend response: {result}")
            return "❌ Unexpected backend response format."

        if not contacts:
            return f"🔍 No contacts found for: {query or tag}"

        logger.info(f"Found {len(contacts)} contacts")
        return contacts

    except Exception as e:
        return f"❌ Error connecting to backend: {str(e)}"


@tool
def update_contact_notes(contact_id: str, notes: str):
    """Request backend to update notes for a contact."""
    logger.info(f"Updating notes for contact: {contact_id}, {notes}")
    try:
        payload = {"notes": notes}
        response = httpx.put(f"{BACKEND_API}/contacts/{contact_id}", json=payload, timeout=10.0)
        result = response.json()
        logger.info(f"Result: {result}")
        if response.status_code == 200:
            return f"✅ Notes updated successfully"
        else:
            return f"❌ Error: {result.get('detail', 'Unknown error')}"
    except Exception as e:
        return f"❌ Error connecting to backend: {str(e)}"


@tool
def delete_contact_tool(contact_id: str):
    """Request backend to delete a contact."""
    try:
        response = httpx.delete(f"{BACKEND_API}/contacts/{contact_id}", timeout=10.0)
        result = response.json()
        
        if response.status_code == 200:
            return f"✅ Contact deleted successfully"
        else:
            return f"❌ Error: {result.get('detail', 'Unknown error')}"
    except Exception as e:
        return f"❌ Error connecting to backend: {str(e)}"


# ==========================================
# Agent workflow
# ==========================================

backend_tools = [
    add_contact,
    get_all_contacts,
    search_contacts,
    update_contact_notes,
    delete_contact_tool
]
backend_tool_names = [tool.name for tool in backend_tools]


async def chat_node(state: AgentState, config: RunnableConfig) -> Command[str]:
    model = ChatOpenAI(model="gpt-4o-mini")
    model_with_tools = model.bind_tools(
        [
            *state.get("copilotkit", {}).get("actions", []),
            *backend_tools,
        ],
        parallel_tool_calls=False,
    )
    
    system_message = SystemMessage(
    content="""
        You are a professional contact management assistant.

        Your primary role is NOT to list data, but to help the user understand,
        filter, analyze, and act on their contacts.

        CORE RESPONSIBILITIES:
        - Interpret user intent
        - Call backend API tools when needed
        - Decide whether displaying contacts in chat adds real value
        - Provide concise summaries and intelligent next-step suggestions

        IMPORTANT UI PRINCIPLE:
        The main UI already displays contact lists.
        The chat should only render contact cards when it provides HIGH contextual value.

        DISPLAY RULES (VERY IMPORTANT):
        - If result count is 1 → call `displayContacts`
        - If result count is 2–3 → you MAY call `displayContacts`
        - If result count > 3 → DO NOT call `displayContacts`
        Instead:
        - Provide a short summary (count + high-level insight)
        - Propose concrete next actions (filters, grouping, analysis)

        CRITICAL:
        After calling `displayContacts`, you MUST NOT repeat ANY contact fields in text, because the cards with details are already displayed.
        Do not restate names, emails, phones, companies, tags, notes, or statuses.

        AVAILABLE TOOLS (MANDATORY USAGE):
        - add_contact
        - get_all_contacts
        - search_contacts
        - update_contact_notes
        - delete_contact_tool

        NEVER:
        - Invent contact data
        - Modify data without using a tool
        - Repeat contact details after displayContacts
        - Dump large lists into the chat

        WORKFLOW:
        1. Fetch data using a backend tool
        2. Evaluate result size
        3. Decide:
        - Render (1–3 contacts)
        - OR summarize (>3 contacts)
        4. Offer the next logical action

        CATEGORY / FILTER HANDLING:
        - If user requests a category (e.g. "tech"):
        1) Call `get_all_contacts`
        2) Filter locally using tags first, then company/position keywords
        3) Apply DISPLAY RULES based on result size
        4) If no matches, explain and ask how the category should be defined

        AFTER DATA MODIFICATION:
        - Always call `refreshContacts` to sync the UI

        CONTINUITY RULE:
        - Always continue the user's last intent
        - Suggestions must stay tightly related to the current context
        - No generic or vague questions

        LANGUAGE RULE (CRITICAL):
        - ALWAYS respond in the same language as the user

        STATE AUTHORITY RULE (CRITICAL):
            - The backend API is the single source of truth.
            - Conversation memory is NOT a reliable source of data state.

            Before making ANY statement about:
            - whether a contact exists
            - whether a contact was deleted
            - whether a contact can be added
            - whether something is duplicated

            YOU MUST:
            1. Call `get_all_contacts` or `search_contacts`
            2. Base your decision ONLY on that response

            You are NOT allowed to infer data state from:
            - previous messages
            - earlier tool calls
            - conversation memory

            If the backend response contradicts previous context:
            - The backend ALWAYS wins.
        """
        )

    
    response = await model_with_tools.ainvoke(
        [system_message, *state["messages"]],
        config,
    )
    
    if route_to_tool_node(response):
        return Command(goto="tool_node", update={"messages": [response]})
    
    return Command(goto=END, update={"messages": [response]})


def route_to_tool_node(response: BaseMessage):
    tool_calls = getattr(response, "tool_calls", None)
    if not tool_calls:
        return False
    
    for tool_call in tool_calls:
        if tool_call.get("name") in backend_tool_names:
            return True
    return False


workflow = StateGraph(AgentState)
workflow.add_node("chat_node", chat_node)
workflow.add_node("tool_node", ToolNode(tools=backend_tools))
workflow.add_edge("tool_node", "chat_node")
workflow.set_entry_point("chat_node")

graph = workflow.compile()