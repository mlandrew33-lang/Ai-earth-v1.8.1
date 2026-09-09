"""Read-only dashboard snapshot helpers for AI Earth."""
from dataclasses import asdict


def _citizen(c, education):
    education.ensure_citizen(c)
    records = {}
    for cid, rec in c.training_records.items():
        records[cid] = asdict(rec)
    return {
        "id": c.id,
        "name": c.name,
        "role": c.role,
        "country": c.country,
        "intelligence_capability": c.intelligence_capability,
        "knowledge": round(c.knowledge_score, 1),
        "experience": round(c.experience_score, 1),
        "training_level": c.training_level,
        "productivity": round(c.productivity, 3),
        "skills": list(c.skills),
        "qualifications": list(c.qualifications),
        "mastery": education.mastery(c),
        "training_records": records,
        "next_recommendation": education.next_recommendation(c),
    }


def snapshot(world, finance, marketplace, education=None):
    from .education import EducationEngine
    education = education or EducationEngine()
    businesses = []
    for b in sorted(world.businesses.values(), key=lambda x: x.profit, reverse=True):
        businesses.append({
            "id": b.id, "name": b.name, "sector": b.sector.value,
            "cash": round(b.cash, 2), "revenue": round(b.revenue, 2),
            "expenses": round(b.expenses, 2), "profit": round(b.profit, 2),
            "employees": len(b.employees), "quality": round(b.quality_score, 1),
            "safety": round(b.safety_score, 1), "security": round(b.security_score, 1),
            "reputation": round(b.reputation, 1), "status": b.status,
        })
    citizens = [_citizen(c, education) for c in world.citizens.values()]
    qualified = sum(1 for c in world.citizens.values() if c.qualifications)
    avg_knowledge = sum(c.knowledge_score for c in world.citizens.values()) / max(1, len(world.citizens))
    return {
        "version": "1.1",
        "day": world.day,
        "economy_value": round(world.economy_value, 2),
        "owner_capital": round(world.owner_capital, 2),
        "treasury": round(world.treasury, 2),
        "external_revenue": round(world.external_revenue, 2),
        "citizens": len(world.citizens),
        "business_count": len(world.businesses),
        "flags": list(world.flags),
        "education": {
            "citizens_with_qualifications": qualified,
            "average_knowledge": round(avg_knowledge, 1),
            "competencies": [asdict(x) for x in education.registry.competencies.values()],
            "qualifications": [asdict(x) for x in education.registry.qualifications.values()],
        },
        "institutions": _institution_snapshot(world),
        "minerals": world.mineral_ecosystem.summary() if world.mineral_ecosystem else {},
        "industry": world.industrial_system.summary() if world.industrial_system else {},
        "citizen_profiles": citizens,
        "businesses": businesses,
        "listings": [asdict(x) for x in marketplace.listings.values() if x.active],
        "sales": [asdict(x) for x in marketplace.sales.values()][-20:],
        "finance": {
            "deposited_principal": round(finance.deposited_principal, 2),
            "realized_profit": round(finance.realized_profit, 2),
            "withdrawn_profit": round(finance.withdrawn_profit, 2),
            "available_profit": round(finance.available_profit, 2),
            "entries": [asdict(x) for x in finance.entries[-30:]],
        },
        "events": [asdict(x) for x in world.events[-30:]],
    }


def _institution_snapshot(world):
    s = world.institutions
    if not s:
        return {}
    return {
        "institutions": [asdict(x) for x in s.institutions.values()],
        "research_projects": [asdict(x) for x in s.research_projects.values()],
        "restaurants": [asdict(x) for x in s.restaurants.values()],
        "game_studios": [asdict(x) for x in s.game_studios.values()],
        "virtual_sports": asdict(s.sports),
        "forces": [asdict(x) for x in s.forces.values()],
    }
