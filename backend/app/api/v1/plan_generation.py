from fastapi import APIRouter
from typing import List
from app.core.llm.factory import LLMFactory
from pydantic import BaseModel
import asyncio
from datetime import datetime

router = APIRouter()


class PlanGenerationRequest(BaseModel):
    event_id: str
    event_title: str
    event_type: str
    event_description: str
    location: dict
    parties: List[str]
    agent_configs: List[dict] = []


class AnalysisSection(BaseModel):
    title: str
    content: str
    key_points: List[str]


class PlanGenerationResponse(BaseModel):
    event_id: str
    sections: List[AnalysisSection]
    generated_at: str


@router.post('/generate', response_model=PlanGenerationResponse)
async def generate_plan(request: PlanGenerationRequest):
    """使用 LLM 生成企业合规/争议应对分析方案"""
    llm = LLMFactory.create()

    analysis_directions = [
        {
            'title': '适用法律框架分析',
            'prompt': f'''作为法律与合规专家，请分析以下事件的适用法律框架：\n\n事件：{request.event_title}\n类型：{request.event_type}\n描述：{request.event_description}\n涉及方：{', '.join(request.parties)}\n\n请说明适用法律法规、监管要求、内部制度和合同依据。'''
        },
        {
            'title': '核心争议焦点',
            'prompt': f'''作为法律与合规专家，请分析以下事件的核心争议焦点：\n\n事件：{request.event_title}\n类型：{request.event_type}\n描述：{request.event_description}\n涉及方：{', '.join(request.parties)}\n\n请识别双方主张、关键分歧、责任认定难点与可能的争议升级点。'''
        },
        {
            'title': '证据与责任认定',
            'prompt': f'''作为法律与合规专家，请分析以下事件中证据与责任认定路径：\n\n事件：{request.event_title}\n类型：{request.event_type}\n描述：{request.event_description}\n涉及方：{', '.join(request.parties)}\n\n请说明需要补强的证据、证明责任分配和事实认定重点。'''
        },
        {
            'title': '处置与优化建议',
            'prompt': f'''作为法律与合规专家，请给出以下事件的处置与优化建议：\n\n事件：{request.event_title}\n类型：{request.event_type}\n描述：{request.event_description}\n涉及方：{', '.join(request.parties)}\n\n请给出短期应对、中期整改和长期制度优化建议。'''
        }
    ]

    async def generate_section(direction: dict) -> AnalysisSection:
        try:
            system_prompt = '''你是一位资深的法律与合规专家，精通公司治理、劳动用工、数据合规、合同争议和监管应对等领域。
请输出专业、客观、结构化的分析内容，并在最后列出若干关键要点（以 - 开头）。'''
            response = await llm.generate(direction['prompt'], system_prompt=system_prompt)

            lines = response.strip().split('\n')
            content_lines = []
            key_points = []
            in_key_points = False

            for raw_line in lines:
                line = raw_line.strip()
                if not line:
                    continue
                if '关键要点' in line or '要点' in line:
                    in_key_points = True
                    continue
                if in_key_points and (line.startswith('-') or line.startswith('*')):
                    key_points.append(line.lstrip('-* '))
                else:
                    if not in_key_points:
                        content_lines.append(line)

            if not key_points:
                key_points = [
                    '识别适用法律法规与内部规则。',
                    '梳理证据链与责任链。',
                    '形成可执行的整改与应对方案。',
                ]

            return AnalysisSection(
                title=direction['title'],
                content='\n'.join(content_lines) or response,
                key_points=key_points[:5],
            )
        except Exception:
            return AnalysisSection(
                title=direction['title'],
                content=f'正在分析 {direction["title"]} ...',
                key_points=['分析进行中', '请稍后刷新'],
            )

    sections = await asyncio.gather(*[generate_section(direction) for direction in analysis_directions])
    return PlanGenerationResponse(event_id=request.event_id, sections=sections, generated_at=datetime.now().isoformat())
