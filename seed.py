from .models import World, Citizen, Business, Sector, Product
from .institutions import InstitutionSystem, Institution, ResearchProject, Restaurant, GameStudio, PublicSafetyForce, MineralEcosystem, MineralResource, MineralProject

NAMES = [
    "Amina", "Liam", "Thandi", "Noah", "Zanele", "Ethan", "Naledi", "Mia", "Sipho", "Leo",
    "Ayanda", "Oliver", "Lerato", "Maya", "Themba", "Ava", "Kabelo", "Sofia", "Bongani", "Ella",
    "Karabo", "Lucas", "Nandi", "Amara", "Siyabonga", "Isla", "Neo", "Grace", "Teboho", "Luna",
    "Mpho", "James", "Refilwe", "Emma", "Tshepo", "Chloe", "Busi", "Daniel", "Kea", "Adam",
    "Lesedi", "Zach", "Onthatile", "Ruby", "Vusi", "Layla", "Tumelo", "Mason", "Palesa", "Aria"
]
ROLES = ["Entrepreneur", "Engineer", "Accountant", "Researcher", "Designer", "Writer", "Marketer", "Teacher", "Analyst", "Operator"]
SKILLS = ["strategy", "writing", "analysis", "design", "coding", "sales", "research", "finance", "teaching", "operations"]
PERSONALITIES = ["bold", "cautious", "creative", "analytical", "competitive", "patient", "curious", "efficient"]

BUSINESSES = [
    ("Aether Press", Sector.PUBLISHING, 5000),
    ("Nova Media", Sector.MEDIA, 5000),
    ("SkillForge Academy", Sector.EDUCATION, 5000),
    ("Orbit Software", Sector.SOFTWARE, 5000),
    ("PixelFoundry", Sector.DESIGN, 4000),
    ("DeepMind Labs", Sector.RESEARCH, 4000),
    ("Atlas Capital", Sector.FINANCE, 6000),
    ("Vertex Services", Sector.SERVICES, 4000),
]

def seed_world() -> World:
    w = World()
    for i, name in enumerate(NAMES, 1):
        cid = f"C{i:03d}"
        w.citizens[cid] = Citizen(
            id=cid, name=name, role=ROLES[(i-1)%len(ROLES)],
            skills=[SKILLS[(i-1)%len(SKILLS)], SKILLS[(i+2)%len(SKILLS)]],
            personality=PERSONALITIES[(i-1)%len(PERSONALITIES)],
            cash=1000 + (i % 7) * 125,
            intelligence_capability=228,
            country="South Africa",
            learning_goal="Become a master in their chosen field",
            productivity=0.85 + (i % 6) * 0.06,
        )
    for i, (name, sector, cash) in enumerate(BUSINESSES, 1):
        bid = f"B{i:02d}"
        employees = [c.id for c in list(w.citizens.values())[(i-1)*6:i*6]]
        for cid in employees: w.citizens[cid].employer_id = bid
        b = Business(id=bid, name=name, sector=sector, cash=cash, employees=employees)
        b.products = [Product(id=f"P{i:02d}A", business_id=bid, name=f"{name} Starter Product", kind={Sector.PUBLISHING:'book', Sector.MEDIA:'video series', Sector.EDUCATION:'course', Sector.SOFTWARE:'software tool', Sector.DESIGN:'template pack', Sector.RESEARCH:'research report', Sector.FINANCE:'market model', Sector.SERVICES:'service package'}[sector], price=120 + i*15, quality=72+i, demand=0.6 + (i%4)*0.08)]
        w.businesses[bid] = b
    # Advanced institutions and public-service systems.
    system = InstitutionSystem()
    research_ids = ["C004", "C014", "C024", "C034"]
    system.institutions["BIO-01"] = Institution("BIO-01", "AI Earth Institute of Biochemistry", "Biochemistry Institute", "Study biochemistry, biotechnology, nutrition and life-science questions with safety review.", citizen_ids=research_ids)
    system.institutions["SCI-01"] = Institution("SCI-01", "AI Earth Science Institute", "Science Institute", "Run controlled scientific research, experiments, analysis and publish reproducible findings.", citizen_ids=["C004", "C014", "C024", "C034", "C044"])
    system.research_projects["R-BIO-01"] = ResearchProject("R-BIO-01", "BIO-01", "Biochemistry", "Biomolecule learning project", "How can simulated biochemical models improve educational understanding?", "active", "Simulation findings pending controlled analysis.", True)
    system.research_projects["R-SCI-01"] = ResearchProject("R-SCI-01", "SCI-01", "General Science", "Evidence and measurement project", "How can better experimental logging improve reproducibility?", "active", "Initial result: structured logs improve traceability in simulation.", True)

    chef_ids = ["C006", "C016", "C026", "C036"]
    for idx, cid in enumerate(chef_ids, 1):
        rid = f"REST-{idx:02d}"
        system.restaurants[rid] = Restaurant(rid, ["Earth Table", "Ubuntu Kitchen", "Future Flavours", "Citizen Chef House"][idx-1], cid, ["African fusion", "International", "Healthy cooking", "Creative cuisine"][idx-1], ["signature bowl", "seasonal plate", "chef special"])
    system.institutions["CUL-01"] = Institution("CUL-01", "AI Earth Culinary Academy", "Culinary Institute", "Train chefs to operate restaurants and publish recipes and cooking content.", citizen_ids=chef_ids)

    game_ids = ["C005", "C015", "C025", "C035", "C045"]
    system.game_studios["GAME-01"] = GameStudio("GAME-01", "AI Earth GameWorks", game_ids, ["PC", "PlayStation", "Xbox"], ["Earth Quest", "Citizen Sports", "Future City Builder"])
    system.institutions["GAME-01"] = Institution("GAME-01", "AI Earth Game & Software Studio", "Game Development", "Create original software and games for PC and console platforms, subject to platform licensing and technical requirements.", citizen_ids=game_ids)

    system.sports.teams = 12
    system.sports.events = 24
    system.institutions["SPORT-01"] = Institution("SPORT-01", "AI Earth Virtual Sports Platform", "Virtual Sports", "Run fair-play virtual sports competitions, coaching, analytics and media content.", citizen_ids=["C007", "C017", "C027", "C037"])

    force_specs = [("ARMY", "AI Earth Army", "Defensive land protection, disaster response and emergency logistics."), ("NAVY", "AI Earth Navy", "Maritime safety, rescue, disaster response and territorial defence simulation."), ("POLICE", "AI Earth Police Service", "Public safety, lawful emergency response and community protection."), ("SECURITY", "AI Earth Security Service", "Protect institutions, systems and people through defensive security and incident response.")]
    for key, name, mission in force_specs:
        ids = [f"C{n:03d}" for n in range(1, 51) if (n + len(key)) % 4 == 0][:8]
        system.forces[key] = PublicSafetyForce(name, mission, ids, 82.0, 0.0, 0, True)
        system.institutions[key] = Institution(key, name, "Public Safety", mission, citizen_ids=ids)
    w.institutions = system

    # Mineral wealth ecosystem: exploration -> responsible extraction -> beneficiation -> manufacturing -> recycling.
    minerals = MineralEcosystem()
    mineral_specs = [
        ("PGM", "Platinum Group Metals", "precious/industrial", 1800000, 42000, 95000, 96),
        ("MN", "Manganese", "battery/steel", 12000000, 1800, 70000, 82),
        ("VAN", "Vanadium", "energy storage", 900000, 8500, 28000, 78),
        ("FE", "Iron Ore", "steel", 50000000, 180, 6500, 75),
        ("CR", "Chromium", "steel/alloys", 16000000, 650, 14000, 76),
        ("AU", "Gold", "precious", 3500000, 950000, 120000, 88),
        ("LI", "Lithium", "battery", 1500000, 24000, 52000, 74),
        ("CU", "Copper", "electrical", 7000000, 13000, 46000, 80),
        ("CO", "Cobalt", "battery", 700000, 42000, 90000, 79),
        ("GRAPH", "Graphite", "battery", 3000000, 900, 12000, 70),
        ("REE", "Rare Earth Elements", "advanced technology", 500000, 38000, 115000, 92),
    ]
    for mid, name, category, stock, price, strategic, env in mineral_specs:
        minerals.resources[mid] = MineralResource(mid, name, category, "tonnes", stock, 0, 0, 0, price, strategic, env)
    for idx, mid in enumerate(minerals.resources, 1):
        minerals.projects[f"MIN-{idx:02d}"] = MineralProject(f"MIN-{idx:02d}", mid, f"{minerals.resources[mid].name} Value Chain Project", "exploration", 250000 + idx*50000, 20 + idx*5)
    w.mineral_ecosystem = minerals
    from .manufacturing import IndustrialSystem, ManufacturingPlant, ManufacturedProduct
    industry = IndustrialSystem()
    products = [
        ("BAT", "Grid Battery Pack", "energy storage", ["LI", "MN", "GRAPH"], 18000),
        ("HYD", "Hydrogen Technology Module", "green hydrogen", ["PGM", "VAN"], 24000),
        ("ELEC", "Power Electronics Unit", "electronics", ["CU", "REE"], 12000),
        ("STEEL", "Advanced Steel Component", "advanced manufacturing", ["FE", "CR", "MN"], 8500),
        ("EV", "Electric Mobility Component", "electric mobility", ["LI", "CU", "PGM"], 32000),
    ]
    for pid, name, category, inputs, value in products:
        industry.products[pid] = ManufacturedProduct(pid, name, category, inputs, value)
    for idx, (pid, prod) in enumerate(industry.products.items(), 1):
        industry.plants[f"PLANT-{idx:02d}"] = ManufacturingPlant(f"PLANT-{idx:02d}", f"AI Earth {prod.name} Plant", prod.name, prod.mineral_inputs, 60 + idx * 12, 100.0, 0.0, 0.0, 0.0)
    industry.industrial_jobs = sum(x.jobs for x in industry.plants.values())
    w.industrial_system = industry
    system.institutions["MIN-01"] = Institution("MIN-01", "AI Earth Mineral Resources & Beneficiation Institute", "Mineral Science & Industry", "Map mineral resources, study responsible extraction, beneficiation, recycling and advanced manufacturing with environmental safeguards.", citizen_ids=["C004", "C014", "C024", "C034", "C044"])
    w.events.append(__import__('ai_earth.models', fromlist=['Event']).Event(0, "system", "AI Earth advanced institutions initialized: biochemistry, science, culinary, game development, virtual sports, army, navy, police, security and mineral value chains."))
    w.events.append(__import__('ai_earth.models', fromlist=['Event']).Event(0, "system", "AI Earth v1.0 national civilization world initialized with 50 citizens, 8 businesses and a mineral value-chain ecosystem."))
    return w
