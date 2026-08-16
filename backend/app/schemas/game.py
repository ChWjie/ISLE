from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class GameStatus(str, Enum):
    """博弈状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class RuleType(str, Enum):
    """规则类型"""
    PERMISSION = "permission"      # 行动许可规则
    RISK = "risk"                  # 风险触发规则
    PREMISE = "premise"            # 前提失效规则
    TERMINATION = "termination"    # 终止与回退规则


class GameRule(BaseModel):
    """博弈规则"""
    type: RuleType
    condition: str
    action: str
    priority: int = 0


class GameRound(BaseModel):
    """博弈回合"""
    round: int
    our_action: str
    their_action: str
    risks: List[str] = Field(default_factory=list)
    state: Dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentConfigSide(BaseModel):
    """单方智能体配置"""
    llm_model: str = Field(default="deepseek", description="LLM模型")
    temperature: float = Field(default=0.7, ge=0, le=2, description="温度参数")
    custom_prompt: Optional[str] = Field(None, description="自定义提示词")
    max_tokens: int = Field(default=500, ge=100, le=2000, description="最大token数")


class GameStartRequest(BaseModel):
    """启动博弈请求"""
    event_id: str
    plan_id: str
    rules: List[GameRule] = Field(default_factory=list)
    max_rounds: int = Field(default=10, ge=1, le=50)
    # 双方智能体配置
    our_agent_config: Optional[AgentConfigSide] = Field(default=None, description="我方智能体配置")
    opponent_agent_config: Optional[AgentConfigSide] = Field(default=None, description="对方智能体配置")


class GameSessionResponse(BaseModel):
    """博弈会话响应"""
    id: str
    event_id: str
    plan_id: str
    status: GameStatus
    current_round: int
    max_rounds: int
    rounds: List[GameRound]
    created_at: datetime

    class Config:
        from_attributes = True


class GameResult(BaseModel):
    """博弈结果"""
    session_id: str
    total_rounds: int
    outcome: str  # success/failure/uncertain
    risk_score: float
    recommendations: List[str]
    summary: str
