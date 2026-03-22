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

        assistant_message = result.get("content", result) if isinstance(result, dict) else str(result)

        # Add assistant response to history
        history.append({"role": "assistant", "content": assistant_message})

        return ChatResponse(
            response=assistant_message,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
