import random
from .models import World, Event
from .agents import WorldController, Decision
from .constitution import Constitution
from .agent_brain import AgentBrain
from .product_factory import ProductFactory
from .education import EducationEngine

class EconomyEngine:
    def __init__(self, world: World, seed: int = 42):
        self.world = world
        self.random = random.Random(seed)
        self.controller = WorldController()
        self.constitution = Constitution()
        self.brain = AgentBrain()
        self.product_factory = ProductFactory()
        self.education = EducationEngine()
        for citizen in self.world.citizens.values():
            self.education.ensure_citizen(citizen)

    def log(self, kind, message, amount=0.0, actor=None):
        self.world.events.append(Event(self.world.day, kind, message, amount, actor))

    def apply_decision(self, d: Decision):
        w = self.world
        if d.action in {"quality_hold", "safety_hold", "security_hold"}:
            b = w.businesses.get(d.target)
            if b:
                b.status = "review"
                w.flags.append(f"{d.agent} HOLD: {b.name} — {d.reason}")
                self.log("oversight", f"{d.agent} placed {b.name} on review hold.", actor=d.agent)
            return
        if d.action == "freeze_spending":
            self.log("finance", f"Finance AI froze discretionary spending for {w.businesses[d.target].name}.", actor=d.agent)
        elif d.action == "expand":
            b = w.businesses[d.target]
            if self.constitution.allows_spending(b, 50) and w.treasury >= 50:
                w.treasury -= 50; b.cash += 50
                self.log("allocation", f"World Controller approved controlled expansion for {b.name}.", 50, "WORLD_CONTROLLER")
        elif d.action == "train":
            c = w.citizens[d.target]
            if w.treasury >= 15:
                w.treasury -= 15
                competency = self.education.next_recommendation(c)
                rec = self.education.train(c, competency, hours=2.0, practical=True)
                self.education.award_qualifications(c)
                self.log("training", f"Training AI developed {c.name} in {competency}; mastery score {c.mastery_scores[competency]:.1f}.", 15, "TRAINING")
        elif d.action == "experiment":
            b = w.businesses[d.target]
            b.quality_score = min(100, b.quality_score + 0.8)
            self.log("research", f"Research AI ran an improvement experiment for {b.name}.", actor="RESEARCH")
        elif d.action == "review_debt":
            self.log("finance", f"Finance AI requested debt review for {w.businesses[d.target].name}.", actor="FINANCE")
        elif d.action == "save_invest":
            self.log("citizen", f"{d.agent} proposed investment in {d.target}.", actor=d.agent)
        elif d.action == "found_business":
            self.log("citizen", f"{d.agent} proposed founding a new business; Governance review required.", actor=d.agent)

    def run_institutions(self):
        system = self.world.institutions
        if not system:
            return
        # Research produces logged, safety-reviewed simulated findings.
        for project in system.research_projects.values():
            if project.status == "active" and project.safety_reviewed:
                project.status = "completed"
                project.findings = project.findings or "Finding recorded after controlled simulation and review."
                inst = system.institutions.get(project.institution_id)
                if inst:
                    inst.findings.append(project.findings)
                self.log("research", f"{project.title} produced a reviewed finding.", actor=project.institution_id)
        # Chefs operate restaurants and publish recipes/media as economic products.
        for restaurant in system.restaurants.values():
            restaurant.recipes_shared += 1
            restaurant.content_published += 1
            restaurant.revenue += 75.0
            self.world.external_revenue += 75.0
            self.log("culinary", f"{restaurant.name} published a recipe and cooking content.", 75.0, restaurant.chef_id)
        # Game studio iterates cross-platform builds; sales remain simulated until an external store integration exists.
        for studio in system.game_studios.values():
            studio.revenue += 120.0
            self.world.external_revenue += 120.0
            self.log("games", f"{studio.name} shipped a cross-platform game build for {', '.join(studio.platforms)}.", 120.0, studio.id)
        system.sports.events += 1
        system.sports.revenue += 50.0
        self.world.external_revenue += 50.0
        self.log("sports", "Virtual Sports platform hosted a fair-play event.", 50.0, "SPORT-01")
        for force in system.forces.values():
            force.training_hours += 4.0
            force.readiness = min(100.0, force.readiness + 0.2)
            force.operations += 1
            self.log("public_safety", f"{force.name} completed a defensive readiness exercise.", actor=force.name)


    def run_mineral_ecosystem(self):
        eco = self.world.mineral_ecosystem
        if not eco:
            return
        # Responsible simulated extraction; every project requires environmental review.
        for project in eco.projects.values():
            resource = eco.resources[project.mineral_id]
            if not project.environmental_review or project.status != "active":
                continue
            extraction = min(resource.remaining * 0.00002, 120.0)
            resource.extracted += extraction
            beneficiation = extraction * (0.25 + eco.beneficiation_index / 400.0)
            resource.refined += beneficiation
            eco.local_value_added += beneficiation * resource.market_value_per_unit * 0.12
            eco.exports_value += extraction * resource.market_value_per_unit * 0.035
            eco.ecosystem_revenue += extraction * resource.market_value_per_unit * 0.08
            eco.environmental_fund += extraction * resource.market_value_per_unit * 0.01
            project.value_added += beneficiation * resource.market_value_per_unit
            project.stage = "beneficiation" if eco.beneficiation_index > 35 else "extraction"
            self.log("minerals", f"{resource.name}: responsible extraction and beneficiation cycle completed.", extraction * resource.market_value_per_unit, project.id)
        # Recycling and downstream manufacturing grow alongside local beneficiation.
        for resource in eco.resources.values():
            recycled = min(resource.refined * 0.0025, 25.0)
            resource.recycled += recycled
        eco.exploration_index = min(100.0, eco.exploration_index + 0.4)
        eco.beneficiation_index = min(100.0, eco.beneficiation_index + 0.35)
        eco.recycling_index = min(100.0, eco.recycling_index + 0.25)
        eco.manufacturing_index = min(100.0, eco.manufacturing_index + 0.3)
        self.world.external_revenue += eco.ecosystem_revenue * 0.001

    def run_manufacturing(self):
        industry = self.world.industrial_system
        eco = self.world.mineral_ecosystem
        if not industry or not eco:
            return
        for plant in industry.plants.values():
            if plant.status != "active":
                continue
            readiness = min((eco.beneficiation_index + eco.manufacturing_index) / 2, 100.0)
            plant.utilization = max(10.0, min(95.0, readiness * 0.8 + self.random.uniform(-4, 4)))
            output = plant.capacity * plant.utilization / 1000.0
            product = next((p for p in industry.products.values() if p.name == plant.product), None)
            if not product:
                continue
            # Production consumes a small share of refined inputs, never exceeding available material.
            limiting = 1.0
            for mid in product.mineral_inputs:
                resource = eco.resources.get(mid)
                if not resource or resource.refined <= 0:
                    limiting = 0.0
                    break
                limiting = min(limiting, resource.refined / 1000.0)
            output = min(output, limiting)
            if output <= 0:
                continue
            for mid in product.mineral_inputs:
                eco.resources[mid].refined = max(0.0, eco.resources[mid].refined - output * 0.2)
            product.units_produced += output
            sold = output * (0.65 + self.random.random() * 0.25)
            product.units_sold += sold
            revenue = sold * product.unit_value
            plant.output += output
            plant.revenue += revenue
            industry.industrial_revenue += revenue
            industry.domestic_sales += revenue * 0.65
            industry.exports += revenue * 0.35
            self.world.external_revenue += revenue * 0.05
            self.log("manufacturing", f"{plant.name} produced {output:.2f} units of {product.name} and sold {sold:.2f}.", revenue, plant.id)
        industry.energy_efficiency = min(100.0, industry.energy_efficiency + 0.12)
        industry.automation_index = min(100.0, industry.automation_index + 0.2)

    def deliberate(self):
        decisions = self.controller.deliberate(self.world)
        # Optional model-powered proposals. Every proposal still passes through apply_decision.
        if self.brain.llm.enabled():
            specialist_summary = [{'agent': d.agent, 'action': d.action, 'target': d.target, 'reason': d.reason} for d in decisions[:30]]
            decisions.extend(self.brain.controller_plan(self.world, specialist_summary))
            for citizen in list(self.world.citizens.values())[:12]:
                proposal = self.brain.citizen_decision(citizen, self.world)
                if proposal:
                    decisions.append(proposal)
        for d in decisions:
            self.apply_decision(d)
        return decisions

    def generate_products(self):
        for b in self.world.businesses.values():
            if b.status != 'active' or not b.products:
                continue
            if self.world.day == 1 or self.world.day % 3 == 0:
                path, source = self.product_factory.create(b, b.products[0], self.world.day)
                self.log('product', f'{b.name} released {b.products[0].name} using {source} generation.', actor=b.id)

    def run(self, days=1):
        for _ in range(max(0, int(days))):
            self.advance_day()
        return self.world

    def advance_day(self):
        w = self.world
        w.day += 1
        daily_revenue = 0.0
        for b in w.businesses.values():
            if b.status != "active":
                continue
            quality_factor = max(0.35, min(1.25, b.quality_score / 80))
            demand_factor = 0.75 + self.random.random() * 0.65
            productivity = sum(w.citizens[c].productivity for c in b.employees) / max(1, len(b.employees))
            units = max(0, int((2 + len(b.employees)/5) * demand_factor * quality_factor * productivity))
            product = b.products[0]
            sales = units * product.price
            b.cash += sales; b.revenue += sales; product.units_sold += units; daily_revenue += sales
            self.log("sale", f"{b.name} sold {units} {product.kind}(s).", sales, b.id)
            wages = min(sum(22 + 8*w.citizens[cid].training_level for cid in b.employees), max(0, b.cash * 0.5))
            b.cash -= wages; b.expenses += wages
            per = wages / max(1, len(b.employees))
            for cid in b.employees: w.citizens[cid].cash += per
            self.log("wages", f"{b.name} paid employee wages.", wages, b.id)
            ops = min(b.cash, 30 + len(b.employees)*4)
            b.cash -= ops; b.expenses += ops
            self.log("expense", f"{b.name} paid operating costs.", ops, b.id)
            b.quality_score = max(40, min(100, b.quality_score + self.random.uniform(-1.5, 1.8)))
            b.safety_score = max(55, min(100, b.safety_score + self.random.uniform(-1.0, 1.2)))
            b.security_score = max(50, min(100, b.security_score + self.random.uniform(-1.2, 1.0)))
            b.reputation = max(30, min(100, b.reputation + self.random.uniform(-0.7, 0.8)))
        tax = daily_revenue * 0.03; w.treasury += tax
        self.log("tax", "Treasury collected internal transaction tax.", tax, "TREASURY")
        self.deliberate()
        self.generate_products()
        self.run_institutions()
        self.run_mineral_ecosystem()
        self.run_manufacturing()
        w.flags = list(dict.fromkeys(w.flags))[-30:]
        self.log("day_end", f"Day {w.day} closed. Economy value: {w.economy_value:,.2f}", actor="WORLD")
        return w
