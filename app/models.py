from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    intent: str
    risk_level: str
    confidence_score: float
    response: str
    recommended_action: str
    log_required: bool
    extracted_info: Optional[dict] = {}

# --- Honeypot API Models ---

class HoneyPotMessage(BaseModel):
    sender: str
    text: str
    timestamp: Optional[str] = None

class HoneyPotMetadata(BaseModel):
    channel: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None

class HoneyPotRequest(BaseModel):
    sessionId: str
    message: HoneyPotMessage
    conversationHistory: List[HoneyPotMessage] = []
    metadata: Optional[HoneyPotMetadata] = None

class HoneyPotResponse(BaseModel):
    status: str = "success"
    reply: str
    riskLevel: Optional[str] = None
