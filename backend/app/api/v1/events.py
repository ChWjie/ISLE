from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.event import (
    EventCreate, EventUpdate, EventResponse, EventStats, EventType, EventStatus
)
from app.database import get_db
from app.models.database import Event
from datetime import datetime
import uuid

router = APIRouter()


@router.get("", response_model=List[EventResponse])
async def get_events(
    type: Optional[EventType] = None,
    status: Optional[EventStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取事件列表"""
    query = db.query(Event)

    # 筛选
    if type:
        query = query.filter(Event.type == type.value)
    if status:
        query = query.filter(Event.status == status.value)

    # 分页
    events = query.order_by(Event.created_at.desc()).offset(skip).limit(limit).all()
    return [EventResponse(**event.to_dict()) for event in events]


@router.get("/stats", response_model=EventStats)
async def get_event_stats(db: Session = Depends(get_db)):
    """获取事件统计"""
    events = db.query(Event).all()

    by_type = {}
    by_status = {}
    by_severity = {}

    for event in events:
        # 按类型统计
        by_type[event.type] = by_type.get(event.type, 0) + 1
        # 按状态统计
        by_status[event.status] = by_status.get(event.status, 0) + 1
        # 按严重程度统计
        severity_range = f"{(event.severity-1)//3*3+1}-{(event.severity-1)//3*3+3}"
        by_severity[severity_range] = by_severity.get(severity_range, 0) + 1

    return EventStats(
        total=len(events),
        by_type=by_type,
        by_status=by_status,
        by_severity=by_severity
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, db: Session = Depends(get_db)):
    """获取事件详情"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")
    return EventResponse(**event.to_dict())


@router.post("", response_model=EventResponse)
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """创建事件"""
    event_id = str(uuid.uuid4())
    new_event = Event(
        id=event_id,
        **event.dict(),
        status=EventStatus.PENDING.value,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return EventResponse(**new_event.to_dict())


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    event_update: EventUpdate,
    db: Session = Depends(get_db)
):
    """更新事件"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")

    update_data = event_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)

    event.updated_at = datetime.now()
    db.commit()
    db.refresh(event)
    return EventResponse(**event.to_dict())


@router.delete("/{event_id}")
async def delete_event(event_id: str, db: Session = Depends(get_db)):
    """删除事件"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")

    db.delete(event)
    db.commit()
    return {"message": "事件已删除"}
