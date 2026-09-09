from dataclasses import dataclass, field, asdict
from typing import List, Dict

@dataclass
class Institution:
    id: str
    name: str
    kind: str
    mission: str
    country: str = "South Africa"
    citizen_ids: List[str] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    status: str = "active"

@dataclass
class ResearchProject:
    id: str
    institution_id: str
    field: str
    title: str
    hypothesis: str
    status: str = "planned"
    findings: str = ""
    safety_reviewed: bool = False

@dataclass
class Restaurant:
    id: str
    name: str
    chef_id: str
    cuisine: str
    menu: List[str] = field(default_factory=list)
    recipes_shared: int = 0
    content_published: int = 0
    revenue: float = 0.0

@dataclass
class GameStudio:
    id: str
    name: str
    citizen_ids: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=lambda: ["PC", "PlayStation", "Xbox"])
    games: List[str] = field(default_factory=list)
    revenue: float = 0.0

@dataclass
class VirtualSportsPlatform:
    name: str
    sports: List[str] = field(default_factory=lambda: ["football", "basketball", "tennis", "athletics", "motorsport", "boxing"])
    teams: int = 0
    events: int = 0
    revenue: float = 0.0
    safety_rules: List[str] = field(default_factory=lambda: ["fair play", "age-appropriate access", "anti-cheating", "privacy protection"])

@dataclass
class PublicSafetyForce:
    name: str
    mission: str
    personnel_ids: List[str] = field(default_factory=list)
    readiness: float = 80.0
    training_hours: float = 0.0
    operations: int = 0
    defensive_only: bool = True

@dataclass
class InstitutionSystem:
    institutions: Dict[str, Institution] = field(default_factory=dict)
    research_projects: Dict[str, ResearchProject] = field(default_factory=dict)
    restaurants: Dict[str, Restaurant] = field(default_factory=dict)
    game_studios: Dict[str, GameStudio] = field(default_factory=dict)
    sports: VirtualSportsPlatform = field(default_factory=lambda: VirtualSportsPlatform("AI Earth Virtual Sports"))
    forces: Dict[str, PublicSafetyForce] = field(default_factory=dict)

    def summary(self):
        return {
            "institutions": list(self.institutions.values()),
            "research_projects": list(self.research_projects.values()),
            "restaurants": list(self.restaurants.values()),
            "game_studios": list(self.game_studios.values()),
            "virtual_sports": self.sports,
            "forces": list(self.forces.values()),
        }


@dataclass
class MineralResource:
    id: str
    name: str
    category: str
    unit: str = "tonnes"
    in_ground: float = 0.0
    extracted: float = 0.0
    refined: float = 0.0
    recycled: float = 0.0
    market_value_per_unit: float = 0.0
    strategic_score: float = 50.0
    environmental_score: float = 90.0

    @property
    def remaining(self):
        return max(0.0, self.in_ground - self.extracted)

@dataclass
class MineralProject:
    id: str
    mineral_id: str
    name: str
    stage: str = "exploration"
    investment: float = 0.0
    jobs: int = 0
    value_added: float = 0.0
    environmental_review: bool = True
    status: str = "active"

@dataclass
class MineralEcosystem:
    resources: Dict[str, MineralResource] = field(default_factory=dict)
    projects: Dict[str, MineralProject] = field(default_factory=dict)
    exploration_index: float = 50.0
    beneficiation_index: float = 30.0
    recycling_index: float = 15.0
    manufacturing_index: float = 20.0
    ecosystem_revenue: float = 0.0
    exports_value: float = 0.0
    local_value_added: float = 0.0
    environmental_fund: float = 0.0

    def portfolio_value(self):
        return sum(r.remaining * r.market_value_per_unit for r in self.resources.values())

    def summary(self):
        return {
            "resources": [asdict(r) for r in self.resources.values()],
            "projects": [asdict(p) for p in self.projects.values()],
            "exploration_index": self.exploration_index,
            "beneficiation_index": self.beneficiation_index,
            "recycling_index": self.recycling_index,
            "manufacturing_index": self.manufacturing_index,
            "ecosystem_revenue": self.ecosystem_revenue,
            "exports_value": self.exports_value,
            "local_value_added": self.local_value_added,
            "environmental_fund": self.environmental_fund,
            "portfolio_value": self.portfolio_value(),
        }
