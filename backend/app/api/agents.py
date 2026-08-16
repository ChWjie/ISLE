"""
Agent API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.base import BaseResponse
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse, AgentTemplate
from app.services.agent_service import AgentService
from app.models.database import AgentType

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


@router.post("", response_model=BaseResponse[AgentResponse])
async def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    """创建Agent"""
    try:
        created_agent = AgentService.create_agent(db, agent)
        return BaseResponse(data=AgentResponse.from_orm(created_agent))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=BaseResponse[List[AgentResponse]])
async def list_agents(
    agent_type: Optional[AgentType] = None,
    event_id: Optional[int] = None,
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """获取Agent列表"""
    agents = AgentService.list_agents(db, agent_type, event_id, is_active)
    return BaseResponse(data=[AgentResponse.from_orm(a) for a in agents])


@router.get("/templates", response_model=BaseResponse[List[AgentTemplate]])
async def get_templates(agent_type: Optional[str] = None):
    """获取Agent模板"""
    templates = AgentService.get_templates(agent_type)
    return BaseResponse(data=templates)


@router.get("/{agent_id}", response_model=BaseResponse[AgentResponse])
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """获取单个Agent"""
    agent = AgentService.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return BaseResponse(data=AgentResponse.from_orm(agent))


@router.put("/{agent_id}", response_model=BaseResponse[AgentResponse])
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    db: Session = Depends(get_db)
):
    """更新Agent"""
    updated_agent = AgentService.update_agent(db, agent_id, agent_data)
    if not updated_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return BaseResponse(data=AgentResponse.from_orm(updated_agent))


@router.delete("/{agent_id}", response_model=BaseResponse[dict])
async def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """删除Agent"""
    success = AgentService.delete_agent(db, agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return BaseResponse(data={"deleted": True})
