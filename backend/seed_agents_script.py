
import sys
import os
from sqlalchemy.orm import Session
from datetime import datetime

# Ensure app can be imported
sys.path.append(os.getcwd())

from app.database import SessionLocal, engine
from app.models.database import Base, Agent, AgentType

# Re-create tables if needed (optional, here we assume schema is updated)
Agent.__table__.drop(engine, checkfirst=True)
Base.metadata.create_all(bind=engine)

def _template_to_agent(template):
    config = template.get("default_config", {})
    return {
        "agent_id": template["template_id"],
        "name": template["name"],
        "agent_type": template["agent_type"],
        "description": template["description"],
        "mission": template.get("mission"),
        "responsibilities": template.get("responsibilities"),
        "system_prompt": template["system_prompt"],
        "stance": "企业合规与争议解决场景下的专业、中立、可执行法律建议",
        "goals": config.get("goals", ["risk_control", "compliance"]),
        "strategy_orientation": config.get("strategy_orientation", "balanced"),
        "legal_priority": config.get("legal_priority", "corporate_compliance"),
        "knowledge_scope": config.get("knowledge_scope", ["企业合规"]),
        "llm_config": {
            "temperature": config.get("temperature", 0.4),
            "max_tokens": config.get("max_tokens", 1800),
        },
        "template_id": template["template_id"],
    }


def seed_agents():
    """Seed the D06 enterprise-compliance agent set.

    This runtime definition intentionally overrides the legacy maritime-law
    seeding logic above, so running this script inserts the 23 compliance,
    dispute, opposing-party and adjudication agents used by the frontend.
    """
    from app.services.agent_service import AGENT_TEMPLATES

    db = SessionLocal()
    try:
        templates = []
        for group in ("blue", "red", "judge"):
            templates.extend(AGENT_TEMPLATES.get(group, []))

        db.query(Agent).delete()
        for template in templates:
            agent = Agent(**_template_to_agent(template))
            db.add(agent)
            print(f"[OK] 已插入: {agent.name}")

        db.commit()
        total = db.query(Agent).count()
        print(f"\n[DONE] 完成！数据库中现有 agents 数量：{total}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_agents()
