import os
import uuid
from typing import Optional
from collections import defaultdict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from nemoguardrails import RailsConfig, LLMRails

router = APIRouter()

# In-memory session store
sessions: dict[str, list[dict]] = defaultdict(list)
MAX_HISTORY = 20

# Load NeMo Guardrails config once
config_path = os.path.join(os.path.dirname(__file__), "..", "config")
rails_config = RailsConfig.from_path(config_path)
rails = LLMRails(rails_config)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())

    # Get or initialize history
    history = sessions[session_id]

    # Add user message
    history.append({"role": "user", "content": request.message})

    # Trim to max history
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
        sessions[session_id] = history

    try:
        # Pass through NeMo Guardrails
        result = await rails.generate_async(
            messages=history
        )

        # NeMo Guardrails returns either:
        # - a dict with "content" key
        # - a dict with "role" and "content" keys  
        # - a list of message dicts
        # - a string directly
        assistant_message = ""
        if isinstance(result, dict):
            assistant_message = result.get("content", "")
        elif isinstance(result, list):
            # Get the last assistant message from the list
            for msg in reversed(result):
                if isinstance(msg, dict) and msg.get("role") == "assistant":
                    assistant_message = msg.get("content", "")
                    break
        elif isinstance(result, str):
            assistant_message = result
        
        if not assistant_message:
            assistant_message = "I'm here to help with Pantoja Digital's services — security testing, AI agents, web development, and SEO. What would you like to know?"

        # Add assistant response to history
        history.append({"role": "assistant", "content": assistant_message})

        return ChatResponse(
            response=assistant_message,
            session_id=session_id
        )
    except Exception as e:
        return ChatResponse(
            response="I'm having trouble right now. You can reach our team at team@pantojadigital.com or visit pantojadigital.com/contact. How else can I help?",
            session_id=session_id
        )
