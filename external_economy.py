"""Governed bridge between AI Earth and the outside economy.

The gateway separates agent drafting from authorization and execution. External
execution is disabled until a real provider webhook is configured explicitly.
Files are registered with SHA-256 hashes so imports/exports are auditable.
"""
from __future__ import annotations

import hashlib, hmac, json, os, pathlib, secrets, time, urllib.request
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class ExternalRecord:
    id: str
    kind: str
    status: str
    created_at: float
    actor: str
    counterparty: str = ""
    item: str = ""
    amount: float = 0.0
    currency: str = "ZAR"
    details: str = ""
    risk: str = "medium"
    approved_by: str = ""
    approved_at: float = 0.0
    executed_at: float = 0.0
    provider_reference: str = ""
    asset_path: str = ""
    asset_sha256: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExternalEconomyGateway:
    def __init__(self, storage_path="data/external_economy.json", asset_dir="data/external_assets"):
        self.storage_path = storage_path
        self.asset_dir = pathlib.Path(asset_dir)
        self.records: Dict[str, ExternalRecord] = {}
        self.audit: List[dict] = []
        self.spending_limit = float(os.getenv("AI_EARTH_EXTERNAL_SPEND_LIMIT", "250000"))
        self.daily_limit = float(os.getenv("AI_EARTH_EXTERNAL_DAILY_LIMIT", "500000"))
        self._load()

    def _load(self):
        try:
            raw = json.loads(pathlib.Path(self.storage_path).read_text(encoding="utf-8"))
            self.records = {k: ExternalRecord(**v) for k, v in raw.get("records", {}).items()}
            self.audit = raw.get("audit", [])
        except (FileNotFoundError, ValueError, TypeError):
            self.records, self.audit = {}, []

    def _save(self):
        p = pathlib.Path(self.storage_path); p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"records": {k: asdict(v) for k,v in self.records.items()}, "audit": self.audit[-2000:]}, indent=2), encoding="utf-8")

    def _audit(self, action, record_id, actor, detail=""):
        self.audit.append({"at": time.time(), "action": action, "record_id": record_id, "actor": actor, "detail": detail})
        self._save()

    def _risk(self, amount):
        if amount <= 10000: return "low"
        if amount <= self.spending_limit: return "medium"
        return "high"

    def create_order(self, supplier, item, amount, actor="External Economy Agent", details=""):
        amount = round(float(amount), 2)
        if not supplier or not item or amount <= 0: raise ValueError("Supplier, item and positive amount are required")
        rid = "ord_" + secrets.token_hex(6)
        r = ExternalRecord(rid, "order", "pending_approval", time.time(), actor, supplier, item, amount, "ZAR", details, self._risk(amount))
        self.records[rid] = r; self._audit("created", rid, actor, "External order drafted")
        return r

    def create_service(self, service, details, actor="External Economy Agent"):
        if not service: raise ValueError("Service is required")
        rid = "svc_" + secrets.token_hex(6)
        r = ExternalRecord(rid, "service_request", "queued", time.time(), actor, item=service, details=details)
        self.records[rid] = r; self._audit("created", rid, actor, "External service request drafted")
        return r

    def register_asset(self, direction, asset, party, value=0, metadata=None, actor="Import/Export Gateway Agent", asset_path="", asset_sha256=""):
        if direction not in ("import", "export"): raise ValueError("Invalid transfer direction")
        if not asset or not party: raise ValueError("Asset and counterparty are required")
        rid = ("imp_" if direction == "import" else "exp_") + secrets.token_hex(6)
        r = ExternalRecord(rid, direction, "pending_review", time.time(), actor, party, asset, round(float(value),2), "ZAR", metadata=json.loads(json.dumps(metadata or {})), asset_path=asset_path, asset_sha256=asset_sha256)
        self.records[rid] = r; self._audit("created", rid, actor, "Asset transfer registered")
        return r

    def _today_spend(self):
        now = time.time(); day = now - 86400
        return sum(r.amount for r in self.records.values() if r.kind == "order" and r.status == "executed" and r.executed_at >= day)

    def approve(self, record_id, approver, note=""):
        r = self.records.get(record_id)
        if not r: raise KeyError("Record not found")
        if r.status not in ("pending_approval", "pending_review", "queued"):
            raise ValueError(f"Cannot approve status {r.status}")
        if r.kind == "order":
            if r.amount > self.spending_limit: raise ValueError("Order exceeds per-transaction spending limit")
            if self._today_spend() + r.amount > self.daily_limit: raise ValueError("Order exceeds daily external spending limit")
        r.status = "approved"; r.approved_by = approver; r.approved_at = time.time(); r.details = (r.details + " | " + note).strip(" |")
        self._audit("approved", record_id, approver, note); return r

    def reject(self, record_id, actor, reason=""):
        r = self.records.get(record_id)
        if not r: raise KeyError("Record not found")
        r.status = "rejected"; r.details = (r.details + " | REJECTED: " + reason).strip(" |")
        self._audit("rejected", record_id, actor, reason); return r

    def execute(self, record_id, actor="Finance Agent"):
        r = self.records.get(record_id)
        if not r: raise KeyError("Record not found")
        if r.status != "approved": raise ValueError("Only approved records can execute")
        webhook = os.getenv("AI_EARTH_EXTERNAL_EXECUTION_WEBHOOK")
        if not webhook:
            raise RuntimeError("No external execution provider configured. Approval succeeded; execution remains blocked.")
        payload = {"id":r.id,"kind":r.kind,"counterparty":r.counterparty,"item":r.item,
                   "amount":r.amount,"currency":r.currency,"details":r.details,"approved_by":r.approved_by}
        body = json.dumps(payload).encode()
        req = urllib.request.Request(webhook, data=body, headers={"Content-Type":"application/json"}, method="POST")
        secret = os.getenv("AI_EARTH_EXTERNAL_WEBHOOK_SECRET", "")
        if secret:
            req.add_header("X-AI-Earth-Signature", hmac.new(secret.encode(), body, hashlib.sha256).hexdigest())
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status >= 300: raise RuntimeError(f"External provider returned HTTP {resp.status}")
            r.provider_reference = resp.read().decode(errors="replace")[:500]
        r.status = "executed"; r.executed_at = time.time()
        self._audit("executed", record_id, actor, "External action executed")
        return r

    def save_asset(self, filename, content, max_bytes=10*1024*1024):
        if len(content) > max_bytes: raise ValueError("Asset exceeds 10 MB limit")
        safe = pathlib.Path(filename).name
        if not safe or safe in (".", ".."):
            raise ValueError("Invalid filename")
        self.asset_dir.mkdir(parents=True, exist_ok=True)
        token = secrets.token_hex(5) + "_" + safe
        path = self.asset_dir / token
        path.write_bytes(content)
        return str(path), hashlib.sha256(content).hexdigest()

    def dashboard(self):
        vals = list(self.records.values())
        return {
            "orders": [asdict(x) for x in vals if x.kind == "order"],
            "service_requests": [asdict(x) for x in vals if x.kind == "service_request"],
            "imports": [asdict(x) for x in vals if x.kind == "import"],
            "exports": [asdict(x) for x in vals if x.kind == "export"],
            "audit": self.audit[-50:],
            "limits": {"per_transaction": self.spending_limit, "daily": self.daily_limit},
            "execution_provider_configured": bool(os.getenv("AI_EARTH_EXTERNAL_EXECUTION_WEBHOOK")),
        }
