"""
Agents API - CRUD operations for intelligent agents
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database import Agent
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

router = APIRouter()

# Pydantic schemas
class AgentBase(BaseModel):
    name: str
    type: Optional[str] = None
    model: Optional[str] = None
    avatar: Optional[str] = None
    law_domains: Optional[List[str]] = None
    description: Optional[str] = None
    level: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    model: Optional[str] = None
    avatar: Optional[str] = None
    law_domains: Optional[List[str]] = None
    description: Optional[str] = None
    level: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class AgentResponse(AgentBase):
    id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[dict])
async def get_agents(
    type: Optional[str] = Query(None, description="Filter by type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取智能体列表"""
    query = db.query(Agent)

    if type:
        query = query.filter(Agent.type == type)

    agents = query.order_by(Agent.created_at.desc()).offset(skip).limit(limit).all()
    return [agent.to_dict() for agent in agents]


@router.get("/{agent_id}")
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """获取单个智能体详情"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.to_dict()


@router.post("", response_model=dict)
async def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """创建智能体"""
    agent_id = str(uuid.uuid4())
    agent = Agent(
        id=agent_id,
        **agent_data.dict()
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent.to_dict()


@router.put("/{agent_id}", response_model=dict)
async def update_agent(
    agent_id: str,
    agent_update: AgentUpdate,
    db: Session = Depends(get_db)
):
    """更新智能体"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    update_data = agent_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    agent.updated_at = datetime.now()
    db.commit()
    db.refresh(agent)
    return agent.to_dict()


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """删除智能体"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    db.delete(agent)
    db.commit()
    return {"message": "Agent deleted successfully"}
