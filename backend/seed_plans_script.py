
import sys
import os
import random
import uuid
from datetime import datetime, timedelta

# 添加当前目录到Python路径
sys.path.append(os.getcwd())

from app.database import SessionLocal, init_db
from app.models.database import Event, Plan

def seed_plans():
    db = SessionLocal()
    try:
        print("Starting plans seeding...")

        # Get existing events to link to
        events = db.query(Event).all()
        if not events:
            print("No events found! Please run seed_events_script.py first.")
            return

        plans_data = [
            {
                "title": "南海争议海域常态化巡航执法方案",
                "status": "verified",
                "risk_score": 35,
                "content": "# 南海争议海域常态化巡航执法方案\n\n## 1. 行动目标\n建立常态化巡航机制，宣示主权，遏制非法侵权行为...",
                "feasibility": 85,
            },
            {
                "title": "针对外籍渔船非法捕捞的应急处置预案",
                "status": "deployed",
                "risk_score": 45,
                "content": "# 应急处置预案\n\n## 1. 预警机制\n利用卫星遥感与AIS数据...",
                "feasibility": 90,
            },
            {
                "title": "东海油气田设施安全保卫法律对策",
                "status": "draft",
                "risk_score": 60,
                "content": "# 安全保卫法律对策\n\n## 1. 法律依据\n依据《联合国海洋法公约》第60条...",
                "feasibility": 70,
            },
            {
                "title": "应对某国单方面划界主张的外交与法律反制方案",
                "status": "verified",
                "risk_score": 55,
                "content": "# 外交与法律反制方案\n\n## 1. 外交声明\n发布严正声明，重申我方立场...",
                "feasibility": 80,
            },
            {
                "title": "涉外海事纠纷仲裁应对策略分析报告",
                "status": "draft",
                "risk_score": 25,
                "content": "# 仲裁应对策略\n\n## 1. 管辖权异议\n首先对仲裁庭管辖权提出异议...",
                "feasibility": 95,
            }
        ]

        created_count = 0
        for plan_tmpl in plans_data:
            # Randomly pick an event
            event = random.choice(events)

            plan_id = f"PLAN-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

            plan = Plan(
                plan_id=plan_id,
                name=plan_tmpl["title"],
                event_id=event.id,
                content_md=plan_tmpl["content"],
                risk_score=plan_tmpl["risk_score"],
                feasibility_score=plan_tmpl["feasibility"],
                overall_score=(plan_tmpl["risk_score"] + plan_tmpl["feasibility"])/2,
                status=plan_tmpl["status"],
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                action_paths=[{"step": 1, "action": "Initial Assessment"}, {"step": 2, "action": "Legal Review"}],
                risk_assessment={"legal_risk": "Low", "political_risk": "Medium"},
                legal_basis={"UNCLOS": ["Art 56", "Art 58"]}
            )

            db.add(plan)
            created_count += 1
            print(f"Created plan: {plan.name} (Linked to: {event.name})")

        db.commit()
        print(f"Successfully created {created_count} plans!")

    except Exception as e:
        print(f"Error seeding plans: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_plans()
