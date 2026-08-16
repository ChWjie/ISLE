from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.models.database import Law
from app.database import get_db

router = APIRouter()

# --- Pydantic Models ---

class LawBase(BaseModel):
    code: str
    name_zh: str
    name_en: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    region: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    effective_date: Optional[datetime] = None

class LawOut(LawBase):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Endpoints ---

@router.get("", response_model=List[LawOut])
async def list_laws(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取法律列表，支持分类筛选和关键词搜索"""
    query = db.query(Law)

    if category:
        query = query.filter(Law.category == category)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Law.name_zh.like(search_term),
                Law.content.like(search_term),
                Law.code.like(search_term)
            )
        )

    laws = query.offset(skip).limit(limit).all()
    return laws


@router.get("/{code}", response_model=LawOut)
async def get_law(
    code: str,
    db: Session = Depends(get_db)
):
    """根据编号获取法律详情"""
    law = db.query(Law).filter(Law.code == code).first()
    if not law:
        raise HTTPException(status_code=404, detail="Law not found")
    return law


@router.get("/categories/list")
async def list_categories(
    db: Session = Depends(get_db)
):
    """获取所有已存在的分类"""
    # Simply return distinct categories
    results = db.query(Law.category).distinct().all()
    categories = [r[0] for r in results if r[0]]
    return categories
