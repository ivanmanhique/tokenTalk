# models.py - Response models for API
from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class AlertResponse:
    id: str
    message: str
    status: str
    condition_type: str
    tokens: List[str]
    threshold: float
    created_at: str
    triggered_at: Optional[str] = None

@dataclass
class CreateAlertRequest:
    user_id: str
    message: str  # Natural language: "Alert me when ETH hits $4000"
    # We'll parse this with NLP later

@dataclass
class AlertListResponse:
    alerts: List[AlertResponse]
    total: int


from dataclasses import dataclass

@dataclass
class ChatMessage:
    message: str
    user_id: str = "default_user"

@dataclass
class ChatResponse:
    response: str
    parsed: Optional[Dict]
    alert_created: bool
    alert_id: Optional[str]
    timestamp: str
    user_id: str
