"""
Event API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.base import BaseResponse
from app.schemas.event import EventCreate, EventResponse
from app.models.database import Event

router = APIRouter(prefix="/api/v1/events", tags=["events"])


@router.get("", response_model=BaseResponse[List[EventResponse]])
async def list_events(db: Session = Depends(get_db)):
    """获取事件列表"""
    import json
    events = db.query(Event).all()

    # 转换JSON字符串字段为列表
    event_list = []
    for e in events:
        event_dict = {
            "id": e.id,
            "event_id": e.event_id,
            "name": e.name,
            "description": e.description,
            "dispute_type": e.dispute_type,
            "our_side": json.loads(e.our_side) if isinstance(e.our_side, str) else e.our_side,
            "opponent_side": json.loads(e.opponent_side) if isinstance(e.opponent_side, str) else e.opponent_side,
            "legal_systems": json.loads(e.legal_systems) if isinstance(e.legal_systems, str) else e.legal_systems,
            "fact_summary": e.fact_summary,
            "created_at": e.created_at,
            "updated_at": e.updated_at,
            "opponent_stance_preset": e.opponent_stance_preset,
            "opponent_claims_options": json.loads(e.opponent_claims_options) if isinstance(e.opponent_claims_options, str) else e.opponent_claims_options,
            "opponent_legal_system": e.opponent_legal_system
        }
        event_list.append(EventResponse(**event_dict))

    return BaseResponse(data=event_list)


@router.get("/{event_id}", response_model=BaseResponse[EventResponse])
async def get_event(event_id: str, db: Session = Depends(get_db)):
    """获取单个事件"""
    import json
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event_dict = {
        "id": event.id,
        "event_id": event.event_id,
        "name": event.name,
        "description": event.description,
        "dispute_type": event.dispute_type,
        "our_side": json.loads(event.our_side) if isinstance(event.our_side, str) else event.our_side,
        "opponent_side": json.loads(event.opponent_side) if isinstance(event.opponent_side, str) else event.opponent_side,
        "legal_systems": json.loads(event.legal_systems) if isinstance(event.legal_systems, str) else event.legal_systems,
        "fact_summary": event.fact_summary,
            "created_at": event.created_at,
        "updated_at": event.updated_at,
        "opponent_stance_preset": event.opponent_stance_preset,
        "opponent_claims_options": json.loads(event.opponent_claims_options) if isinstance(event.opponent_claims_options, str) else event.opponent_claims_options,
        "opponent_legal_system": event.opponent_legal_system
    }
    return BaseResponse(data=EventResponse(**event_dict))


@router.post("", response_model=BaseResponse[EventResponse])
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """创建事件"""
    new_event = Event(**event.dict())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return BaseResponse(data=EventResponse.from_orm(new_event))
