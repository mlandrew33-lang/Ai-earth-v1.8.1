"""AI Earth external digital-product marketplace.

Products are listed for sale in ZAR. Checkout is hosted by PayFast, so AI Earth
never receives card/bank credentials. Completed payments create a realized-profit
ledger entry after a configurable platform fee and record a local delivery path.
"""
import json, pathlib, time, urllib.parse, hashlib
from dataclasses import dataclass, asdict
from typing import Dict, Any
from .owner_finance import OwnerFinance

@dataclass
class Listing:
    id: str
    business_id: str
    product_id: str
    name: str
    kind: str
    price: float
    file_path: str = ""
    active: bool = True

@dataclass
class Sale:
    id: str
    listing_id: str
    amount: float
    fee: float
    net_profit: float
    email: str
    status: str = "pending"
    provider_payment_id: str = ""
    created_at: float = 0.0

class Marketplace:
    def __init__(self, owner_finance: OwnerFinance, path="data/marketplace.json"):
        self.owner_finance = owner_finance
        self.path = path
        self.listings: Dict[str, Listing] = {}
        self.sales: Dict[str, Sale] = {}
        self._load()

    def _load(self):
        try:
            raw = json.loads(pathlib.Path(self.path).read_text(encoding="utf-8"))
            self.listings = {k: Listing(**v) for k,v in raw.get("listings", {}).items()}
            self.sales = {k: Sale(**v) for k,v in raw.get("sales", {}).items()}
        except (FileNotFoundError, ValueError, TypeError):
            self.listings, self.sales = {}, {}

    def _save(self):
        p=pathlib.Path(self.path); p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"listings":{k:asdict(v) for k,v in self.listings.items()},"sales":{k:asdict(v) for k,v in self.sales.items()}}, indent=2), encoding="utf-8")

    def sync_world(self, world):
        """Expose generated product files as sellable listings."""
        for b in world.businesses.values():
            for p in b.products:
                lid=f"{b.id}_{p.id}"
                path=pathlib.Path("generated_products") / f"{b.id}_{p.id}_day{world.day}.md"
                # Keep the newest generated file if available.
                candidates=sorted(pathlib.Path("generated_products").glob(f"{b.id}_{p.id}_day*.md"))
                file_path=str(candidates[-1]) if candidates else ""
                self.listings[lid]=Listing(lid,b.id,p.id,p.name,p.kind,round(p.price,2),file_path,True)
        self._save()

    def get(self, listing_id):
        return self.listings.get(listing_id)

    def create_sale(self, listing_id, email):
        listing=self.get(listing_id)
        if not listing or not listing.active: raise ValueError("Listing is not available")
        if not email: raise ValueError("Email is required for delivery")
        sid=f"sale_{int(time.time()*1000)}_{len(self.sales)}"
        fee=round(listing.price*0.035,2)
        net=round(listing.price-fee,2)
        sale=Sale(sid,listing.id,listing.price,fee,net,email,status="pending",created_at=time.time())
        self.sales[sid]=sale; self._save(); return sale

    @staticmethod
    def signature(data: Dict[str, Any], passphrase: str=""):
        parts=[]
        for k,v in data.items():
            if v != "": parts.append(f"{k}={urllib.parse.quote_plus(str(v).strip())}")
        if passphrase: parts.append(f"passphrase={urllib.parse.quote_plus(passphrase.strip())}")
        return hashlib.md5("&".join(parts).encode()).hexdigest()

    def complete_sale(self, payload, merchant_id, passphrase):
        sid=str(payload.get("m_payment_id","")); sale=self.sales.get(sid)
        if not sale: return None
        if str(payload.get("merchant_id","")) != str(merchant_id): raise ValueError("Invalid merchant ID")
        if payload.get("payment_status") != "COMPLETE":
            sale.status=str(payload.get("payment_status","failed")).lower(); self._save(); return sale
        if round(float(payload.get("amount_gross",0)),2) != sale.amount: raise ValueError("Payment amount mismatch")
        received=str(payload.get("signature",""))
        if received:
            ordered={k:v for k,v in payload.items() if k!="signature"}
            if self.signature(ordered,passphrase) != received: raise ValueError("Invalid PayFast signature")
        if sale.status == "completed": return sale
        sale.status="completed"; sale.provider_payment_id=str(payload.get("pf_payment_id",""))
        self.owner_finance.add("profit", sale.net_profit, "completed", f"Digital product sale {sale.id}; gross R{sale.amount:.2f}; fee R{sale.fee:.2f}")
        self._save(); return sale
