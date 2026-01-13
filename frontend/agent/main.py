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
import os

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
BACKEND_API = os.getenv("NEXT_PUBLIC_BACKEND_URL", "http://localhost:8001/api")

if not BACKEND_API.endswith("/api"):
    BACKEND_API = BACKEND_API.rstrip("/") + "/api"


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
    model = ChatOpenAI(model="gpt-4o")
    model_with_tools = model.bind_tools(
        [
            *state.get("copilotkit", {}).get("actions", []),
            *backend_tools,
        ],
        parallel_tool_calls=False,
    )
    
    system_message = SystemMessage(
    content="""
        You are a professional contact management assistant embedded in a system where the backend is the single source of truth.

        YOUR ROLE:
        - INTERPRET user intent from each message.
        - CALL the correct backend tool to fetch or update data.
        - ANALYZE tool responses to decide next steps.
        - ACT as a smart mediator, not a data dumper.

        IMPORTANT:
        The main UI ALREADY DISPLAYS contact cards. Your job is to add insight, not repetition.

        🎯 DISPLAY STRATEGY:
        - IF result is a list:
            - LET `n` = number of items in the list.
            - IF n == 0 → SAY no results + suggest next action (NO `displayContacts`).
            - IF n == 1 → MUST CALL `displayContacts` for 1 contact + suggest next action.
            - IF n in [2,3] → MUST call `displayContacts` for all + brief summary/suggestion.
            - IF n > 3 → DO NOT CALL `displayContacts`. Instead:
                - SAY how many were found
                - PROVIDE high-level summary (e.g., tag or company breakdown)
                - SUGGEST filters or grouping options

        AFTER `displayContacts`, DO NOT REPEAT:
        - name, email, phone, company, tags, notes, status → the cards already show them.

        TOOL RULES (USE ONLY THESE):
        - `get_all_contacts` → to fetch all contacts
        - `search_contacts` → for search/filter by name, tag, etc.
        - `add_contact` → to add a contact
        - `update_contact_notes` → to update notes
        - `delete_contact_tool` → to delete a contact

        AFTER ANY MODIFICATION (add/update/delete):
        - ALWAYS CALL `refreshContacts`
        - THEN fetch updated data with `get_all_contacts` or `search_contacts` as needed

        STATE RULE (MANDATORY):
        - BACKEND = SINGLE SOURCE OF TRUTH
        - You MUST call `get_all_contacts` or `search_contacts` BEFORE making any claim about:
            - whether a contact exists
            - if it was deleted
            - if it can be added
            - if it's duplicated
        - DO NOT rely on previous tool calls or memory

        FILTERING BY CATEGORY (TECH, CLIENT, ETC.):
        - IF user requests a category:
            1. CALL `get_all_contacts`
            2. FILTER LOCALLY using ALL of the following fields:
                - TAGS
                - COMPANY
                - POSITION
            3. Consider a match ONLY IF:
                - AT LEAST ONE field (tag, position, or company) CONTAINS the keyword
                - AND the match is SEMANTICALLY RELEVANT (e.g., "tech" should NOT match “actriz”)
            4. DO NOT include results that only match superficially but are unrelated to the intent of the category
            5. Apply DISPLAY STRATEGY based on the number of matches
            6. If no match → EXPLAIN and ASK user how they define the category

        CONTINUITY RULE:
        - ALWAYS respond in the user's language
        - KEEP FOCUS on the user's last request
        - AVOID generic questions or topic shifts

        CRITICAL FILTERING OUTPUT RULE:

        - WHEN filtering by category:
            - ONLY acknowledge and talk about contacts that MATCH the category.
            - DO NOT mention, explain, justify, or reference contacts that were evaluated and discarded.
            - DO NOT say things like:
                - "The third contact is not related to tech"
                - "Other contacts were excluded"
                - "X does not match the category"
            - SILENCE is mandatory for non-matching contacts.

        RATIONALE:
        The user-facing response must reflect ONLY the final filtered result,
        not the internal reasoning or evaluation process.

        NEVER:
        - INVENT contacts or details
        - GUESS result counts
        - DISPLAY more than 3 contacts
        - REPEAT contact fields shown in cards
        - SAY something exists unless the backend says so
        - FILTER by only one field when interpreting a category — YOU MUST consider tags, position, and company together
        - SKIP matching contacts just because one field doesn't match — a match in ANY relevant field is enough
        - STOP after finding the first match — CHECK ALL contacts and RETURN ALL valid matches
        - ASSUME that a category like "tech" only means engineering — it could include PMs, designers, etc.
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