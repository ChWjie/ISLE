"""
Event Schema Definitions
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class EventBase(BaseModel):
    """Event基础模型"""
    event_id: str
    name: str
    description: Optional[str] = None
    dispute_type: Optional[str] = None
    our_side: List[str] = []
    opponent_side: List[str] = []
    legal_systems: List[str] = []
    fact_summary: Optional[str] = None
    opponent_stance_preset: Optional[str] = None
    opponent_claims_options: List[str] = []
    opponent_legal_system: Optional[str] = None


class EventCreate(EventBase):
    """创建Event请求"""
    pass


class EventResponse(EventBase):
    """Event响应"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
