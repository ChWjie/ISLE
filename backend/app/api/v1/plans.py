from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
import uuid

router = APIRouter()


class PlanBase(BaseModel):
    """方案基础模型"""
    event_id: str
    title: str
    content: str
    analysis_results: List[dict] = []


class PlanResponse(PlanBase):
    """方案响应"""
    id: str
    status: str  # draft/pending_approval/approved/deployed
    created_at: datetime
    updated_at: datetime


# 模拟方案存储
mock_plans = {}


@router.get("", response_model=List[PlanResponse])
async def get_plans():
    """获取方案列表"""
    return list(mock_plans.values())


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(plan_id: str):
    """获取方案详情"""
    if plan_id not in mock_plans:
        return {"error": "方案不存在"}
    return mock_plans[plan_id]


@router.post("", response_model=PlanResponse)
async def create_plan(plan: PlanBase):
    """创建方案"""
    plan_id = str(uuid.uuid4())
    plan_data = PlanResponse(
        id=plan_id,
        **plan.dict(),
        status="draft",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_plans[plan_id] = plan_data
    return plan_data


@router.put("/{plan_id}", response_model=PlanResponse)
async def update_plan(plan_id: str, plan: PlanBase):
    """更新方案"""
    if plan_id not in mock_plans:
        return {"error": "方案不存在"}

    plan_data = mock_plans[plan_id]
    for key, value in plan.dict().items():
        setattr(plan_data, key, value)
    plan_data.updated_at = datetime.now()

    return plan_data


from app.core.llm.factory import LLMFactory
from app.config import get_settings

class PlanGenerationRequest(BaseModel):
    event_id: str
    agent_results: List[dict] # 包含agent_id, analysis, recommendations等

@router.post("/generate", response_model=PlanResponse)
async def generate_plan(request: PlanGenerationRequest):
    """S4: 生成初步方案 (调用真实LLM)"""
    settings = get_settings()
    llm = LLMFactory.create(provider=settings.LLM_PROVIDER)

    # 构建 Prompt
    agent_opinions = ""
    for res in request.agent_results:
        agent_opinions += f"""
        【{res.get('agent_name', '专家')}意见】
        - 分析: {res.get('analysis')}
        - 建议: {', '.join(res.get('recommendations', []))}
        """

    system_prompt = """你是一个国家级法律应对方案撰写专家。请基于多位领域专家的研判意见，整合生成一份结构化的初步法律应对方案。
    方案必须包含以下部分：
    1. 核心定性：对事件性质的法律定性。
    2. 总体策略：外交、法律、舆论三位一体的总体指导思想。
    3. 具体行动建议：
       - 外交层面
       - 法律层面
       - 舆论层面
       - 军事/执法层面
    4. 预期效果与风险预估。

    输出风格：专业、严谨、条理清晰。直接输出Markdown格式的内容。
    """

    user_prompt = f"""专家意见汇总如下：
    {agent_opinions}

    请据此生成初步应对方案。"""

    print(f"Start generating plan for event {request.event_id} with {len(request.agent_results)} agent results...")
    try:
        content = await llm.generate(user_prompt, system_prompt)
    except Exception as e:
        print(f"LLM Generation Failed: {e}")
        # Return a fallback or re-raise
        raise HTTPException(status_code=500, detail=f"LLM生成失败: {str(e)}")

    # 创建方案记录
    plan_id = str(uuid.uuid4())
    plan_data = PlanResponse(
        id=plan_id,
        event_id=request.event_id,
        title="法律应对初步方案 (智能生成)",
        content=content,
        analysis_results=request.agent_results,
        status="draft",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_plans[plan_id] = plan_data
    return plan_data

@router.post("/{plan_id}/optimize", response_model=PlanResponse)
async def optimize_plan(plan_id: str, game_result: dict):
    """S6: 基于博弈结果优化方案"""
    if plan_id not in mock_plans:
        return {"error": "方案不存在"}

    plan = mock_plans[plan_id]
    settings = get_settings()
    llm = LLMFactory.create(provider=settings.LLM_PROVIDER)

    system_prompt = """你是一个资深战略规划专家。请基于博弈推演的复盘结果，对原有的法律应对方案进行迭代优化。
    重点关注：
    1. 推演中暴露的风险点（如被对手反制、舆论失控等）。
    2. 针对性补充补救措施或调整行动力度。
    3. 保持原有方案骨架，但在具体措施上更加完善。
    """

    user_prompt = f"""原方案内容：
    {plan.content}

    博弈推演结果摘要：
    - 最终结果: {game_result.get('outcome')}
    - 风险评分: {game_result.get('risk_score')}
    - 结束原因/复盘: {game_result.get('summary')}

    请生成优化后的方案版本。"""

    optimized_content = await llm.generate(user_prompt, system_prompt)

    # 更新方案
    plan.content = optimized_content
    plan.status = "optimized"
    plan.updated_at = datetime.now()

    return plan

@router.post("/{plan_id}/approve")
async def approve_plan(plan_id: str):
    """签发方案"""
    if plan_id not in mock_plans:
        return {"error": "方案不存在"}

    plan = mock_plans[plan_id]
    plan.status = "approved"
    plan.updated_at = datetime.now()

    return {"message": "方案已签发", "plan_id": plan_id}


@router.post("/{plan_id}/deploy")
async def deploy_plan(plan_id: str):
    """部署方案"""
    if plan_id not in mock_plans:
        return {"error": "方案不存在"}

    plan = mock_plans[plan_id]
    plan.status = "deployed"
    plan.updated_at = datetime.now()

    return {"message": "方案已部署", "plan_id": plan_id}
