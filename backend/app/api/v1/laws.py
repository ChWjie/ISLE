from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database import Law
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Pydantic schemas
class LawBase(BaseModel):
    code: str
    name_zh: str
    name_en: Optional[str] = None
    category: str
    content: str
    summary: Optional[str] = None
    source: Optional[str] = None
    tags: Optional[List[str]] = None

class LawCreate(LawBase):
    pass

class LawResponse(LawBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[dict])
async def get_laws(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in name and content"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取法律列表"""
    query = db.query(Law)

    if category:
        query = query.filter(Law.category == category)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Law.name_zh.like(search_pattern)) |
            (Law.content.like(search_pattern))
        )

    laws = query.offset(skip).limit(limit).all()
    return [law.to_dict() for law in laws]


@router.get("/{code}")
async def get_law(code: str, db: Session = Depends(get_db)):
    """获取单个法律条文"""
    law = db.query(Law).filter(Law.code == code).first()
    if not law:
        raise HTTPException(status_code=404, detail="Law not found")
    return law.to_dict()


@router.post("", response_model=dict)
async def create_law(law_data: LawCreate, db: Session = Depends(get_db)):
    """添加法律条文"""
    # Check if code already exists
    existing = db.query(Law).filter(Law.code == law_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Law code already exists")

    law = Law(**law_data.dict())
    db.add(law)
    db.commit()
    db.refresh(law)
    return law.to_dict()


@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """获取所有法律分类"""
    categories = db.query(Law.category).distinct().all()
    return [cat[0] for cat in categories]
