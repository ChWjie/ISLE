"""
Simulation API - 法律博弈推演
"""
import json
import logging
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.database import Agent, Event, Plan, Simulation, SimulationRound, SimulationStatus
from app.services.agent_prompt_service import build_retrieval_decision, build_stage_prompt, normalize_agent_type
from app.services.delilegal_client import get_delilegal_client
from app.services.llm_client import ChatMessage, get_llm_client
from app.services.optimization_service import analyze_evidence_impact, generate_optimized_plan

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/simulation", tags=["simulation"])


class SimulationStartRequest(BaseModel):
    event_id: str
    plan_id: str
    blue_agent_ids: List[str]
    red_agent_ids: List[str]
    judge_agent_id: str
    max_rounds: int = 3
    target_win_rate: float = 80.0


class SimulationStartResponse(BaseModel):
    simulation_id: str
    status: str
    message: str


class SimulationRoundRequest(BaseModel):
    round_num: int
    event_id: str
    blue_agents: List[str]
    red_agents: List[str]
    judge_agent: str
    previous_arguments: Optional[Dict[str, str]] = None


def agent_to_dict(agent: Agent) -> Dict[str, Any]:
    return {
        "agent_id": agent.agent_id,
        "name": agent.name,
        "description": agent.description,
        "stance": agent.stance,
        "goals": agent.goals,
        "system_prompt": agent.system_prompt,
        "mission": getattr(agent, "mission", ""),
        "responsibilities": getattr(agent, "responsibilities", ""),
        "knowledge_scope": getattr(agent, "knowledge_scope", []) or [],
        "agent_type": normalize_agent_type(agent.agent_type),
    }


def merge_agent_configs(agent_configs: List[Dict[str, Any]], fallback_name: str, fallback_type: str) -> Dict[str, Any]:
    if not agent_configs:
        return {
            "name": fallback_name,
            "description": "",
            "mission": "",
            "responsibilities": "",
            "stance": "",
            "system_prompt": "",
            "knowledge_scope": [],
            "agent_type": fallback_type,
        }

    names = [cfg.get("name") for cfg in agent_configs if cfg.get("name")]
    knowledge_scope: List[str] = []
    descriptions: List[str] = []
    missions: List[str] = []
    responsibilities: List[str] = []
    stances: List[str] = []
    system_prompts: List[str] = []
    for cfg in agent_configs:
        knowledge_scope.extend([str(item) for item in (cfg.get("knowledge_scope") or []) if str(item).strip()])
        for key, bucket in [
            ("description", descriptions),
            ("mission", missions),
            ("responsibilities", responsibilities),
            ("stance", stances),
            ("system_prompt", system_prompts),
        ]:
            value = str(cfg.get(key) or "").strip()
            if value:
                bucket.append(value)

    return {
        "name": " / ".join(names) if names else fallback_name,
        "description": "；".join(descriptions[:3]),
        "mission": "；".join(missions[:3]),
        "responsibilities": "；".join(responsibilities[:4]),
        "stance": "；".join(stances[:3]),
        "system_prompt": "；".join(system_prompts[:3]),
        "knowledge_scope": list(dict.fromkeys(knowledge_scope)),
        "agent_type": fallback_type,
    }


async def run_stage_stream(
    event: Event,
    stage: str,
    agent_config: Dict[str, Any],
    round_num: int,
    history: str,
    opponent_text: str = "",
    current_text: str = "",
):
    llm_client = get_llm_client()
    delilegal_client = get_delilegal_client()

    retrieval_pack = None
    retrieval_decision = build_retrieval_decision(
        stage=stage,
        event=event,
        agent=agent_config,
        opponent_text=opponent_text,
        current_text=current_text,
    )
    if retrieval_decision.enabled:
        try:
            retrieval_pack = await delilegal_client.retrieve_pack(retrieval_decision.query)
        except Exception as exc:
            logger.warning("Simulation retrieval failed for %s/%s: %s", stage, agent_config.get("name"), exc)

    prompt_bundle = build_stage_prompt(
        stage=stage,
        event=event,
        agent=agent_config,
        retrieval_pack=retrieval_pack,
        opponent_text=opponent_text,
        current_text=current_text,
        history=history,
        round_num=round_num,
    )

    stream_gen = await llm_client.chat(
        messages=[
            ChatMessage(role="system", content=prompt_bundle["system_prompt"]),
            ChatMessage(role="user", content=prompt_bundle["user_prompt"]),
        ],
        max_tokens=1800 if stage == "judge" else 1200,
        temperature=0.25 if stage == "judge" else 0.45,
        stream=True,
    )
    return stream_gen, retrieval_decision, retrieval_pack


@router.post("/start", response_model=SimulationStartResponse)
async def start_simulation(request: SimulationStartRequest, db: Session = Depends(get_db)):
    try:
        event = db.query(Event).filter(Event.event_id == request.event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail=f"Event {request.event_id} not found")

        blue_agents = db.query(Agent).filter(Agent.agent_id.in_(request.blue_agent_ids)).all()
        red_agents = db.query(Agent).filter(Agent.agent_id.in_(request.red_agent_ids)).all()
        judge_agent = db.query(Agent).filter(Agent.agent_id == request.judge_agent_id).first()

        simulation_id = f"SIM-{uuid.uuid4().hex[:8].upper()}"
        db_plan = db.query(Plan).filter(Plan.plan_id == request.plan_id).first()

        simulation = Simulation(
            session_id=simulation_id,
            plan_id=db_plan.id if db_plan else None,
            blue_agent_config=[agent_to_dict(item) for item in blue_agents],
            red_agent_config=[agent_to_dict(item) for item in red_agents],
            judge_agent_config=agent_to_dict(judge_agent) if judge_agent else {},
            params={
                "max_rounds": request.max_rounds,
                "target_win_rate": request.target_win_rate,
                "event_id": request.event_id,
            },
            status=SimulationStatus.RUNNING,
            current_round=0,
            started_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        db.add(simulation)
        db.commit()
        db.refresh(simulation)

        return SimulationStartResponse(simulation_id=simulation_id, status="started", message="推演已启动")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to start simulation: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/round/{simulation_id}")
async def execute_round(simulation_id: str, request: SimulationRoundRequest, db: Session = Depends(get_db)):
    async def event_stream():
        try:
            simulation = db.query(Simulation).filter(Simulation.session_id == simulation_id).first()
            if not simulation:
                yield json.dumps({"type": "error", "error": "Simulation not found"}) + "\n"
                return

            event = db.query(Event).filter(Event.event_id == request.event_id).first()
            if not event:
                yield json.dumps({"type": "error", "error": "Event not found"}) + "\n"
                return

            previous_arguments = request.previous_arguments or {}
            blue_last = previous_arguments.get("blue", "")
            red_last = previous_arguments.get("red", "")
            round_num = request.round_num

            past_rounds = db.query(SimulationRound).filter(
                SimulationRound.simulation_id == simulation.id,
                SimulationRound.round_number < round_num,
            ).order_by(SimulationRound.round_number).all()
            history_context = "\n".join(
                [
                    f"第{item.round_number}轮：蓝方={item.blue_argument[:120]}；红方={item.red_argument[:120]}；裁判={item.judge_ruling[:120]}"
                    for item in past_rounds
                ]
            )

            blue_config = merge_agent_configs(simulation.blue_agent_config or [], "我方律师团", "blue")
            red_config = merge_agent_configs(simulation.red_agent_config or [], "对方代理团", "red")
            judge_config = simulation.judge_agent_config or {"name": "裁判者", "agent_type": "judge"}
            judge_config["agent_type"] = normalize_agent_type(judge_config.get("agent_type") or "judge")

            yield json.dumps({"type": "status", "agent": "blue", "message": f"{blue_config['name']} 正在组织论点..."}) + "\n"
            blue_stream, blue_decision, blue_pack = await run_stage_stream(
                event=event,
                stage="debate_blue",
                agent_config=blue_config,
                round_num=round_num,
                history=history_context,
                opponent_text=red_last,
            )
            yield json.dumps({
                "type": "retrieval",
                "agent": "blue",
                "query": blue_decision.query,
                "enabled": blue_decision.enabled,
                "degraded": bool(blue_pack and blue_pack.get("degraded")),
            }) + "\n"
            blue_argument = ""
            async for chunk in blue_stream:
                if chunk:
                    blue_argument += chunk
                    yield json.dumps({"type": "blue_argument", "chunk": chunk, "round": round_num}) + "\n"
            yield json.dumps({"type": "blue_complete", "argument": blue_argument, "round": round_num}) + "\n"

            yield json.dumps({"type": "status", "agent": "red", "message": f"{red_config['name']} 正在准备抗辩..."}) + "\n"
            red_stream, red_decision, red_pack = await run_stage_stream(
                event=event,
                stage="debate_red",
                agent_config=red_config,
                round_num=round_num,
                history=history_context,
                opponent_text=blue_argument,
            )
            yield json.dumps({
                "type": "retrieval",
                "agent": "red",
                "query": red_decision.query,
                "enabled": red_decision.enabled,
                "degraded": bool(red_pack and red_pack.get("degraded")),
            }) + "\n"
            red_argument = ""
            async for chunk in red_stream:
                if chunk:
                    red_argument += chunk
                    yield json.dumps({"type": "red_argument", "chunk": chunk, "round": round_num}) + "\n"
            yield json.dumps({"type": "red_complete", "argument": red_argument, "round": round_num}) + "\n"

            yield json.dumps({"type": "status", "agent": "judge", "message": f"{judge_config.get('name', '裁判者')} 正在进行评估..."}) + "\n"
            judge_stream, judge_decision, judge_pack = await run_stage_stream(
                event=event,
                stage="judge",
                agent_config=judge_config,
                round_num=round_num,
                history=history_context,
                opponent_text=red_argument,
                current_text=blue_argument,
            )
            yield json.dumps({
                "type": "retrieval",
                "agent": "judge",
                "query": judge_decision.query,
                "enabled": judge_decision.enabled,
                "degraded": bool(judge_pack and judge_pack.get("degraded")),
            }) + "\n"
            judge_comment = ""
            async for chunk in judge_stream:
                if chunk:
                    judge_comment += chunk
                    yield json.dumps({"type": "judge_comment", "chunk": chunk, "round": round_num}) + "\n"

            previous_win_rate = simulation.win_rate if simulation.win_rate is not None else 50.0
            new_win_rate = previous_win_rate
            match = re.search(r"当前蓝方胜率[:：]\s*(\d+)%", judge_comment)
            if match:
                new_win_rate = float(match.group(1))

            win_rate_delta = new_win_rate - previous_win_rate
            opt_result = await analyze_evidence_impact(simulation_id, blue_argument, win_rate_delta, db)
            if opt_result:
                yield json.dumps({"type": "optimization_update", "data": opt_result}) + "\n"

            simulation.current_round = round_num
            simulation.win_rate = new_win_rate
            round_record = SimulationRound(
                simulation_id=simulation.id,
                round_number=round_num,
                blue_argument=blue_argument,
                red_argument=red_argument,
                judge_ruling=judge_comment,
                win_rate_before=previous_win_rate,
                win_rate_after=new_win_rate,
                win_rate_delta=win_rate_delta,
                blue_legal_basis=blue_pack.get("source_map", []) if blue_pack else [],
                red_legal_basis=red_pack.get("source_map", []) if red_pack else [],
                judge_score={"win_rate": new_win_rate},
                created_at=datetime.utcnow(),
            )
            db.add(round_record)
            db.commit()

            yield json.dumps({
                "type": "judge_complete",
                "comment": judge_comment,
                "win_rate": new_win_rate,
                "round": round_num,
            }) + "\n"

            target_win_rate = simulation.params.get("target_win_rate", 80.0) if simulation.params else 80.0
            max_rounds = simulation.params.get("max_rounds", 5) if simulation.params else 5
            is_terminated = new_win_rate >= target_win_rate or round_num >= max_rounds
            if is_terminated:
                simulation.status = SimulationStatus.COMPLETED
                simulation.total_rounds = round_num
                db.commit()
                reason = "我方胜率已达到目标" if new_win_rate >= target_win_rate else "已达到最大轮次"
                yield json.dumps({
                    "type": "termination",
                    "reason": reason,
                    "final_win_rate": new_win_rate,
                    "total_rounds": round_num,
                }) + "\n"
                return

            yield json.dumps({
                "type": "round_complete",
                "round": round_num,
                "blue_argument": blue_argument,
                "red_argument": red_argument,
                "judge_comment": judge_comment,
                "win_rate": new_win_rate,
            }) + "\n"
        except Exception as exc:
            logger.error("Round execution failed: %s", exc)
            yield json.dumps({"type": "error", "error": str(exc)}) + "\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.get("/status/{simulation_id}")
async def get_simulation_status(simulation_id: str, db: Session = Depends(get_db)):
    simulation = db.query(Simulation).filter(Simulation.session_id == simulation_id).first()
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    return {
        "simulation_id": simulation.session_id,
        "status": simulation.status,
        "current_round": simulation.current_round,
        "max_rounds": simulation.params.get("max_rounds", 5) if simulation.params else 5,
        "win_rate": simulation.win_rate,
    }


@router.post("/optimize/{simulation_id}")
async def create_optimized_plan(simulation_id: str, db: Session = Depends(get_db)):
    try:
        simulation = db.query(Simulation).filter(Simulation.session_id == simulation_id).first()
        if not simulation:
            raise HTTPException(status_code=404, detail="Simulation not found")

        result = await generate_optimized_plan(simulation_id, db)
        if isinstance(result, dict) and "event_id" not in result:
            if simulation.plan and simulation.plan.event:
                result["event_id"] = simulation.plan.event.event_id
            elif simulation.params and "event_id" in simulation.params:
                result["event_id"] = simulation.params["event_id"]
        return result
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error("Failed to generate optimized plan: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
