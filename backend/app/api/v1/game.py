from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from app.schemas.game import GameStartRequest, GameSessionResponse, GameRound, GameResult
from app.core.game_engine.simulator import GameSimulator, GameState
from app.core.connection import manager
import uuid
import random
from typing import Dict

router = APIRouter()
simulator = GameSimulator()

# 简单的内存存储 (在真实场景中应使用Redis/DB)
sessions: Dict[str, Dict] = {}

class GameStatus:
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            # 保持连接，接收客户端消息（如有）
            data = await websocket.receive_text()
            # 可以处理客户端指令，如暂停/继续
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)

@router.post("/start")
async def start_game(request: GameStartRequest):
    session_id = str(uuid.uuid4())

    # 初始化状态
    initial_state = simulator.initialize_state(session_id)

    # 加载方案数据
    plan_content = ""
    if request.plan_id:
        from app.api.v1.plans import mock_plans
        if request.plan_id in mock_plans:
            plan = mock_plans[request.plan_id]
            plan_content = plan.content

    sessions[session_id] = {
        "id": session_id,
        "event_id": request.event_id,
        "plan_id": request.plan_id,
        "plan_content": plan_content,
        "status": GameStatus.RUNNING,
        "rounds": [],
        "state": initial_state, # 存储GameState对象
        "result": None,
        "max_rounds": request.max_rounds or 10,
        # 存储双方智能体配置
        "our_agent_config": request.our_agent_config,
        "opponent_agent_config": request.opponent_agent_config
    }

    return {
        "session_id": session_id,
        "status": "active",
        "current_round": 0,
        "message": "博弈推演已启动 (Rule Engine + WebSocket Ready)",
        "plan_loaded": bool(plan_content)
    }

@router.get("/{session_id}")
async def get_game_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    # 将GameState对象转换为dict以便JSON序列化
    session = sessions[session_id].copy()
    if isinstance(session.get("state"), GameState):
        session["state"] = session["state"].dict()

    return session

@router.post("/{session_id}/round")
async def execute_round(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    if session["status"] != GameStatus.RUNNING:
         return {"status": session["status"], "message": "Game not running", "round": None}

    # 获取当前状态
    current_state: GameState = session["state"]

    # 执行推演，传递智能体配置和方案内容
    round_result = await simulator.simulate_round(
        current_state,
        session.get("plan_content", ""),
        our_agent_config=session.get("our_agent_config"),
        opponent_agent_config=session.get("opponent_agent_config")
    )

    # 更新会话记录
    session["rounds"].append(round_result)

    # 检查是否结束
    if round_result["is_terminated"]:
        session["status"] = GameStatus.COMPLETED

    # WebSocket广播更新
    await manager.broadcast({
        "type": "round_update",
        "data": round_result,
        "status": session["status"]
    }, session_id)

    return {
        "status": session["status"],
        "round": round_result
    }

@router.get("/{session_id}/result", response_model=GameResult)
async def get_game_result(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    state: GameState = session["state"]

    # 评估结果
    evaluation = simulator.evaluate_result(state)

    session["result"] = evaluation

    return GameResult(
        session_id=session_id,
        total_rounds=len(session["rounds"]),
        outcome=evaluation["outcome"],
        risk_score=evaluation["risk_score"],
        recommendations=["建议参考行动详情中的风险提示"],
        summary=evaluation["details"]
    )
