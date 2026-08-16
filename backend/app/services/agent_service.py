"""
Agent Service - Business Logic
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.database import Agent, AgentType
from app.schemas.agent import AgentCreate, AgentUpdate
import uuid


def _compliance_template(
    template_id: str,
    name: str,
    agent_type: AgentType,
    domain: str,
    description: str,
    scenarios: List[str],
    legal_priority: str,
    temperature: float = 0.4,
) -> Dict[str, Any]:
    mission = f"围绕{domain}场景提供法律风险识别、合规审查、争议研判和可执行的处置建议。"
    responsibilities = (
        f"1. 梳理{domain}场景下的事实、主体、流程与证据材料。\n"
        "2. 识别关键法律风险、监管关注点和争议焦点。\n"
        "3. 给出法律依据、风险等级、证据补强和整改建议。\n"
        "4. 输出适合演示和业务落地的结构化分析结论。"
    )
    system_prompt = (
        f"你是{name}，专注{domain}。请严格基于中国现行法律法规、监管规则和司法实践，"
        "以事实清单、法律依据、风险判断、证据建议、处置方案的结构输出。"
        "不得使用与当前案件无关的领域作为默认分析框架。"
    )
    return {
        "template_id": template_id,
        "name": name,
        "agent_type": agent_type,
        "description": description,
        "mission": mission,
        "responsibilities": responsibilities,
        "system_prompt": system_prompt,
        "default_config": {
            "temperature": temperature,
            "max_tokens": 1800,
            "goals": ["risk_control", "compliance", "actionable_advice"],
            "strategy_orientation": "balanced" if agent_type != AgentType.RED else "adversarial",
            "legal_priority": legal_priority,
            "knowledge_scope": [domain],
        },
        "suitable_scenarios": scenarios,
    }


# Runtime templates for Tencent Kaiwu D06 legal-tech track.
# This assignment intentionally supersedes the legacy maritime-law templates above.
AGENT_TEMPLATES = {
    "blue": [
        _compliance_template("AGENT-LABOR-COMPLIANCE-001", "劳动合规顾问-张律师", AgentType.BLUE, "劳动用工合规", "专注劳动合同、工资支付、竞业限制、裁员解雇和工伤争议，提供企业用工风险防控建议。", ["劳动用工体检", "劳动争议预防", "裁员解雇合规"], "labor_compliance"),
        _compliance_template("AGENT-DATA-COMPLIANCE-001", "数据合规专家-李顾问", AgentType.BLUE, "数据安全与个人信息保护", "专注个人信息保护、数据安全、网络安全和数据出境合规，擅长隐私政策审查与事件处置。", ["隐私政策审查", "数据出境评估", "数据安全事件应对"], "data_compliance"),
        _compliance_template("AGENT-CONTRACT-DISPUTE-001", "合同纠纷律师-王律师", AgentType.BLUE, "合同审查与商事争议", "专注合同起草、履约审查、违约责任认定和商事争议解决策略。", ["合同条款审查", "违约争议分析", "诉前谈判准备"], "contract_dispute"),
        _compliance_template("AGENT-IP-LAW-001", "知识产权律师-陈律师", AgentType.BLUE, "知识产权保护", "专注商标、专利、著作权和商业秘密保护，擅长侵权判断、取证保全和维权路径设计。", ["侵权预警", "商业秘密保护", "维权方案设计"], "intellectual_property"),
        _compliance_template("AGENT-COMPETITION-COMPLIANCE-001", "竞争合规顾问-赵律师", AgentType.BLUE, "反垄断与反不正当竞争", "专注反垄断、反不正当竞争、平台经济监管和经营者集中风险评估。", ["平台规则审查", "反垄断调查应对", "竞争合规培训"], "competition_compliance"),
        _compliance_template("AGENT-SECURITIES-COMPLIANCE-001", "证券合规律师-孙律师", AgentType.BLUE, "证券合规与公司披露", "专注上市公司信息披露、内幕交易防控、关联交易和证券执法应对。", ["信息披露审查", "监管问询回复", "上市公司合规体检"], "securities_compliance"),
        _compliance_template("AGENT-CONSUMER-RIGHTS-001", "消费者权益律师-吴律师", AgentType.BLUE, "消费者权益保护", "专注消费者保护、产品责任、广告宣传、格式条款和售后服务合规。", ["消费者投诉处理", "营销文案审查", "产品责任评估"], "consumer_protection"),
        _compliance_template("AGENT-RISK-CONTROL-001", "合规风控顾问-周律师", AgentType.BLUE, "企业合规风控", "统筹劳动、数据、合同、竞争、证券等多领域风险，输出管理层视角的合规风险报告。", ["合规体系建设", "风险清单汇总", "管理层决策支持"], "enterprise_risk_control"),
        _compliance_template("AGENT-CRIMINAL-COMPLIANCE-001", "刑事合规律师-郑律师", AgentType.BLUE, "企业刑事合规", "关注商业贿赂、职务侵占、非法经营、虚开发票等企业刑事风险。", ["刑事风险排查", "内部调查", "高风险业务评估"], "criminal_compliance"),
        _compliance_template("AGENT-CORPORATE-GOVERNANCE-001", "公司治理顾问-冯律师", AgentType.BLUE, "公司治理", "专注股东会、董事会、授权机制、关联交易、利益冲突和治理结构优化。", ["章程修订", "董事会治理", "关联交易审查"], "corporate_governance"),
        _compliance_template("AGENT-LITIGATION-STRATEGY-001", "诉讼策略分析师-韩律师", AgentType.BLUE, "诉讼与仲裁策略", "擅长争议焦点拆解、证据强弱评估、攻防路径设计和庭审策略规划。", ["诉讼路径设计", "证据强弱评估", "案件总体策略规划"], "litigation_strategy"),
        _compliance_template("AGENT-TAX-COMPLIANCE-001", "税务合规顾问-杨律师", AgentType.BLUE, "税务合规", "专注税务筹划边界、发票管理、涉税争议和税务稽查应对。", ["税务体检", "发票合规审查", "稽查应对准备"], "tax_compliance"),
        _compliance_template("AGENT-ENVIRONMENTAL-COMPLIANCE-001", "环保合规律师-朱律师", AgentType.BLUE, "生态环保合规", "专注环评、排污许可、危废处置、环境事故责任和行政处罚应对。", ["环保体检", "排污许可审查", "环境执法应对"], "environmental_compliance"),
        _compliance_template("AGENT-FINANCIAL-REGULATION-001", "金融监管顾问-秦律师", AgentType.BLUE, "金融监管合规", "专注金融产品、持牌经营、投资者适当性、金融营销和监管检查应对。", ["金融产品审查", "营销合规评估", "监管检查准备"], "financial_regulation"),
        _compliance_template("AGENT-DISPUTE-MEDIATION-001", "争议调解顾问-许律师", AgentType.BLUE, "争议调解", "擅长争议缓和、和解窗口识别、多方利益平衡和可执行调解方案设计。", ["商事调解", "劳动和解", "争议降级处理"], "dispute_resolution"),
        _compliance_template("AGENT-MEDICAL-COMPLIANCE-001", "医疗合规律师-何律师", AgentType.BLUE, "医疗健康合规", "关注医疗服务、药械流通、患者隐私、知情同意和医疗广告合规。", ["医疗机构体检", "药械合规审查", "患者纠纷预防"], "medical_compliance"),
        _compliance_template("AGENT-INTERNET-PLATFORM-001", "互联网平台律师-施律师", AgentType.BLUE, "互联网平台治理", "擅长平台责任、内容审核、算法规则、商家管理和用户权益保护。", ["平台规则优化", "内容治理合规", "平台投诉处置"], "platform_compliance"),
        _compliance_template("AGENT-EVIDENCE-EXPERT-001", "证据专家顾问-曹律师", AgentType.BLUE, "证据规则与电子数据", "专注证据目录构建、取证策略、电子证据保全和证明力评估。", ["证据梳理", "电子证据保全", "诉前取证规划"], "evidence_strategy"),
    ],
    "red": [
        _compliance_template("AGENT-REGULATORY-ENFORCEMENT-001", "监管执法代理-模拟器", AgentType.RED, "监管执法压力测试", "模拟监管机关审查口径、质询方式和处罚逻辑，用于压力测试企业合规方案。", ["执法压力测试", "监管问询演练", "处罚风险评估"], "regulatory_enforcement", 0.5),
        _compliance_template("AGENT-OPPOSING-PARTY-001", "对方当事人代理-模拟器", AgentType.RED, "争议对方攻防模拟", "模拟合同相对方、劳动者、消费者或合作方的对抗立场，用于争议博弈演练。", ["对抗推演", "谈判演练", "争议博弈模拟"], "dispute_counterparty", 0.6),
    ],
    "judge": [
        _compliance_template("AGENT-CIVIL-JUDGE-001", "民事法官-裁判模拟", AgentType.JUDGE, "民事裁判模拟", "从民事裁判视角评估合同、侵权、证据和程序问题，注重事实认定与裁判可执行性。", ["合同纠纷模拟裁判", "侵权争议评议", "民事诉讼推演"], "civil_adjudication", 0.2),
        _compliance_template("AGENT-ADMINISTRATIVE-JUDGE-001", "行政法官-裁判模拟", AgentType.JUDGE, "行政裁判模拟", "关注行政行为合法性、程序正当性和处罚适当性，适用于监管执法争议分析。", ["行政处罚争议", "监管执法复盘", "行政诉讼推演"], "administrative_adjudication", 0.2),
        _compliance_template("AGENT-LABOR-ARBITRATOR-001", "劳动仲裁员-裁判模拟", AgentType.JUDGE, "劳动仲裁模拟", "适用于劳动争议中立评议，注重劳动关系认定、证据留痕与裁审口径。", ["劳动仲裁模拟", "解雇争议评议", "薪酬工时争议分析"], "labor_adjudication", 0.2),
    ],
}


class AgentService:
    """Agent业务逻辑服务"""

    @staticmethod
    def create_agent(db: Session, agent_data: AgentCreate) -> Agent:
        """创建Agent"""
        agent_id = f"AGENT-{uuid.uuid4().hex[:8].upper()}"

        agent = Agent(
            agent_id=agent_id,
            name=agent_data.name,
            description=agent_data.description,
            mission=agent_data.mission,
            responsibilities=agent_data.responsibilities,
            agent_type=agent_data.agent_type,
            event_id=agent_data.event_id,
            system_prompt=agent_data.system_prompt,
            stance=agent_data.stance,
            goals=agent_data.goals,
            strategy_orientation=agent_data.strategy_orientation,
            legal_priority=agent_data.legal_priority,
            knowledge_scope=agent_data.knowledge_scope,
            llm_config=agent_data.llm_config or {},
            template_id=agent_data.template_id
        )

        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent

    @staticmethod
    def get_agent(db: Session, agent_id: str) -> Optional[Agent]:
        """获取单个Agent"""
        return db.query(Agent).filter(Agent.agent_id == agent_id).first()

    @staticmethod
    def list_agents(
        db: Session,
        agent_type: Optional[AgentType] = None,
        event_id: Optional[int] = None,
        is_active: bool = True
    ) -> List[Agent]:
        """列出Agents"""
        query = db.query(Agent)

        if agent_type:
            query = query.filter(Agent.agent_type == agent_type)
        if event_id:
            query = query.filter(Agent.event_id == event_id)
        if is_active is not None:
            query = query.filter(Agent.is_active == is_active)

        return query.all()

    @staticmethod
    def update_agent(db: Session, agent_id: str, agent_data: AgentUpdate) -> Optional[Agent]:
        """更新Agent"""
        agent = AgentService.get_agent(db, agent_id)
        if not agent:
            return None

        update_data = agent_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(agent, key, value)

        db.commit()
        db.refresh(agent)
        return agent

    @staticmethod
    def delete_agent(db: Session, agent_id: str) -> bool:
        """删除Agent (软删除)"""
        agent = AgentService.get_agent(db, agent_id)
        if not agent:
            return False

        agent.is_active = False
        db.commit()
        return True

    @staticmethod
    def get_templates(agent_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取Agent模板"""
        if agent_type:
            return AGENT_TEMPLATES.get(agent_type, [])

        # 返回所有模板
        all_templates = []
        for templates in AGENT_TEMPLATES.values():
            all_templates.extend(templates)
        return all_templates
