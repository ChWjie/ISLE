"""
Enhanced Database Models for 48h Sprint
Supports: Events, Agents, Plans, Simulations
"""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Float, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


def enum_values(enum_cls):
    return [member.value for member in enum_cls]


class AgentType(str, enum.Enum):
    """Agent类型枚举"""
    BLUE = "blue"  # 我方
    RED = "red"    # 对手
    JUDGE = "judge"  # 裁判
    ANALYST = "analyst"  # 分析师


class SimulationStatus(str, enum.Enum):
    """推演状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    OPTIMIZING = "optimizing"
    COMPLETED = "completed"
    FAILED = "failed"


class Event(Base):
    """事件模型 (S1/S2)"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(50), unique=True, index=True)  # Event-20251222-ECS
    name = Column(String(200), nullable=False)
    description = Column(Text)
    dispute_type = Column(String(100))  # 争议类型
    our_side = Column(JSON)  # 我方主体 (list)
    opponent_side = Column(JSON)  # 对方主体 (list)
    legal_systems = Column(JSON)  # 涉及法律体系 (list)
    fact_summary = Column(Text)

    # Dynamic Agent Config
    opponent_stance_preset = Column(Text)  # 对方预设立场
    opponent_claims_options = Column(JSON)  # 对方可能主张 (list of strings or dicts)
    opponent_legal_system = Column(String(50))  # 对方法律体系侧重
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agents = relationship("Agent", back_populates="event", cascade="all, delete-orphan")
    plans = relationship("Plan", back_populates="event", cascade="all, delete-orphan")


class Agent(Base):
    """智能体配置 (S3)"""
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(50), unique=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)  # 描述
    mission = Column(Text)  # 角色使命
    responsibilities = Column(Text)  # 核心职责
    agent_type = Column(
        Enum(AgentType, values_callable=enum_values, native_enum=False),
        nullable=False
    )

    # 关联事件
    event_id = Column(Integer, ForeignKey("events.id"))
    event = relationship("Event", back_populates="agents")

    # 配置
    system_prompt = Column(Text)  # 系统提示词
    stance = Column(Text)  # 立场
    goals = Column(JSON)  # 目标列表
    strategy_orientation = Column(String(50))  # 策略倾向
    legal_priority = Column(String(50))  # 法律体系优先级
    knowledge_scope = Column(JSON)  # 法律知识范围 (list of categories: ["公司法", "数据合规"])

    # LLM配置
    llm_config = Column(JSON)  # {temperature, max_tokens, etc}

    # 元数据
    template_id = Column(String(50))  # 基于哪个模板
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Plan(Base):
    """方案模型 (S4)"""
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String(50), unique=True, index=True)
    name = Column(String(200), nullable=False)

    # 关联事件
    event_id = Column(Integer, ForeignKey("events.id"))
    event = relationship("Event", back_populates="plans")

    # 内容
    content_md = Column(Text)  # Markdown格式完整内容
    action_paths = Column(JSON)  # 行动路径列表
    risk_assessment = Column(JSON)  # 风险评估
    legal_basis = Column(JSON)  # 法律依据

    # 评分
    feasibility_score = Column(Float)  # 可行性得分
    risk_score = Column(Float)  # 风险得分
    overall_score = Column(Float)  # 综合得分

    # 状态
    status = Column(String(20), default="draft")  # draft, reviewed, approved
    is_optimized = Column(Boolean, default=False)  # 是否为优化版本
    parent_plan_id = Column(String(50))  # 如果是优化版本，指向原方案

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    simulations = relationship("Simulation", back_populates="plan")


class Simulation(Base):
    """推演会话 (S5)"""
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), unique=True, index=True)

    # 关联方案
    plan_id = Column(Integer, ForeignKey("plans.id"))
    plan = relationship("Plan", back_populates="simulations")

    # 配置快照 (保存启动时的完整配置)
    blue_agent_config = Column(JSON)
    red_agent_config = Column(JSON)
    judge_agent_config = Column(JSON)
    params = Column(JSON)  # {max_rounds, target_win_rate, etc}

    # 状态
    status = Column(
        Enum(SimulationStatus, values_callable=enum_values, native_enum=False),
        default=SimulationStatus.PENDING
    )
    current_round = Column(Integer, default=0)
    win_rate = Column(Float, default=50.0)

    # 统计
    total_rounds = Column(Integer, default=0)
    evidence_stats = Column(JSON)  # {pro: 0, con: 0}

    # 结果
    final_result = Column(JSON)  # 最终评估结果
    optimized_plan_id = Column(String(50))  # 优化后生成的新方案ID

    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    rounds = relationship("SimulationRound", back_populates="simulation", cascade="all, delete-orphan")


class SimulationRound(Base):
    """推演单轮记录"""
    __tablename__ = "simulation_rounds"

    id = Column(Integer, primary_key=True, index=True)

    # 关联推演
    simulation_id = Column(Integer, ForeignKey("simulations.id"))
    simulation = relationship("Simulation", back_populates="rounds")

    round_number = Column(Integer, nullable=False)

    # Blue发言
    blue_argument = Column(Text)
    blue_legal_basis = Column(JSON)  # 引用的法条

    # Red反驳
    red_argument = Column(Text)
    red_legal_basis = Column(JSON)
    red_risks_raised = Column(JSON)  # 提出的风险点

    # Judge评估
    judge_ruling = Column(Text)
    judge_score = Column(JSON)  # {blue_score, red_score, impact}

    # 该轮后的胜率变化
    win_rate_before = Column(Float)
    win_rate_after = Column(Float)
    win_rate_delta = Column(Float)


    created_at = Column(DateTime, default=datetime.utcnow)


class Law(Base):
    """法律法规模型"""
    __tablename__ = "laws"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True)  # 例如: PIPL-13
    name_zh = Column(String(200), nullable=False)
    name_en = Column(String(200))
    category = Column(String(50))  # 公司治理, 数据合规...
    level = Column(String(50))  # 公约, 国内法, 判例...
    region = Column(String(50))  # UN, CN, US...
    content = Column(Text)  # 完整内容
    summary = Column(Text)  # 摘要
    source_url = Column(String(200))

    effective_date = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow)
