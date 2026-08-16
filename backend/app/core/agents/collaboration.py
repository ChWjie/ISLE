"""
Agent Collaboration and Consensus Building

Implements cross-examination, debate, and consensus mechanisms for
multi-agent legal analysis.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio


class ConsensusLevel(str, Enum):
    """Level of consensus among agents"""
    STRONG_CONSENSUS = "strong_consensus"  # >80% agreement
    MODERATE_CONSENSUS = "moderate_consensus"  # 60-80% agreement
    WEAK_CONSENSUS = "weak_consensus"  # 40-60% agreement
    NO_CONSENSUS = "no_consensus"  # <40% agreement
    CONFLICTING = "conflicting"  # Direct contradictions


@dataclass
class AgentOpinion:
    """Single agent's opinion on a legal issue"""
    agent_id: str
    agent_name: str
    position: str  # "support", "oppose", "neutral"
    analysis: str
    legal_basis: List[str]
    confidence: float
    key_points: List[str]


@dataclass
class CrossExaminationResult:
    """Result of cross-examination between agents"""
    examiner_id: str
    examinee_id: str
    questions: List[str]
    responses: List[str]
    identified_weaknesses: List[str]
    identified_strengths: List[str]


@dataclass
class ConsensusResult:
    """Result of consensus building process"""
    consensus_level: ConsensusLevel
    majority_position: str
    support_percentage: float
    key_agreements: List[str]
    key_disagreements: List[str]
    synthesized_position: str
    confidence: float


class AgentCollaborationEngine:
    """
    Engine for managing agent collaboration and consensus building

    Implements:
    1. Cross-examination - agents question each other's analyses
    2. Debate - agents present conflicting viewpoints
    3. Consensus building - synthesize multiple opinions
    4. Conflict resolution - resolve contradictions
    """

    def __init__(self, llm_model):
        """
        Initialize collaboration engine

        Args:
            llm_model: LLM model for generating questions and synthesis
        """
        self.llm_model = llm_model

    async def conduct_cross_examination(
        self,
        agent_analyses: List[Dict[str, Any]],
        focus_areas: List[str] = None
    ) -> List[CrossExaminationResult]:
        """
        Conduct cross-examination between agents

        Each agent examines others' analyses to identify strengths and weaknesses

        Args:
            agent_analyses: List of agent analysis results
            focus_areas: Specific areas to focus examination on

        Returns:
            List of cross-examination results
        """
        results = []

        # Each agent examines each other agent
        for i, examiner_analysis in enumerate(agent_analyses):
            for j, examinee_analysis in enumerate(agent_analyses):
                if i == j:
                    continue  # Don't self-examine

                result = await self._examine_analysis(
                    examiner=examiner_analysis,
                    examinee=examinee_analysis,
                    focus_areas=focus_areas
                )
                results.append(result)

        return results

    async def _examine_analysis(
        self,
        examiner: Dict[str, Any],
        examinee: Dict[str, Any],
        focus_areas: List[str] = None
    ) -> CrossExaminationResult:
        """Conduct examination of one agent's analysis by another"""

        examination_prompt = f"""你是{examiner['agent_name']}，请从你的专业角度审查以下分析：

被审查专家：{examinee['agent_name']}
分析内容：
{examinee['analysis']}

法律依据：
{', '.join(examinee.get('legal_basis', []))}

请提出3-5个关键问题来检验该分析的：
1. 法律依据的充分性
2. 论证的逻辑性
3. 潜在的法律风险
4. 遗漏的重要因素

同时指出该分析的优势和不足。

输出格式（JSON）：
{{
    "questions": ["问题1", "问题2", ...],
    "strengths": ["优势1", "优势2", ...],
    "weaknesses": ["不足1", "不足2", ...]
}}
"""

        try:
            response = await self.llm_model.generate_json(
                examination_prompt,
                system_prompt=f"你是{examiner['agent_name']}，专业领域：{', '.join(examiner.get('law_domains', []))}"
            )

            # Generate responses from examinee
            response_prompt = f"""你是{examinee['agent_name']}，请回应以下质疑：

质疑问题：
{chr(10).join(f"{i+1}. {q}" for i, q in enumerate(response.get('questions', [])))}

请逐一回应，提供：
1. 直接回答
2. 补充的法律依据
3. 必要的澄清

输出格式（JSON）：
{{
    "responses": ["回应1", "回应2", ...]
}}
"""

            responses_data = await self.llm_model.generate_json(
                response_prompt,
                system_prompt=f"你是{examinee['agent_name']}"
            )

            return CrossExaminationResult(
                examiner_id=examiner['agent_id'],
                examinee_id=examinee['agent_id'],
                questions=response.get('questions', []),
                responses=responses_data.get('responses', []),
                identified_weaknesses=response.get('weaknesses', []),
                identified_strengths=response.get('strengths', [])
            )

        except Exception as e:
            # Fallback
            return CrossExaminationResult(
                examiner_id=examiner['agent_id'],
                examinee_id=examinee['agent_id'],
                questions=[],
                responses=[],
                identified_weaknesses=[],
                identified_strengths=[]
            )

    async def build_consensus(
        self,
        agent_analyses: List[Dict[str, Any]],
        cross_examination_results: List[CrossExaminationResult] = None
    ) -> ConsensusResult:
        """
        Build consensus from multiple agent analyses

        Uses weighted voting and synthesis to create unified position

        Args:
            agent_analyses: List of agent analysis results
            cross_examination_results: Optional cross-examination results

        Returns:
            Consensus result with synthesized position
        """
        # Extract opinions
        opinions = self._extract_opinions(agent_analyses)

        # Analyze agreement level
        consensus_level, support_percentage = self._analyze_consensus_level(opinions)

        # Identify agreements and disagreements
        agreements, disagreements = self._identify_agreements_disagreements(
            agent_analyses,
            cross_examination_results
        )

        # Synthesize position
        synthesized_position = await self._synthesize_position(
            agent_analyses=agent_analyses,
            agreements=agreements,
            disagreements=disagreements,
            consensus_level=consensus_level
        )

        # Calculate overall confidence
        confidence = self._calculate_consensus_confidence(
            opinions=opinions,
            consensus_level=consensus_level,
            cross_examination_results=cross_examination_results
        )

        # Determine majority position
        majority_position = self._determine_majority_position(opinions)

        return ConsensusResult(
            consensus_level=consensus_level,
            majority_position=majority_position,
            support_percentage=support_percentage,
            key_agreements=agreements,
            key_disagreements=disagreements,
            synthesized_position=synthesized_position,
            confidence=confidence
        )

    def _extract_opinions(self, agent_analyses: List[Dict[str, Any]]) -> List[AgentOpinion]:
        """Extract structured opinions from agent analyses"""
        opinions = []

        for analysis in agent_analyses:
            # Simple position extraction (can be enhanced with NLP)
            analysis_text = analysis.get('analysis', '').lower()

            # Determine position based on keywords
            if any(word in analysis_text for word in ['支持', '赞同', '应当', '建议采取']):
                position = "support"
            elif any(word in analysis_text for word in ['反对', '不应', '不建议', '风险较大']):
                position = "oppose"
            else:
                position = "neutral"

            # Extract key points (simplified - first 3 recommendations)
            key_points = analysis.get('recommendations', [])[:3]

            opinions.append(AgentOpinion(
                agent_id=analysis['agent_id'],
                agent_name=analysis['agent_name'],
                position=position,
                analysis=analysis.get('analysis', ''),
                legal_basis=analysis.get('legal_basis', []),
                confidence=analysis.get('confidence', 0.5),
                key_points=key_points
            ))

        return opinions

    def _analyze_consensus_level(
        self,
        opinions: List[AgentOpinion]
    ) -> Tuple[ConsensusLevel, float]:
        """Analyze level of consensus among opinions"""

        if not opinions:
            return ConsensusLevel.NO_CONSENSUS, 0.0

        # Count positions
        position_counts = {"support": 0, "oppose": 0, "neutral": 0}
        for opinion in opinions:
            position_counts[opinion.position] += 1

        total = len(opinions)
        max_count = max(position_counts.values())
        support_percentage = max_count / total

        # Determine consensus level
        if support_percentage >= 0.8:
            level = ConsensusLevel.STRONG_CONSENSUS
        elif support_percentage >= 0.6:
            level = ConsensusLevel.MODERATE_CONSENSUS
        elif support_percentage >= 0.4:
            level = ConsensusLevel.WEAK_CONSENSUS
        else:
            # Check for direct conflicts
            if position_counts["support"] > 0 and position_counts["oppose"] > 0:
                level = ConsensusLevel.CONFLICTING
            else:
                level = ConsensusLevel.NO_CONSENSUS

        return level, support_percentage

    def _identify_agreements_disagreements(
        self,
        agent_analyses: List[Dict[str, Any]],
        cross_examination_results: List[CrossExaminationResult] = None
    ) -> Tuple[List[str], List[str]]:
        """Identify key agreements and disagreements"""

        # Collect all legal bases and recommendations
        all_legal_bases = []
        all_recommendations = []

        for analysis in agent_analyses:
            all_legal_bases.extend(analysis.get('legal_basis', []))
            all_recommendations.extend(analysis.get('recommendations', []))

        # Find common items (agreements)
        legal_basis_counts = {}
        for basis in all_legal_bases:
            legal_basis_counts[basis] = legal_basis_counts.get(basis, 0) + 1

        recommendation_counts = {}
        for rec in all_recommendations:
            recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1

        # Agreements: mentioned by multiple agents
        threshold = max(2, len(agent_analyses) // 2)  # At least 2 or half of agents
        agreements = []

        for basis, count in legal_basis_counts.items():
            if count >= threshold:
                agreements.append(f"法律依据共识：{basis}")

        for rec, count in recommendation_counts.items():
            if count >= threshold:
                agreements.append(f"建议共识：{rec}")

        # Disagreements: from cross-examination weaknesses
        disagreements = []
        if cross_examination_results:
            for result in cross_examination_results:
                disagreements.extend(result.identified_weaknesses[:2])  # Top 2 weaknesses

        return agreements[:5], disagreements[:5]  # Limit to top 5 each

    async def _synthesize_position(
        self,
        agent_analyses: List[Dict[str, Any]],
        agreements: List[str],
        disagreements: List[str],
        consensus_level: ConsensusLevel
    ) -> str:
        """Synthesize unified position from multiple analyses"""

        synthesis_prompt = f"""基于以下{len(agent_analyses)}位法律专家的分析，请综合形成统一的法律立场和建议。

共识程度：{consensus_level.value}

一致意见：
{chr(10).join(f"- {a}" for a in agreements)}

分歧意见：
{chr(10).join(f"- {d}" for d in disagreements)}

各专家分析摘要：
{chr(10).join(f"{i+1}. {a['agent_name']}: {a['analysis'][:200]}..." for i, a in enumerate(agent_analyses))}

请提供：
1. 综合的法律立场（整合各方观点）
2. 核心法律依据（基于共识）
3. 具体行动建议（考虑分歧）
4. 风险提示（基于不同意见）

要求：
- 保持专业性和权威性
- 明确指出共识和分歧
- 提供可操作的建议
- 长度控制在500-800字
"""

        try:
            synthesized = await self.llm_model.generate(
                [{"role": "user", "content": synthesis_prompt}]
            )

            return synthesized if isinstance(synthesized, str) else synthesized.get("content", "")

        except Exception as e:
            # Fallback synthesis
            return f"综合{len(agent_analyses)}位专家意见，形成以下法律立场：\n\n" + \
                   "\n".join(f"- {a}" for a in agreements[:3])

    def _calculate_consensus_confidence(
        self,
        opinions: List[AgentOpinion],
        consensus_level: ConsensusLevel,
        cross_examination_results: List[CrossExaminationResult] = None
    ) -> float:
        """Calculate overall confidence in the consensus"""

        # Base confidence from individual opinions
        avg_confidence = sum(op.confidence for op in opinions) / len(opinions) if opinions else 0.5

        # Adjust based on consensus level
        consensus_multipliers = {
            ConsensusLevel.STRONG_CONSENSUS: 1.1,
            ConsensusLevel.MODERATE_CONSENSUS: 1.0,
            ConsensusLevel.WEAK_CONSENSUS: 0.9,
            ConsensusLevel.NO_CONSENSUS: 0.7,
            ConsensusLevel.CONFLICTING: 0.6
        }

        multiplier = consensus_multipliers.get(consensus_level, 0.8)

        # Adjust based on cross-examination
        if cross_examination_results:
            # More weaknesses identified = lower confidence
            total_weaknesses = sum(len(r.identified_weaknesses) for r in cross_examination_results)
            weakness_penalty = min(total_weaknesses * 0.02, 0.2)  # Max 20% penalty
            multiplier -= weakness_penalty

        final_confidence = min(avg_confidence * multiplier, 1.0)

        return round(final_confidence, 2)

    def _determine_majority_position(self, opinions: List[AgentOpinion]) -> str:
        """Determine the majority position"""

        position_counts = {"support": 0, "oppose": 0, "neutral": 0}
        for opinion in opinions:
            position_counts[opinion.position] += 1

        majority = max(position_counts, key=position_counts.get)

        position_labels = {
            "support": "支持该法律立场",
            "oppose": "反对该法律立场",
            "neutral": "中立/需进一步分析"
        }

        return position_labels.get(majority, "未确定")
