"""
Quality Assessment Framework

Evaluates the quality of legal analyses and synthesized plans.
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class QualityDimension(str, Enum):
    """Dimensions of quality assessment"""
    LEGAL_SOUNDNESS = "legal_soundness"  # 法律依据的充分性
    LOGICAL_COHERENCE = "logical_coherence"  # 论证的逻辑性
    COMPLETENESS = "completeness"  # 分析的全面性
    PRACTICAL_FEASIBILITY = "practical_feasibility"  # 实际可操作性
    RISK_AWARENESS = "risk_awareness"  # 风险意识
    CONSISTENCY = "consistency"  # 内部一致性


@dataclass
class QualityScore:
    """Quality score for a single dimension"""
    dimension: QualityDimension
    score: float  # 0-1
    feedback: str
    evidence: List[str]


@dataclass
class QualityAssessmentResult:
    """Overall quality assessment result"""
    overall_score: float  # 0-1
    dimension_scores: List[QualityScore]
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]
    quality_level: str  # "excellent", "good", "fair", "poor"


class QualityAssessmentFramework:
    """
    Framework for assessing quality of legal analyses

    Evaluates multiple dimensions:
    1. Legal soundness - validity of legal basis
    2. Logical coherence - consistency of arguments
    3. Completeness - coverage of all aspects
    4. Practical feasibility - actionability
    5. Risk awareness - identification of risks
    6. Consistency - internal consistency
    """

    def __init__(self, llm_model):
        """
        Initialize quality assessment framework

        Args:
            llm_model: LLM model for assessment
        """
        self.llm_model = llm_model

        # Weights for different dimensions
        self.dimension_weights = {
            QualityDimension.LEGAL_SOUNDNESS: 0.30,
            QualityDimension.LOGICAL_COHERENCE: 0.20,
            QualityDimension.COMPLETENESS: 0.20,
            QualityDimension.PRACTICAL_FEASIBILITY: 0.15,
            QualityDimension.RISK_AWARENESS: 0.10,
            QualityDimension.CONSISTENCY: 0.05
        }

    async def assess_quality(
        self,
        synthesized_plan: str,
        agent_analyses: List[Dict[str, Any]],
        consensus_result: Any = None
    ) -> QualityAssessmentResult:
        """
        Assess quality of synthesized legal plan

        Args:
            synthesized_plan: The synthesized legal plan
            agent_analyses: Individual agent analyses
            consensus_result: Consensus building result

        Returns:
            Quality assessment result
        """
        # Assess each dimension
        dimension_scores = []

        for dimension in QualityDimension:
            score = await self._assess_dimension(
                dimension=dimension,
                synthesized_plan=synthesized_plan,
                agent_analyses=agent_analyses,
                consensus_result=consensus_result
            )
            dimension_scores.append(score)

        # Calculate overall score
        overall_score = sum(
            score.score * self.dimension_weights[score.dimension]
            for score in dimension_scores
        )

        # Identify strengths and weaknesses
        strengths = [
            score.feedback
            for score in dimension_scores
            if score.score >= 0.75
        ]

        weaknesses = [
            score.feedback
            for score in dimension_scores
            if score.score < 0.6
        ]

        # Generate improvement suggestions
        improvement_suggestions = await self._generate_improvements(
            dimension_scores=dimension_scores,
            synthesized_plan=synthesized_plan
        )

        # Determine quality level
        quality_level = self._determine_quality_level(overall_score)

        return QualityAssessmentResult(
            overall_score=round(overall_score, 2),
            dimension_scores=dimension_scores,
            strengths=strengths,
            weaknesses=weaknesses,
            improvement_suggestions=improvement_suggestions,
            quality_level=quality_level
        )

    async def _assess_dimension(
        self,
        dimension: QualityDimension,
        synthesized_plan: str,
        agent_analyses: List[Dict[str, Any]],
        consensus_result: Any
    ) -> QualityScore:
        """Assess a single quality dimension"""

        dimension_prompts = {
            QualityDimension.LEGAL_SOUNDNESS: """评估该法律方案的法律依据充分性：
1. 引用的法律条文是否准确和相关
2. 法律论证是否有说服力
3. 是否考虑了相关法律原则、监管要求与证据规则
4. 法律依据是否足以支撑结论

评分标准（0-1）：
- 0.9-1.0: 法律依据充分、准确、权威
- 0.7-0.9: 法律依据较充分，有少量可改进之处
- 0.5-0.7: 法律依据基本充分，但存在明显不足
- 0.3-0.5: 法律依据不足或部分不准确
- 0-0.3: 法律依据严重不足或错误""",

            QualityDimension.LOGICAL_COHERENCE: """评估该法律方案的逻辑连贯性：
1. 论证结构是否清晰
2. 各部分之间是否存在逻辑矛盾
3. 结论是否从前提自然得出
4. 论证链条是否完整

评分标准（0-1）：
- 0.9-1.0: 逻辑严密，论证完整
- 0.7-0.9: 逻辑基本清晰，有小的瑕疵
- 0.5-0.7: 逻辑基本成立，但有明显跳跃
- 0.3-0.5: 存在逻辑矛盾或断层
- 0-0.3: 逻辑混乱""",

            QualityDimension.COMPLETENESS: """评估该法律方案的全面性：
1. 是否覆盖了所有关键法律问题
2. 是否考虑了多个法律视角
3. 是否分析了正反两方面
4. 是否遗漏重要因素

评分标准（0-1）：
- 0.9-1.0: 分析全面，无明显遗漏
- 0.7-0.9: 基本全面，有少量遗漏
- 0.5-0.7: 覆盖主要方面，但有重要遗漏
- 0.3-0.5: 分析不够全面
- 0-0.3: 严重不完整""",

            QualityDimension.PRACTICAL_FEASIBILITY: """评估该法律方案的可操作性：
1. 建议是否具体明确
2. 是否考虑了实施的可行性
3. 是否提供了具体的行动步骤
4. 是否考虑了实际约束条件

评分标准（0-1）：
- 0.9-1.0: 高度可操作，有具体步骤
- 0.7-0.9: 基本可操作，需要细化
- 0.5-0.7: 部分可操作，较为抽象
- 0.3-0.5: 可操作性较差
- 0-0.3: 基本不可操作""",

            QualityDimension.RISK_AWARENESS: """评估该法律方案的风险意识：
1. 是否识别了主要法律风险
2. 是否提出了风险应对措施
3. 是否考虑了不同情景
4. 是否有风险预警机制

评分标准（0-1）：
- 0.9-1.0: 风险识别全面，应对充分
- 0.7-0.9: 识别主要风险，有应对措施
- 0.5-0.7: 识别部分风险，应对不足
- 0.3-0.5: 风险意识较弱
- 0-0.3: 缺乏风险意识""",

            QualityDimension.CONSISTENCY: """评估该法律方案的内部一致性：
1. 不同部分的观点是否一致
2. 是否存在自相矛盾
3. 建议是否与分析相符
4. 整体立场是否统一

评分标准（0-1）：
- 0.9-1.0: 完全一致，无矛盾
- 0.7-0.9: 基本一致，有小的不协调
- 0.5-0.7: 存在一些不一致
- 0.3-0.5: 有明显矛盾
- 0-0.3: 严重不一致"""
        }

        prompt = f"""{dimension_prompts.get(dimension, '')}

法律方案：
{synthesized_plan}

请评估并输出JSON格式：
{{
    "score": 0.85,
    "feedback": "具体评价",
    "evidence": ["证据1", "证据2"]
}}
"""

        try:
            result = await self.llm_model.generate_json(
                prompt,
                system_prompt="你是一位资深的法律质量评估专家"
            )

            return QualityScore(
                dimension=dimension,
                score=result.get('score', 0.5),
                feedback=result.get('feedback', ''),
                evidence=result.get('evidence', [])
            )

        except Exception as e:
            # Fallback scoring
            return QualityScore(
                dimension=dimension,
                score=0.7,
                feedback=f"{dimension.value}评估失败",
                evidence=[]
            )

    async def _generate_improvements(
        self,
        dimension_scores: List[QualityScore],
        synthesized_plan: str
    ) -> List[str]:
        """Generate improvement suggestions based on scores"""

        # Find dimensions with low scores
        weak_dimensions = [
            score for score in dimension_scores
            if score.score < 0.7
        ]

        if not weak_dimensions:
            return ["方案质量优秀，无需重大改进"]

        improvement_prompt = f"""基于以下质量评估结果，提供3-5条具体的改进建议：

需要改进的方面：
{chr(10).join(f"- {d.dimension.value}: {d.score:.2f} - {d.feedback}" for d in weak_dimensions)}

当前方案：
{synthesized_plan[:500]}...

请提供具体、可操作的改进建议。

输出JSON格式：
{{
    "suggestions": ["建议1", "建议2", ...]
}}
"""

        try:
            result = await self.llm_model.generate_json(
                improvement_prompt,
                system_prompt="你是法律方案优化专家"
            )

            return result.get('suggestions', [])

        except Exception:
            # Fallback suggestions
            return [
                f"加强{d.dimension.value}方面的分析"
                for d in weak_dimensions[:3]
            ]

    def _determine_quality_level(self, overall_score: float) -> str:
        """Determine quality level based on overall score"""

        if overall_score >= 0.85:
            return "excellent"  # 优秀
        elif overall_score >= 0.70:
            return "good"  # 良好
        elif overall_score >= 0.55:
            return "fair"  # 中等
        else:
            return "poor"  # 较差

    def get_quality_report(self, assessment: QualityAssessmentResult) -> str:
        """Generate human-readable quality report"""

        quality_labels = {
            "excellent": "优秀",
            "good": "良好",
            "fair": "中等",
            "poor": "较差"
        }

        report = f"""## 质量评估报告

**总体评分**: {assessment.overall_score:.2f} / 1.00
**质量等级**: {quality_labels.get(assessment.quality_level, '未知')}

### 各维度评分

"""

        for score in assessment.dimension_scores:
            report += f"- **{score.dimension.value}**: {score.score:.2f} - {score.feedback}\n"

        if assessment.strengths:
            report += "\n### 优势\n\n"
            for strength in assessment.strengths:
                report += f"- {strength}\n"

        if assessment.weaknesses:
            report += "\n### 不足\n\n"
            for weakness in assessment.weaknesses:
                report += f"- {weakness}\n"

        if assessment.improvement_suggestions:
            report += "\n### 改进建议\n\n"
            for i, suggestion in enumerate(assessment.improvement_suggestions, 1):
                report += f"{i}. {suggestion}\n"

        return report
