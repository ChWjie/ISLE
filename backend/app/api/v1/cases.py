from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database import Case
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter()

# Pydantic schemas
class CaseCreate(BaseModel):
    case_id: str
    title: str
    event_type: Optional[str] = None
    event_description: Optional[str] = None
    location: Optional[Dict] = None
    parties: Optional[List[str]] = None
    plan_data: Optional[Dict] = None
    simulation_id: Optional[str] = None
    total_rounds: Optional[int] = None
    rounds_data: Optional[List[Dict]] = None
    final_outcome: Optional[str] = None
    risk_score: Optional[float] = None
    final_state: Optional[Dict] = None
    agents_config: Optional[List[Dict]] = None
    created_by: Optional[str] = "system"
    is_public: Optional[bool] = False

class SavePlanRequest(BaseModel):
    event_id: str
    title: str
    event_type: str
    event_description: str
    location: Optional[Dict] = None
    parties: Optional[List[str]] = None
    plan_data: Dict  # Contains sections array from S4


@router.post("/save-plan", response_model=dict)
async def save_plan(request: SavePlanRequest, db: Session = Depends(get_db)):
    """
    保存S4生成的法律方案到数据库
    """
    import uuid
    # 生成唯一case_id
    case_id = f"PLAN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"

    # 创建Case记录
    new_case = Case(
        case_id=case_id,
        title=request.title,
        event_type=request.event_type,
        event_description=request.event_description,
        location=request.location,
        parties=request.parties,
        plan_data=request.plan_data,
        created_by='user',
        is_public=True
    )

    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    return {
        "success": True,
        "case_id": new_case.case_id,
        "message": "方案已成功保存到方案库"
    }


@router.post("", response_model=dict)
async def save_case(case_data: CaseCreate, db: Session = Depends(get_db)):
    """保存推演案例"""
    # Check if case_id already exists
    existing = db.query(Case).filter(Case.case_id == case_data.case_id).first()
    if existing:
        # Update existing case
        for key, value in case_data.dict().items():
            setattr(existing, key, value)
        existing.updated_at = datetime.now()
        db.commit()
        db.refresh(existing)
        return existing.to_dict()

    # Create new case
    case = Case(**case_data.dict())
    db.add(case)
    db.commit()
    db.refresh(case)
    return case.to_dict()


@router.get("", response_model=List[dict])
async def get_cases(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取案例列表"""
    query = db.query(Case)

    if event_type:
        query = query.filter(Case.event_type == event_type)

    cases = query.order_by(Case.created_at.desc()).offset(skip).limit(limit).all()
    return [case.to_dict() for case in cases]


@router.get("/{case_id}")
async def get_case(case_id: str, db: Session = Depends(get_db)):
    """获取单个案例详情"""
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Increment views
    case.views += 1
    db.commit()

    return case.to_dict()


@router.delete("/{case_id}")
async def delete_case(case_id: str, db: Session = Depends(get_db)):
    """删除案例"""
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    db.delete(case)
    db.commit()
    return {"message": "Case deleted successfully"}
