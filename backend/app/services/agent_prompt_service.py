from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from app.models.database import Agent, Event


def _safe_join(values: Optional[Iterable[Any]], default: str) -> str:
    items = [str(v).strip() for v in (values or []) if str(v).strip()]
    return "、".join(items) if items else default


def normalize_agent_type(agent_type: Optional[str]) -> str:
    value = str(agent_type or "").strip().lower()
    if value in {"blue", "red", "judge", "analyst"}:
        return value
    return "analyst"


def get_agent_type_label(agent_type: Optional[str]) -> str:
    mapping = {
        "blue": "我方专家",
        "red": "对抗方专家",
        "judge": "中立裁判",
        "analyst": "综合分析师",
    }
    normalized = normalize_agent_type(agent_type)
    return mapping.get(normalized, "综合分析师")


def _collect_agent_keywords(agent: Agent | Dict[str, Any] | None) -> List[str]:
    if not agent:
        return []
    data = agent if isinstance(agent, dict) else {
        "name": agent.name,
        "description": agent.description,
        "mission": agent.mission,
        "responsibilities": agent.responsibilities,
        "knowledge_scope": agent.knowledge_scope,
        "stance": agent.stance,
    }
    keywords: List[str] = []
    for field in ("name", "description", "mission", "responsibilities", "stance"):
        text = str(data.get(field) or "").strip()
        if text:
            keywords.append(text)
    for item in data.get("knowledge_scope") or []:
        text = str(item).strip()
        if text:
            keywords.append(text)
    return keywords


def infer_agent_domain(agent: Agent | Dict[str, Any] | None) -> str:
    corpus = " ".join(_collect_agent_keywords(agent))
    rules = [
        ("劳动用工与劳动争议", ("劳动", "用工", "仲裁", "解除", "社保", "工伤")),
        ("数据合规与个人信息保护", ("数据", "个人信息", "隐私", "网安", "平台治理")),
        ("合同履约与商事争议", ("合同", "违约", "履约", "商事", "交易")),
        ("知识产权保护", ("知识产权", "著作权", "商标", "专利", "不正当竞争")),
        ("公司治理与证券合规", ("公司治理", "股东", "董事", "证券", "上市", "信息披露")),
        ("竞争与反垄断合规", ("竞争", "反垄断", "经营者集中", "滥用市场支配地位")),
        ("税务合规", ("税务", "发票", "税收", "纳税")),
        ("环境与安全生产合规", ("环保", "环境", "安全生产", "排污")),
        ("医疗与医药合规", ("医疗", "医药", "药品", "器械")),
        ("刑事合规与调查应对", ("刑事", "侦查", "合规不起诉", "刑责")),
        ("证据审查与事实认定", ("证据", "证明", "举证", "事实认定")),
        ("争议解决与调解裁判", ("法官", "仲裁", "裁判", "调解", "审理")),
        ("综合法律分析", tuple()),
    ]
    for label, tokens in rules:
        if tokens and any(token in corpus for token in tokens):
            return label
    return "综合法律分析"


def _normalize_search_text(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    for token in ["\r", "\n", "；", ";", "，", ",", "。", "、", "|"]:
        text = text.replace(token, " ")
    return " ".join(text.split())


def _shorten_fact_text(event: Event, limit: int = 48) -> str:
    raw = _normalize_search_text(event.fact_summary or event.description or "")
    if not raw:
        return ""
    if (len(raw) <= limit):
        return raw
    return raw[:limit].rstrip() + "…"


def _collect_search_terms(event: Event, agent: Agent | Dict[str, Any] | None = None) -> List[str]:
    terms: List[str] = []

    for item in [event.dispute_type, event.name, _shorten_fact_text(event)]:
        text = _normalize_search_text(item)
        if text:
            terms.append(text)

    legal_systems = [str(v).strip() for v in (event.legal_systems or []) if str(v).strip()]
    if legal_systems:
        terms.extend(legal_systems[:3])

    if agent:
        data = agent if isinstance(agent, dict) else {
            "knowledge_scope": agent.knowledge_scope,
            "name": agent.name,
            "description": agent.description,
        }
        for item in (data.get("knowledge_scope") or [])[:2]:
            text = _normalize_search_text(item)
            if text:
                terms.append(text)

        agent_name = _normalize_search_text(data.get("name"))
        if any(keyword in agent_name for keyword in ["数据", "隐私", "个人信息", "网安"]):
            terms.append("个人信息保护")
        elif any(keyword in agent_name for keyword in ["合同", "商事"]):
            terms.append("合同纠纷")
        elif any(keyword in agent_name for keyword in ["劳动", "用工"]):
            terms.append("劳动争议")
        elif any(keyword in agent_name for keyword in ["知识产权", "著作权", "商标", "专利"]):
            terms.append("知识产权")

    deduped: List[str] = []
    for term in terms:
        cleaned = _normalize_search_text(term)
        if cleaned and cleaned not in deduped:
            deduped.append(cleaned)
    return deduped

@dataclass
class RetrievalDecision:
    enabled: bool
    query: str
    reason: str


def should_enable_delilegal(stage: str, event: Event, agent: Agent | Dict[str, Any] | None = None) -> bool:
    text = " ".join(
        [
            _safe_join(event.legal_systems, ""),
            str(event.dispute_type or ""),
            str(event.description or ""),
            str(event.fact_summary or ""),
            " ".join(_collect_agent_keywords(agent)),
        ]
    )
    foreign_tokens = ("UNCLOS", "国际海洋法", "国际法", "海洋", "条约法", "WTO")
    if any(token.lower() in text.lower() for token in foreign_tokens):
        return False
    if stage == "integration":
        return False
    return True


def build_retrieval_decision(
    stage: str,
    event: Event,
    agent: Agent | Dict[str, Any] | None = None,
    opponent_text: str = "",
    current_text: str = "",
) -> RetrievalDecision:
    if not should_enable_delilegal(stage, event, agent):
        return RetrievalDecision(False, "", "当前阶段或场景不启用得理检索")

    terms = _collect_search_terms(event, agent)
    query = "；".join(terms[:4]).strip()

    if len(query) > 120:
        query = query[:120].rstrip("； ") + "…"

    if not query:
        query = _normalize_search_text(event.dispute_type or event.name or "法律问题")

    return RetrievalDecision(True, query, "命中国内法与阶段检索规则")


def _base_event_block(event: Event) -> str:
    return f"""【案件背景】
事件名称：{event.name or '未命名事件'}
争议类型：{event.dispute_type or '待确认'}
事实概要：{event.fact_summary or event.description or '暂无详细案情'}
我方主体：{_safe_join(event.our_side, '待确认')}
对方主体：{_safe_join(event.opponent_side, '待确认')}
涉及法律体系：{_safe_join(event.legal_systems, '公司法、合同规则、劳动用工规范、数据合规要求等')}"""


def _agent_block(agent: Agent | Dict[str, Any]) -> str:
    data = agent if isinstance(agent, dict) else {
        "name": agent.name,
        "description": agent.description,
        "mission": agent.mission,
        "responsibilities": agent.responsibilities,
        "system_prompt": agent.system_prompt,
        "stance": agent.stance,
        "knowledge_scope": agent.knowledge_scope,
        "agent_type": agent.agent_type,
    }
    return f"""【智能体画像】
名称：{data.get('name', '未命名智能体')}
角色：{get_agent_type_label(data.get('agent_type'))}
专长领域：{infer_agent_domain(data)}
角色描述：{data.get('description') or '未配置'}
核心使命：{data.get('mission') or '未配置'}
职责重点：{data.get('responsibilities') or '未配置'}
立场：{data.get('stance') or '未配置'}
知识范围：{_safe_join(data.get('knowledge_scope'), '通用法律分析')}
附加系统指令：{data.get('system_prompt') or '无'}"""


def _retrieval_block(retrieval_pack: Optional[Dict[str, Any]]) -> str:
    if not retrieval_pack:
        return "【检索增强】\n当前阶段未接入得理检索，请基于案件事实、角色定位与一般法律规则进行分析。"
    return retrieval_pack.get(
        "retrieval_context",
        "【检索增强】\n检索结果为空，请明确说明信息不足并给出谨慎判断。",
    )


def build_stage_prompt(
    stage: str,
    event: Event,
    agent: Agent | Dict[str, Any],
    retrieval_pack: Optional[Dict[str, Any]] = None,
    opponent_text: str = "",
    current_text: str = "",
    history: str = "",
    round_num: Optional[int] = None,
    analyses_summary: str = "",
) -> Dict[str, str]:
    role = normalize_agent_type((agent.get("agent_type") if isinstance(agent, dict) else agent.agent_type))
    agent_name = agent.get("name") if isinstance(agent, dict) else agent.name
    system_prompt = "你是一位严谨、可核验、重视引用依据的法律智能体。"

    if role == "blue":
        system_prompt = f"你是{agent_name}，代表我方输出专业、审慎、可落地的法律意见。"
    elif role == "red":
        system_prompt = f"你是{agent_name}，代表对抗方提出最强法律挑战和抗辩。"
    elif role == "judge":
        system_prompt = f"你是{agent_name}，保持中立并以裁判/仲裁审查口径评估双方观点。"

    common = "\n\n".join([
        _base_event_block(event),
        _agent_block(agent),
        _retrieval_block(retrieval_pack),
    ])

    if stage == "analysis":
        user_prompt = f"""{common}

【当前阶段】
初始分析阶段：此阶段不需要回应具体对手发言，但需要主动识别争点、证据缺口、适用法规和可能对抗点。

【任务要求】
1. 从你的角色出发，输出本案的核心判断与优先处理事项。
2. 优先引用检索增强中的法规和类案；若引用，请保留如 [Case-1]、[Law-2] 的来源编号。
3. 说明哪些结论来自检索，哪些属于基于事实的专业推断。
4. 结合你的专业领域提出后续博弈时最关键的攻防点。

【输出结构】
### 一、角色结论
### 二、适用法规与类案依据
### 三、事实认定与证据缺口
### 四、后续博弈重点
### 五、行动建议
"""
    elif stage in {"debate_blue", "debate_red"}:
        phase_name = "博弈阶段"
        objective = "强化我方主张并拆解对手论证" if stage == "debate_blue" else "代表对抗方发起反驳并攻击对手漏洞"
        user_prompt = f"""{common}

【当前阶段】
{phase_name}：你必须结合对手上一轮观点、历史交锋与本轮目标动态回应。
当前轮次：第 {round_num or 1} 轮
历史摘要：{history or '当前为首轮交锋'}
对手上一轮观点：{opponent_text or '暂无'}

【本轮目标】
{objective}

【任务要求】
1. 逐项回应对手上一轮最强论点，不能只重复己方立场。
2. 优先引用检索增强中的法规与类案；检索不足时，再使用一般法理补充。
3. 明确指出对手在事实、证据、法律适用、程序策略上的漏洞。
4. 输出应是可直接用于辩论/质证/答辩的发言，不写寒暄。

【输出结构】
### 一、本轮主张
### 二、对对手观点的回应
### 三、法规与类案支撑
### 四、下一步攻防建议
"""
    elif stage == "judge":
        user_prompt = f"""{common}

【当前阶段】
裁判评估阶段：你需要站在中立立场，对双方当前轮次发言进行可核验评估。
当前轮次：第 {round_num or 1} 轮
历史摘要：{history or '暂无既往轮次'}
我方观点：{current_text or '暂无'}
对方观点：{opponent_text or '暂无'}

【任务要求】
1. 比较双方事实主张、法条引用、类案支持和论证完整性。
2. 优先依据检索增强内容进行核验，并指出双方是否存在过度推断。
3. 给出本轮中立点评、争点归纳、裁判倾向和胜率评估。

【输出结构】
### 一、争点评估
### 二、双方论证优劣
### 三、适用法规与类案核验
### 四、本轮裁判倾向
最后一行必须单独输出：当前蓝方胜率：XX%
"""
    elif stage == "integration":
        user_prompt = f"""{_base_event_block(event)}

【当前阶段】
综合整合阶段：此阶段重点是整合多智能体结论、沉淀文档，不要求重新与对手交锋。

【各智能体分析摘要】
{analyses_summary or '暂无智能体分析结果'}

【任务要求】
1. 整合各角色结论，去除重复，保留冲突点与最终采信理由。
2. 优先复用既有分析中的法规、类案与来源编号，不要虚构新来源。
3. 区分“确定结论”“待补证据”“策略建议”三类信息。

【输出结构】
### 一、结论来源与整合逻辑
### 二、核心争点与法规依据
### 三、各方观点对比
### 四、风险与证据缺口
### 五、最终行动建议
"""
    else:
        user_prompt = f"{common}\n\n请基于上述内容输出专业法律分析。"

    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
    }
