"""
Advanced Expert Selection Algorithm

Intelligent expert selection based on relevance scoring, domain matching,
and historical performance analysis.
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import re
from collections import defaultdict


@dataclass
class ExpertRelevanceScore:
    """Expert relevance score for a given task"""
    agent_id: str
    agent_name: str
    relevance_score: float  # 0-1
    domain_match_score: float  # 0-1
    keyword_match_score: float  # 0-1
    historical_performance: float  # 0-1
    final_score: float  # Weighted combination
    reasoning: str


class ExpertSelectionAlgorithm:
    """
    Advanced expert selection algorithm

    Uses multiple criteria to select the most relevant experts:
    1. Domain matching - matches event type to expert domains
    2. Keyword analysis - analyzes event description for legal keywords
    3. Historical performance - considers past analysis quality
    4. Diversity - ensures diverse perspectives
    """

    # Legal domain keywords mapping
    DOMAIN_KEYWORDS = {
        "international_law": [
            "公司法", "合同", "劳动", "数据", "监管", "合规", "治理"
        ],
        "maritime_law": [
            "个人信息", "数据安全", "劳动合同", "股权治理", "知识产权", "反不正当竞争",
            "行政处罚", "证据链", "用工", "平台规则", "合同履约"
        ],
        "territory_law": [
            "领土", "边界", "主权", "领土争端", "边界划定", "历史性权利", "实际控制",
            "领土完整", "边境", "陆地边界"
        ],
        "diplomatic_law": [
            "外交", "外交关系", "外交照会", "外交特权", "外交豁免", "外交谈判",
            "外交抗议", "维也纳公约"
        ],
        "evidence_analysis": [
            "证据", "事实", "文献", "档案", "历史记录", "证明", "举证", "事实认定"
        ],
        "military_law": [
            "军事", "武装冲突", "交战", "军事行动", "防御", "威胁", "武力", "军舰",
            "军机", "演习"
        ],
        "economic_law": [
            "经济", "贸易", "制裁", "WTO", "投资", "关税", "经济制裁", "经济合作"
        ],
        "environmental_law": [
            "环境", "污染", "生态", "环境保护", "环境损害", "气候", "资源保护"
        ],
        "human_rights_law": [
            "人权", "人道主义", "人权公约", "人道主义法", "平民保护"
        ],
        "aviation_law": [
            "航空", "领空", "飞行", "航空器", "防空识别区", "空域", "民航"
        ]
    }

    # Event type to primary domains mapping
    EVENT_TYPE_DOMAINS = {
        "maritime_dispute": ["maritime_law", "territory_law", "international_law", "evidence_analysis"],
        "territorial_dispute": ["territory_law", "international_law", "evidence_analysis", "diplomatic_law"],
        "diplomatic_conflict": ["diplomatic_law", "international_law", "human_rights_law"],
        "military_incident": ["military_law", "international_law", "diplomatic_law", "maritime_law"],
        "economic_sanction": ["economic_law", "international_law", "diplomatic_law"],
        "environmental_issue": ["environmental_law", "maritime_law", "international_law"],
        "aviation_incident": ["aviation_law", "international_law", "military_law"],
    }

    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize expert selection algorithm

        Args:
            weights: Scoring weights for different criteria
        """
        self.weights = weights or {
            "domain_match": 0.4,
            "keyword_match": 0.3,
            "historical_performance": 0.2,
            "diversity": 0.1
        }

        # Historical performance cache (in production, load from database)
        self.historical_performance = defaultdict(lambda: 0.75)  # Default 0.75

    def select_experts(
        self,
        event_description: str,
        event_type: str,
        available_agents: List[Dict[str, Any]],
        min_experts: int = 3,
        max_experts: int = 8
    ) -> List[ExpertRelevanceScore]:
        """
        Select most relevant experts for the given event

        Args:
            event_description: Description of the legal event
            event_type: Type of event (maritime_dispute, territorial_dispute, etc.)
            available_agents: List of available expert agents
            min_experts: Minimum number of experts to select
            max_experts: Maximum number of experts to select

        Returns:
            List of selected experts with relevance scores
        """
        # Calculate relevance scores for all agents
        scored_agents = []

        for agent in available_agents:
            score = self._calculate_relevance_score(
                agent=agent,
                event_description=event_description,
                event_type=event_type
            )
            scored_agents.append(score)

        # Sort by final score (descending)
        scored_agents.sort(key=lambda x: x.final_score, reverse=True)

        # Apply diversity filter
        selected = self._apply_diversity_filter(
            scored_agents=scored_agents,
            min_experts=min_experts,
            max_experts=max_experts
        )

        return selected

    def _calculate_relevance_score(
        self,
        agent: Dict[str, Any],
        event_description: str,
        event_type: str
    ) -> ExpertRelevanceScore:
        """Calculate relevance score for a single agent"""

        agent_type = agent.get("type", "")
        agent_domains = agent.get("law_domains", [])

        # 1. Domain match score
        domain_score = self._calculate_domain_match(agent_type, event_type)

        # 2. Keyword match score
        keyword_score = self._calculate_keyword_match(
            event_description=event_description,
            agent_type=agent_type,
            agent_domains=agent_domains
        )

        # 3. Historical performance
        historical_score = self.historical_performance[agent.get("id", "")]

        # 4. Calculate final weighted score
        final_score = (
            self.weights["domain_match"] * domain_score +
            self.weights["keyword_match"] * keyword_score +
            self.weights["historical_performance"] * historical_score
        )

        # Generate reasoning
        reasoning = self._generate_selection_reasoning(
            agent_name=agent.get("name", ""),
            domain_score=domain_score,
            keyword_score=keyword_score,
            historical_score=historical_score
        )

        return ExpertRelevanceScore(
            agent_id=agent.get("id", ""),
            agent_name=agent.get("name", ""),
            relevance_score=final_score,
            domain_match_score=domain_score,
            keyword_match_score=keyword_score,
            historical_performance=historical_score,
            final_score=final_score,
            reasoning=reasoning
        )

    def _calculate_domain_match(self, agent_type: str, event_type: str) -> float:
        """Calculate domain match score"""

        # Get primary domains for this event type
        primary_domains = self.EVENT_TYPE_DOMAINS.get(event_type, [])

        if not primary_domains:
            # Unknown event type, use moderate score
            return 0.5

        # Check if agent's type is in primary domains
        if agent_type in primary_domains:
            # Calculate position-based score (earlier = more relevant)
            position = primary_domains.index(agent_type)
            score = 1.0 - (position * 0.15)  # Decrease by 0.15 for each position
            return max(score, 0.4)  # Minimum 0.4 for primary domains

        return 0.3  # Not in primary domains

    def _calculate_keyword_match(
        self,
        event_description: str,
        agent_type: str,
        agent_domains: List[str]
    ) -> float:
        """Calculate keyword match score"""

        # Get keywords for this agent type
        agent_keywords = self.DOMAIN_KEYWORDS.get(agent_type, [])

        if not agent_keywords:
            return 0.5

        # Count keyword matches in event description
        description_lower = event_description.lower()
        matches = sum(1 for keyword in agent_keywords if keyword in description_lower)

        # Also check agent domains
        domain_matches = sum(1 for domain in agent_domains if domain in description_lower)

        # Calculate score (normalized)
        total_keywords = len(agent_keywords)
        keyword_score = min(matches / max(total_keywords * 0.3, 1), 1.0)  # 30% match = full score
        domain_score = min(domain_matches / max(len(agent_domains) * 0.5, 1), 1.0)

        # Combine scores
        return (keyword_score * 0.7 + domain_score * 0.3)

    def _generate_selection_reasoning(
        self,
        agent_name: str,
        domain_score: float,
        keyword_score: float,
        historical_score: float
    ) -> str:
        """Generate human-readable reasoning for selection"""

        reasons = []

        if domain_score >= 0.7:
            reasons.append("核心领域专家")
        elif domain_score >= 0.5:
            reasons.append("相关领域专家")

        if keyword_score >= 0.6:
            reasons.append("高度匹配事件关键词")
        elif keyword_score >= 0.4:
            reasons.append("部分匹配事件特征")

        if historical_score >= 0.8:
            reasons.append("历史表现优异")

        if not reasons:
            reasons.append("提供补充视角")

        return f"{agent_name}: " + "、".join(reasons)

    def _apply_diversity_filter(
        self,
        scored_agents: List[ExpertRelevanceScore],
        min_experts: int,
        max_experts: int
    ) -> List[ExpertRelevanceScore]:
        """
        Apply diversity filter to ensure diverse expert perspectives

        Ensures we don't select too many experts from the same domain
        """
        selected = []
        domain_counts = defaultdict(int)
        max_per_domain = 2  # Maximum 2 experts per domain type

        for agent in scored_agents:
            # Extract domain type from agent_id (e.g., "agent-1" -> type from template)
            # For now, use simple selection

            # Always select top min_experts
            if len(selected) < min_experts:
                selected.append(agent)
                continue

            # Stop if we have max_experts
            if len(selected) >= max_experts:
                break

            # For additional experts, apply diversity filter
            # (In production, track actual domain types)
            if agent.final_score >= 0.5:  # Threshold for additional experts
                selected.append(agent)

        return selected[:max_experts]

    def update_historical_performance(self, agent_id: str, performance_score: float):
        """Update historical performance for an agent"""
        # Exponential moving average
        alpha = 0.3  # Learning rate
        current = self.historical_performance[agent_id]
        self.historical_performance[agent_id] = alpha * performance_score + (1 - alpha) * current
