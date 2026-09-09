from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict

class Sector(str, Enum):
    PUBLISHING = "Publishing"
    MEDIA = "Media"
    EDUCATION = "Education"
    SOFTWARE = "Software"
    DESIGN = "Design"
    RESEARCH = "Research"
    FINANCE = "Finance"
    SERVICES = "Services"

@dataclass
class Citizen:
    id: str
    name: str
    role: str
    skills: List[str]
    personality: str
    cash: float = 1000.0
    employer_id: str | None = None
    training_level: int = 1
    productivity: float = 1.0
    intelligence_capability: int = 228
    country: str = "South Africa"
    knowledge_score: float = 20.0
    experience_score: float = 0.0
    mastery_scores: Dict[str, float] = field(default_factory=dict)
    training_records: Dict[str, object] = field(default_factory=dict)
    qualifications: List[str] = field(default_factory=list)
    learning_goal: str = "Become a master in a chosen field"

@dataclass
class Product:
    id: str
    business_id: str
    name: str
    kind: str
    price: float
    quality: float
    demand: float
    units_sold: int = 0

@dataclass
class Business:
    id: str
    name: str
    sector: Sector
    cash: float
    employees: List[str]
    revenue: float = 0.0
    expenses: float = 0.0
    reputation: float = 70.0
    quality_score: float = 80.0
    safety_score: float = 90.0
    security_score: float = 90.0
    products: List[Product] = field(default_factory=list)
    status: str = "active"
    debt: float = 0.0

    @property
    def profit(self) -> float:
        return self.revenue - self.expenses

@dataclass
class Event:
    day: int
    kind: str
    message: str
    amount: float = 0.0
    actor: str | None = None

@dataclass
class World:
    day: int = 0
    owner_capital: float = 10000.0
    treasury: float = 25000.0
    citizens: Dict[str, Citizen] = field(default_factory=dict)
    businesses: Dict[str, Business] = field(default_factory=dict)
    events: List[Event] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    external_revenue: float = 0.0
    institutions: object = None
    mineral_ecosystem: object = None
    industrial_system: object = None

    @property
    def economy_value(self) -> float:
        business_value = sum(b.cash + max(0, b.revenue * 0.5) - b.debt for b in self.businesses.values())
        citizen_cash = sum(c.cash for c in self.citizens.values())
        return self.treasury + business_value + citizen_cash
