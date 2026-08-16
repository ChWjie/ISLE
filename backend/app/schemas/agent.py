"""
Agent Schema Definitions
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.database import AgentType


class AgentBase(BaseModel):
    """Agent基础模型"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    mission: Optional[str] = None
    responsibilities: Optional[str] = None
    agent_type: AgentType
    system_prompt: Optional[str] = None
    stance: Optional[str] = None
    goals: Optional[List[str]] = None
    strategy_orientation: Optional[str] = "balanced"
    legal_priority: Optional[str] = "corporate_compliance"
    knowledge_scope: Optional[List[str]] = None
    llm_config: Optional[Dict[str, Any]] = None  # 重命名避免与Pydantic冲突
    template_id: Optional[str] = None


class AgentCreate(AgentBase):
    """创建Agent请求"""
    event_id: Optional[int] = None


class AgentUpdate(BaseModel):
    """更新Agent请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    mission: Optional[str] = None
    responsibilities: Optional[str] = None
    system_prompt: Optional[str] = None
    stance: Optional[str] = None
    goals: Optional[List[str]] = None
    strategy_orientation: Optional[str] = None
    legal_priority: Optional[str] = None
    knowledge_scope: Optional[List[str]] = None
    llm_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class AgentResponse(AgentBase):
    """Agent响应"""
    id: int
    agent_id: str
    event_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentTemplate(BaseModel):
    """Agent模板"""
    template_id: str
    name: str
    agent_type: AgentType
    description: str
    system_prompt: str
    default_config: Dict[str, Any]
    suitable_scenarios: List[str]
