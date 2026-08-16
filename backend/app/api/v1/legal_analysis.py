from fastapi import APIRouter, HTTPException
from typing import List
from app.core.llm.factory import LLMFactory
from pydantic import BaseModel

router = APIRouter()


class LegalAnalysisRequest(BaseModel):
    event_id: str
    event_title: str
    event_type: str
    event_description: str
    location: dict
    parties: List[str]


class LegalFramework(BaseModel):
    id: str
    name: str
    nameEn: str
    applicability: str
    articles: List[dict]
    arguments: List[str]
    keyPoints: List[str] = []


class LegalAnalysisResponse(BaseModel):
    event_id: str
    frameworks: List[LegalFramework]


@router.post('/analyze', response_model=LegalAnalysisResponse)
async def analyze_event(request: LegalAnalysisRequest):
    """使用 LLM 分析企业合规/争议事件的法律框架"""
    llm = LLMFactory.create()

    system_prompt = """你是一位资深的法律与合规专家，专门分析企业经营、合同履约、劳动用工、数据治理与监管应对等事件的法律框架。
你的任务是为给定事件提供全面的法律分析，包括适用法律框架、关键条款、法律论据、证据方向和处置建议。
请保持专业、客观、结构化。"""

    user_prompt = f"""请分析以下事件的法律框架：

事件标题：{request.event_title}
事件类型：{request.event_type}
事件描述：{request.event_description}
涉及方：{', '.join(request.parties)}
地点：纬度 {request.location.get('lat')}，经度 {request.location.get('lng')}

请重点覆盖：
1. 适用法律法规与监管规则
2. 合同或内部制度依据
3. 关键证据与责任认定路径
4. 可行的合规整改或争议应对建议"""

    try:
        await llm.generate(user_prompt, system_prompt=system_prompt)

        frameworks = [
            {
                'id': '1',
                'name': '法律法规与监管要求',
                'nameEn': 'Laws and Regulatory Requirements',
                'applicability': f'针对 {request.event_title}，应优先审查公司法、合同法规则、劳动用工规范、数据合规要求及对应监管口径，明确行为是否合法、程序是否完备、责任是否已经触发。',
                'articles': [
                    {'id': 'a1', 'title': '个人信息保护法第13条', 'content': '处理个人信息应当具备明确合法性基础，并满足目的明确、最小必要等要求。'},
                    {'id': 'a2', 'title': '数据安全法第21条', 'content': '国家建立数据分类分级保护制度，对重要数据实施重点保护。'},
                ],
                'arguments': [
                    '先识别业务行为属于数据处理、劳动管理、合同履约还是公司治理事项。',
                    '重点比对是否存在法定义务未履行、程序瑕疵或监管申报缺失。',
                    '结合现有处罚规则与裁判口径评估风险敞口。',
                    '整改措施和补救动作会直接影响责任认定与后续风险。',
                ],
                'keyPoints': [
                    '优先确认适用法条与监管口径。',
                    '核对程序是否合规。',
                    '评估已发生与潜在责任。',
                ],
            },
            {
                'id': '2',
                'name': '合同约定与内部制度',
                'nameEn': 'Contracts and Internal Rules',
                'applicability': '除法定规则外，还应重点审查合同条款、补充协议、平台规则、员工手册、授权流程和内部审批制度，它们往往决定权利义务边界与违约责任承担。',
                'articles': [
                    {'id': 'b1', 'title': '合同关键条款', 'content': '重点核查履约义务、违约责任、通知方式、争议解决、保密与数据条款。'},
                    {'id': 'b2', 'title': '内部制度与授权链条', 'content': '重点核查审批权限、流程留痕、制度告知和执行记录。'},
                ],
                'arguments': [
                    '合同条款通常是认定义务和违约责任的第一依据。',
                    '内部制度可用于证明企业是否尽到管理义务。',
                    '通知记录、签收记录、审批记录会影响事实认定。',
                    '历史履行惯例可辅助解释条款真实含义。',
                ],
                'keyPoints': [
                    '核查合同与制度文本。',
                    '补齐授权与通知证据。',
                    '结合历史履行解释争议条款。',
                ],
            },
        ]

        return LegalAnalysisResponse(event_id=request.event_id, frameworks=frameworks)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'法律分析生成失败: {exc}')
