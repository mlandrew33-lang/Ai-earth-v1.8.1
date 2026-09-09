import json, pathlib
from dataclasses import asdict
from .models import World

def save_world(world: World, path="data/world.json"):
    p = pathlib.Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    # Simple JSON snapshot for audit/restart. Enum values are serialized as strings.
    data = asdict(world)
    for b in data.get("businesses", {}).values():
        b["sector"] = str(b["sector"].value if hasattr(b["sector"], "value") else b["sector"])
    p.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
