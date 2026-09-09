from dataclasses import dataclass, field, asdict
from typing import Dict, List

@dataclass
class ManufacturingPlant:
    id: str
    name: str
    product: str
    inputs: List[str]
    jobs: int = 0
    capacity: float = 100.0
    utilization: float = 0.0
    output: float = 0.0
    revenue: float = 0.0
    status: str = "active"

@dataclass
class ManufacturedProduct:
    id: str
    name: str
    category: str
    mineral_inputs: List[str]
    unit_value: float
    units_produced: float = 0.0
    units_sold: float = 0.0

@dataclass
class IndustrialSystem:
    plants: Dict[str, ManufacturingPlant] = field(default_factory=dict)
    products: Dict[str, ManufacturedProduct] = field(default_factory=dict)
    industrial_revenue: float = 0.0
    exports: float = 0.0
    domestic_sales: float = 0.0
    industrial_jobs: int = 0
    energy_efficiency: float = 70.0
    automation_index: float = 35.0

    def summary(self):
        return {
            "plants": [asdict(x) for x in self.plants.values()],
            "products": [asdict(x) for x in self.products.values()],
            "industrial_revenue": self.industrial_revenue,
            "exports": self.exports,
            "domestic_sales": self.domestic_sales,
            "industrial_jobs": self.industrial_jobs,
            "energy_efficiency": self.energy_efficiency,
            "automation_index": self.automation_index,
        }
