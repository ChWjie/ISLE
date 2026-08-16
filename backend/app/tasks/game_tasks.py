import asyncio
from typing import Dict, Any
from app.core.celery_app import celery_app
from app.core.game_engine.simulator import GameSimulator, GameState
from asgiref.sync import async_to_sync

simulator = GameSimulator()

@celery_app.task
def run_game_simulation_task(session_id: str, state_dict: Dict[str, Any], plan_id: str):
    """
    Celery task wrapper for running a game simulation round.
    Since Celery is synchronous by default, we use async_to_sync for the async simulator.
    """
    # 还原 State 对象
    current_state = GameState(**state_dict)

    # 执行异步模拟
    round_result = async_to_sync(simulator.simulate_round)(current_state, f"Plan Context: {plan_id}")

    return round_result
