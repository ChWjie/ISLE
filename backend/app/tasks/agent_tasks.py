from typing import List, Dict, Any
from app.core.celery_app import celery_app
from app.core.llm.factory import LLMFactory
from asgiref.sync import async_to_sync

llm_factory = LLMFactory()

@celery_app.task
def analyze_law_task(question: str, context: str):
    """
    异步法律分析任务
    """
    llm = llm_factory.create()

    prompt = f"请详细分析以下法律问题：\n{question}\n\n背景信息：\n{context}"
    system_prompt = "你是一个资深法律与合规专家，请出具专业的法律意见书。"

    result = async_to_sync(llm.generate)(prompt, system_prompt=system_prompt)
    return result

@celery_app.task
def agent_think_task(agent_name: str, agent_role: str, task_description: str):
    """
    智能体思考任务
    """
    llm = llm_factory.create()

    prompt = f"任务：{task_description}"
    system_prompt = f"你是一名为 {agent_name} 的 {agent_role}。请根据你的专业背景进行分析。"

    result = async_to_sync(llm.generate)(prompt, system_prompt=system_prompt)
    return result
