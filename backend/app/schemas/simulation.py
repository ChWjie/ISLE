"""
Simulation Schema Definitions
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.database import SimulationStatus


class SimulationStartRequest(BaseModel):
    """推演启动请求"""
    plan_id: int
    blue_agent_id: str
    red_agent_id: str
    judge_agent_id: str
    max_rounds: int = 10
    target_win_rate: Optional[float] = 80.0
    termination_type: str = "win_rate"  # win_rate or rounds
    auto_optimize: bool = True
    auto_save: bool = True


class RoundArgument(BaseModel):
    """单轮论证"""
    agent_type: str  # blue, red, judge
    agent_name: str
    content: str
    legal_basis: Optional[List[str]] = []
    risks_raised: Optional[List[str]] = []


class RoundResult(BaseModel):
    """单轮推演结果"""
    round_number: int
    blue_argument: RoundArgument
    red_argument: RoundArgument
    judge_ruling: Optional[RoundArgument] = None
    win_rate_before: float
    win_rate_after: float
    win_rate_delta: float


class SimulationResponse(BaseModel):
    """推演会话响应"""
    id: int
    session_id: str
    plan_id: int
    status: SimulationStatus
    current_round: int
    win_rate: float
    total_rounds: int
    evidence_stats: Optional[Dict[str, Any]] = None
    final_result: Optional[Dict[str, Any]] = None
    optimized_plan_id: Optional[str] = None
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class NextRoundRequest(BaseModel):
    """执行下一轮请求"""
    session_id: str
    manual_input: Optional[str] = None  # 人工介入内容
