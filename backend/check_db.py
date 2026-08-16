from app.database import SessionLocal
from app.models.database import Agent, Event

db = SessionLocal()

# Check agents
agent_count = db.query(Agent).count()
print(f"Total agents in DB: {agent_count}")

# Check events
event_count = db.query(Event).count()
print(f"Total events in DB: {event_count}")

if agent_count > 0:
    sample_agents = db.query(Agent).limit(3).all()
    print("\nSample agents:")
    for agent in sample_agents:
        print(f"  - {agent.name} ({agent.agent_type})")

if event_count > 0:
    events = db.query(Event).all()
    print("\nEvents:")
    for event in events:
        print(f"  - {event.name} ({event.event_id})")

db.close()
