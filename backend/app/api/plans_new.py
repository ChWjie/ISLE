"""
Plans API Routes - 方案生成与整合
"""
import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.database import Agent, Event, Plan
from app.schemas.plan import PlanGenerateRequest
from app.services.agent_prompt_service import build_retrieval_decision, build_stage_prompt, normalize_agent_type
from app.services.delilegal_client import get_delilegal_client
from app.services.llm_client import ChatMessage, get_llm_client

router = APIRouter(prefix="/api/v1/plans", tags=["plans"])
logger = logging.getLogger(__name__)


async def analyze_agent_stream(agent: Agent, prompt_bundle: Dict[str, str]):
    """单个智能体分析（流式）"""
    try:
        llm_client = get_llm_client()
        yield json.dumps({
            "type": "status",
            "agent_id": agent.agent_id,
            "agent_name": agent.name,
            "status": "running",
        }) + "\n"

        messages = [
            ChatMessage(role="system", content=prompt_bundle["system_prompt"]),
            ChatMessage(role="user", content=prompt_bundle["user_prompt"]),
        ]

        full_response = ""
        stream_gen = await llm_client.chat(
            messages=messages,
            max_tokens=2500,
            temperature=0.35,
            stream=True,
        )

        async for chunk in stream_gen:
            if chunk:
                full_response += chunk
                yield json.dumps({
                    "type": "content",
                    "agent_id": agent.agent_id,
                    "chunk": chunk,
                }) + "\n"

        yield json.dumps({
            "type": "complete",
            "agent_id": agent.agent_id,
            "agent_name": agent.name,
            "agent_type": normalize_agent_type(agent.agent_type),
            "status": "completed",
            "analysis": full_response,
        }) + "\n"
    except Exception as exc:
        logger.error("Agent %s analysis failed: %s", agent.agent_id, exc)
        yield json.dumps({
            "type": "error",
            "agent_id": agent.agent_id,
            "agent_name": agent.name,
            "error": str(exc),
        }) + "\n"


async def generate_plan_stream(event_id: str, agent_ids: List[str], db: Session):
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        yield json.dumps({"type": "error", "message": "Event not found"}) + "\n"
        return

    agents = db.query(Agent).filter(Agent.agent_id.in_(agent_ids)).all()
    if not agents:
        yield json.dumps({"type": "error", "message": "No agents found"}) + "\n"
        return

    delilegal_client = get_delilegal_client()
    logger.info("Starting analysis for event %s with %s agents", event_id, len(agents))

    message_queue: asyncio.Queue[Optional[str]] = asyncio.Queue()

    async def run_agent(agent: Agent):
        retrieval_pack = None
        retrieval_decision = build_retrieval_decision("analysis", event, agent=agent)
        await message_queue.put(json.dumps({
            "type": "retrieval",
            "phase": "start",
            "agent_id": agent.agent_id,
            "agent_name": agent.name,
            "enabled": retrieval_decision.enabled,
            "query": retrieval_decision.query,
            "reason": retrieval_decision.reason,
            "retrieval_types": ["case", "law"],
        }) + "\n")
        if retrieval_decision.enabled:
            try:
                retrieval_pack = await delilegal_client.retrieve_pack(retrieval_decision.query)
            except Exception as exc:
                logger.warning("Analysis retrieval failed for %s: %s", agent.agent_id, exc)

        await message_queue.put(json.dumps({
            "type": "retrieval",
            "agent_id": agent.agent_id,
            "agent_name": agent.name,
            "enabled": retrieval_decision.enabled,
            "query": retrieval_decision.query,
            "reason": retrieval_decision.reason,
            "phase": "complete",
            "retrieval_types": ["case", "law"],
            "case_count": len(retrieval_pack.get("cases", [])) if retrieval_pack else 0,
            "law_count": len(retrieval_pack.get("laws", [])) if retrieval_pack else 0,
            "degraded": bool(retrieval_pack and retrieval_pack.get("degraded")),
            "source_map": retrieval_pack.get("source_map", []) if retrieval_pack else [],
        }) + "\n")

        prompt_bundle = build_stage_prompt(
            stage="analysis",
            event=event,
            agent=agent,
            retrieval_pack=retrieval_pack,
        )
        async for message in analyze_agent_stream(agent, prompt_bundle):
            await message_queue.put(message)

        await message_queue.put(None)

    tasks = [asyncio.create_task(run_agent(agent)) for agent in agents]
    completed_workers = 0

    try:
        while completed_workers < len(tasks):
            message = await message_queue.get()
            if message is None:
                completed_workers += 1
                continue
            yield message
    finally:
        await asyncio.gather(*tasks, return_exceptions=True)


class PlanCreateRequest(BaseModel):
    event_id: str
    title: str
    content: str
    action_paths: List[dict] = []


@router.get("")
async def list_plans(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Plan)
    if status and status != "all":
        query = query.filter(Plan.status == status)

    plans = query.order_by(Plan.created_at.desc()).offset(skip).limit(limit).all()
    result = []
    for plan in plans:
        event_desc = ""
        if plan.event:
            event_desc = plan.event.description or plan.event.fact_summary or ""
        result.append({
            "id": plan.id,
            "plan_id": plan.plan_id,
            "title": plan.name,
            "status": plan.status,
            "risk_score": plan.risk_score or 0,
            "created_at": plan.created_at,
            "event_description": event_desc,
            "event_id": plan.event.event_id if plan.event else None,
            "event_name": plan.event.name if plan.event else "Unknown Event",
        })
    return result


@router.get("/{plan_id}")
async def get_plan(plan_id: str, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.plan_id == plan_id).first()
    if not plan and plan_id.isdigit():
        plan = db.query(Plan).filter(Plan.id == int(plan_id)).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    return {
        "id": plan.id,
        "plan_id": plan.plan_id,
        "title": plan.name,
        "status": plan.status,
        "content": plan.content_md,
        "risk_score": plan.risk_score,
        "created_at": plan.created_at,
        "action_paths": plan.action_paths or [],
        "risk_assessment": plan.risk_assessment or {},
        "legal_basis": plan.legal_basis or {},
        "event": {
            "id": plan.event.id,
            "event_id": plan.event.event_id,
            "name": plan.event.name,
            "description": plan.event.description,
        } if plan.event else None,
    }


@router.delete("/{plan_id}")
async def delete_plan(plan_id: str, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.plan_id == plan_id).first()
    if not plan and plan_id.isdigit():
        plan = db.query(Plan).filter(Plan.id == int(plan_id)).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    db.delete(plan)
    db.commit()
    return {"message": "Plan deleted successfully"}


@router.post("/generate")
async def generate_plan(request: PlanGenerateRequest, db: Session = Depends(get_db)):
    async def event_stream():
        async for chunk in generate_plan_stream(request.event_id, request.agent_ids, db):
            yield chunk

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.post("/integrate")
async def integrate_plan(request: dict, db: Session = Depends(get_db)):
    event_id = request.get("event_id")
    agent_analyses = request.get("agent_analyses", [])
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        return {"error": "Event not found"}

    analyses_summary = "\n\n".join(
        [
            f"### {item.get('agent_name', '未命名智能体')} ({normalize_agent_type(item.get('agent_type'))})\n{item.get('analysis', '')}"
            for item in agent_analyses
        ]
    )

    prompt_bundle = build_stage_prompt(
        stage="integration",
        event=event,
        agent={"name": "综合整合智能体", "agent_type": "analyst", "knowledge_scope": event.legal_systems or []},
        analyses_summary=analyses_summary,
    )

    async def event_stream():
        try:
            llm_client = get_llm_client()
            yield json.dumps({"type": "start", "message": "开始整合多智能体分析结果"}) + "\n"
            stream_gen = await llm_client.chat(
                messages=[
                    ChatMessage(role="system", content=prompt_bundle["system_prompt"]),
                    ChatMessage(role="user", content=prompt_bundle["user_prompt"]),
                ],
                max_tokens=1800,
                temperature=0.3,
                stream=True,
            )

            full_response = ""
            async for chunk in stream_gen:
                if chunk:
                    full_response += chunk
                    yield json.dumps({"type": "content", "chunk": chunk}) + "\n"

            yield json.dumps({"type": "complete", "content": full_response}) + "\n"
        except Exception as exc:
            logger.error("Plan integration failed: %s", exc)
            yield json.dumps({"type": "error", "error": str(exc)}) + "\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.post("/save")
async def create_plan(request: PlanCreateRequest, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.event_id == request.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    plan_id = f"PLAN-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    new_plan = Plan(
        plan_id=plan_id,
        name=request.title,
        event_id=event.id,
        content_md=request.content,
        action_paths=request.action_paths or [],
        status="draft",
        created_at=datetime.utcnow(),
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)

    logger.info("Created plan %s for event %s", plan_id, request.event_id)
    return {"plan_id": new_plan.plan_id, "message": "Plan saved successfully"}
