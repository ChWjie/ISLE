from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel

class GameState(BaseModel):
    round_count: int
    tension_level: float      # 0-100
    diplomatic_progress: float # 0-100
    evidence_strength: float  # 0-100
    public_opinion: float     # 0-100 (舆论热度)
    is_terminated: bool = False
    termination_reason: str = ""
    active_risks: List[str] = []
    failed_premises: List[str] = []
    last_their_action: str = "无"  # 记录对方上一轮行动

class BaseRule(ABC):
    @abstractmethod
    def evaluate(self, state: GameState, action: str) -> Any:
        pass

class ActionPermissionRule(BaseRule):
    """
    行动许可规则：基于当前状态判断行动是否被允许
    """
    def evaluate(self, state: GameState, action: str) -> Tuple[bool, str]:
        # 简单逻辑示例：如果紧张局势过高，禁止激进行动
        if "军事演习" in action and state.tension_level > 80:
            return False, "当前局势过热，禁止采取军事刺激行动"

        # 如果舆论过高，限制秘密行动
        if "秘密" in action and state.public_opinion > 90:
            return False, "舆论高度关注下无法执行秘密行动"

        return True, "允许执行"

class RiskTriggerRule(BaseRule):
    """
    风险触发规则：判断行动是否触发特定风险
    """
    def evaluate(self, state: GameState, action: str) -> List[str]:
        triggered_risks = []

        # 规则1: 冲突升级风险
        if "强硬" in action and state.tension_level > 70:
            triggered_risks.append("冲突升级风险")

        # 规则2: 舆论反噬风险
        if "模糊" in action and state.public_opinion > 80:
            triggered_risks.append("舆论反噬风险")

        # 规则3: 外交孤立风险
        if "单边" in action and state.diplomatic_progress < 30:
            triggered_risks.append("外交孤立风险")

        return triggered_risks

class PremiseFailureRule(BaseRule):
    """
    前提失效规则：检查行动的前提条件是否依然成立
    """
    def evaluate(self, state: GameState, action_premises: List[str]) -> List[str]:
        failed = []
        # 示例：假设前提包括"证据充足"
        for premise in action_premises:
            if premise == "evidence_sufficient" and state.evidence_strength < 40:
                failed.append(premise)
            # 更多前提检查逻辑...
        return failed

class TerminationRule(BaseRule):
    """
    终止与回退规则：判断博弈是否应该强制结束
    """
    def evaluate(self, state: GameState) -> Tuple[bool, str]:
        if state.round_count >= 10:
             return True, "达到最大回合数"

        if state.tension_level >= 100:
            return True, "冲突全面爆发，博弈失败"

        if state.diplomatic_progress >= 90:
            return True, "达成外交共识，博弈胜利"

        if len(state.active_risks) >= 3:
            return True, "累积风险过高，强制熔断"

        return False, ""

class GameRuleEngine:
    def __init__(self):
        self.permission_rule = ActionPermissionRule()
        self.risk_rule = RiskTriggerRule()
        self.premise_rule = PremiseFailureRule()
        self.termination_rule = TerminationRule()

    def check_action(self, state: GameState, action: str) -> Tuple[bool, str]:
        return self.permission_rule.evaluate(state, action)

    def check_risks(self, state: GameState, action: str) -> List[str]:
        return self.risk_rule.evaluate(state, action)

    def check_premises(self, state: GameState, premises: List[str]) -> List[str]:
        return self.premise_rule.evaluate(state, premises)

    def check_termination(self, state: GameState) -> Tuple[bool, str]:
        return self.termination_rule.evaluate(state)
