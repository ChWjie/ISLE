"""
Plan Schema Definitions
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class AgentPrompt(BaseModel):
    """智能体Prompt"""
    agent_id: str
    prompt: str
    max_tokens: int = 150  # 限制100字左右


class PlanGenerateRequest(BaseModel):
    """生成方案请求"""
    event_id: str
    agent_ids: List[str]  # 用户选中的智能体
    prompts: Optional[Dict[str, str]] = None  # 可选的自定义prompts


class AgentAnalysisResult(BaseModel):
    """单个智能体分析结果"""
    agent_id: str
    agent_name: str
    agent_type: str
    status: str  # pending/running/completed/error
    analysis: Optional[str] = None
    confidence: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PlanResponse(BaseModel):
    """方案响应"""
    plan_id: str
    event_id: str
    status: str  # generating/completed/error
    agent_results: List[AgentAnalysisResult]
    final_plan: Optional[str] = None
    created_at: datetime
    updated_at: datetime
