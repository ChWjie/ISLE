import json
import logging
from sqlalchemy.orm import Session
from app.models.database import Simulation, Plan
from app.services.llm_client import get_llm_client, ChatMessage

logger = logging.getLogger(__name__)

async def analyze_evidence_impact(simulation_id: str, argument_text: str, win_rate_delta: float, db: Session):
    """
    Analyze the impact of evidence/arguments used in a round.
    If the win rate improved (delta > 0), identify key evidence as 'effective'.
    If the win rate dropped (delta < 0), identify as 'ineffective' or 'risky'.

     Updates Simulation.evidence_stats
    """
    try:
        if not argument_text or abs(win_rate_delta) < 1.0:
            # Ignore small fluctuations or empty arguments
            return

        simulation = db.query(Simulation).filter(Simulation.session_id == simulation_id).first()
        if not simulation:
            return

        llm_client = get_llm_client()

        # Determine sentiment
        impact_type = "positive" if win_rate_delta > 0 else "negative"

        prompt = f"""
        You are a Legal Analyst.
        Analyze the following legal argument and extract 1-3 key pieces of EVIDENCE or LEGAL BASIS (e.g., specific Treaty Articles, Historical Documents, Maps, Precedents) that were likely responsible for the {impact_type} impact.

        Argument:
        "{argument_text}"

        Return ONLY a JSON list of strings. Example: ["PIPL Article 13", "Employment Contract Clause 8"]
        """

        response = await llm_client.chat(
            messages=[ChatMessage(role="user", content=prompt)],
            max_tokens=100,
            temperature=0.1
        )

        extracted_evidence = []
        try:
            # clean response slightly in case of markdown
            cleaned_resp = response.replace("```json", "").replace("```", "").strip()
            extracted_evidence = json.loads(cleaned_resp)
        except Exception:
            logger.warning(f"Failed to parse evidence extraction JSON: {response}")
            return

        if not extracted_evidence:
            return

        # Update Evidence Stats in Simulation
        # Structure: { "positive": {"Frequency": count, "Impact": sum_delta}, "negative": ... }
        stats = simulation.evidence_stats or {"positive": {}, "negative": {}}

        # Ensure deep copy if needed, but here simple assignment usually works with JSON types in some ORMs,
        # but to be safe we read-modify-write.
        # Note: In SQLite/Postgres via SQLAlchemy, mutating a JSON dict in place detected cleanly?
        # Often needs 'flag_modified' or reassignment. We will reassign.

        target_dict = stats[impact_type]

        for item in extracted_evidence:
            if item not in target_dict:
                target_dict[item] = {"count": 0, "total_delta": 0.0}

            target_dict[item]["count"] += 1
            target_dict[item]["total_delta"] += win_rate_delta

        simulation.evidence_stats = stats
        # Flagging modified for some SQLAlchemy versions might be needed:
        # from sqlalchemy.orm.attributes import flag_modified
        # flag_modified(simulation, "evidence_stats")

        # Re-assigning the whole dict usually works
        simulation.evidence_stats = dict(stats)

        db.commit()
        logger.info(f"Updated evidence stats for simulation {simulation_id}: {extracted_evidence} (Delta: {win_rate_delta})")

        return {
            "evidence": extracted_evidence,
            "impact": impact_type,
            "delta": win_rate_delta
        }

    except Exception as e:
        logger.error(f"Error in analyze_evidence_impact: {e}")

async def generate_optimized_plan(simulation_id: str, db: Session) -> dict:
    """
    Generate an optimized plan based on simulation history and evidence stats.
    """
    try:
        # 1. Fetch Simulation Data
        simulation = db.query(Simulation).filter(Simulation.session_id == simulation_id).first()
        if not simulation or not simulation.plan_id:
            raise ValueError("Simulation or Plan not found")

        original_plan = db.query(Plan).filter(Plan.id == simulation.plan_id).first()
        if not original_plan:
            raise ValueError("Original Plan not found")

        # 2. Analyze Simulation History (Rounds & Evidence Stats)
        evidence_stats = simulation.evidence_stats or {"positive": {}, "negative": {}}

        # Format effective evidence
        effective_evidence = []
        for ev, data in evidence_stats.get("positive", {}).items():
            effective_evidence.append(f"- {ev} (Used {data['count']} times, Win Rate Delta: +{data['total_delta']:.1f}%)")

        # Format ineffective/risky evidence
        risky_evidence = []
        for ev, data in evidence_stats.get("negative", {}).items():
            risky_evidence.append(f"- {ev} (Used {data['count']} times, Win Rate Delta: {data['total_delta']:.1f}%)")

        # Fetch Opponent's Strongest Arguments (where we lost points)
        # Simple heuristic: Rounds where win rate dropped significantly
        # (This would ideally query SimulationRound, for now we infer from context)

        # 3. Construct Prompt for Optimization
        prompt = f"""
        You are a Legal Strategist specializing in corporate compliance and dispute resolution.

        【Task】
        Optimize the following Legal Plan based on the results of a "Red Team" simulation.

        【Original Plan】
        {original_plan.content_md}

        【Simulation Feedback】
        1. **Effective Strategies (Reinforce these)**:
        {chr(10).join(effective_evidence) if effective_evidence else "(None identified)"}

        2. **Weaknesses & Risks (Address/Remove these)**:
        {chr(10).join(risky_evidence) if risky_evidence else "(None identified)"}

        【Optimization Instructions】
        1. **Refine Logic**: Remove or modify arguments that were proven ineffective.
        2. **Strengthen Basis**: Expand on the evidence that showed positive impact.
        3. **Add Counter-Measures**: Add a new section "Simulation-Derived Countermeasures" to address potential opponent moves.
        4. **Structure**: Keep the original structure but update the content.

        Return the response in this JSON format:
        {{
            "optimized_content": "Full markdown content...",
            "changes_summary": "Bullet points of key changes made..."
        }}
        """

        # 4. Call LLM
        llm_client = get_llm_client()
        response = await llm_client.chat(
            messages=[ChatMessage(role="user", content=prompt)],
            max_tokens=2000,
            temperature=0.4
        )

        # 5. Parse Response
        try:
            # Clean markdown code blocks if present
            cleaned_resp = response.replace("```json", "").replace("```", "").strip()
            result = json.loads(cleaned_resp)
        except json.JSONDecodeError:
            # Fallback if valid JSON not returned
            logger.warning("LLM did not return valid JSON for optimization")
            result = {
                "optimized_content": response,
                "changes_summary": "Auto-generated from simulation feedback."
            }

        return {
            "original_plan": original_plan.content_md,
            "optimized_plan": result.get("optimized_content", ""),
            "changes_summary": result.get("changes_summary", "")
        }

    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        raise e
