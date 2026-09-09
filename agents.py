from dataclasses import dataclass
from typing import List

from .models import World, Business, Citizen

@dataclass
class Decision:
    agent: str
    action: str
    target: str
    reason: str
    approved: bool = True

class SpecialistAgent:
    name = "Specialist"
    def evaluate(self, world: World) -> List[Decision]:
        return []

class FinanceAgent(SpecialistAgent):
    name = "FINANCE"
    def evaluate(self, world):
        decisions = []
        for b in world.businesses.values():
            if b.status == "active" and b.cash < 120:
                decisions.append(Decision(self.name, "freeze_spending", b.id, f"Cash buffer is low at R{b.cash:.0f}."))
            if b.debt > max(500, b.cash * 1.5):
                decisions.append(Decision(self.name, "review_debt", b.id, "Debt is high relative to available cash."))
        return decisions

class QualityAgent(SpecialistAgent):
    name = "QUALITY"
    def evaluate(self, world):
        return [Decision(self.name, "quality_hold", b.id, f"Quality score {b.quality_score:.1f} is below 62.", False)
                for b in world.businesses.values() if b.quality_score < 62]

class SafetyAgent(SpecialistAgent):
    name = "SAFETY"
    def evaluate(self, world):
        return [Decision(self.name, "safety_hold", b.id, f"Safety score {b.safety_score:.1f} is below 72.", False)
                for b in world.businesses.values() if b.safety_score < 72]

class SecurityAgent(SpecialistAgent):
    name = "SECURITY"
    def evaluate(self, world):
        return [Decision(self.name, "security_hold", b.id, f"Security score {b.security_score:.1f} is below 72.", False)
                for b in world.businesses.values() if b.security_score < 72]

class MarketAgent(SpecialistAgent):
    name = "MARKET"
    def evaluate(self, world):
        ranked = sorted((b for b in world.businesses.values() if b.status == "active"), key=lambda b: b.profit, reverse=True)
        if not ranked:
            return []
        return [Decision(self.name, "expand", ranked[0].id, "Highest current profit; candidate for controlled expansion.")]

class TrainingAgent(SpecialistAgent):
    name = "TRAINING"
    def evaluate(self, world):
        citizens = sorted(world.citizens.values(), key=lambda c: c.training_level)
        return [Decision(self.name, "train", c.id, "Lowest training level receives priority.") for c in citizens[:3]]

class ResearchAgent(SpecialistAgent):
    name = "RESEARCH"
    def evaluate(self, world):
        return [Decision(self.name, "experiment", b.id, "Research review identifies an opportunity to improve the product.")
                for b in world.businesses.values() if b.status == "active" and b.profit > 0][:2]

class CitizenAgent:
    def __init__(self, citizen: Citizen):
        self.citizen = citizen

    def propose(self, world: World) -> Decision | None:
        c = self.citizen
        if c.employer_id is None and c.cash >= 700 and "strategy" in c.skills:
            return Decision(c.name, "found_business", c.id, "Entrepreneurial citizen has capital and strategy skill.")
        if c.employer_id and c.cash > 1400:
            return Decision(c.name, "save_invest", c.employer_id, "Citizen has accumulated enough cash to consider investment.")
        return None

class WorldController:
    """Coordinates specialist agents. It cannot violate constitutional holds."""
    def __init__(self):
        self.specialists = [FinanceAgent(), MarketAgent(), QualityAgent(), SafetyAgent(), SecurityAgent(), TrainingAgent(), ResearchAgent()]

    def deliberate(self, world: World) -> List[Decision]:
        decisions = []
        for agent in self.specialists:
            decisions.extend(agent.evaluate(world))
        for citizen in world.citizens.values():
            proposal = CitizenAgent(citizen).propose(world)
            if proposal:
                decisions.append(proposal)
        return decisions
