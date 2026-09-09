"""Opportunity discovery and governed execution planning for AI Earth.

This module is intentionally provider-agnostic: discovery and financial modelling
can run without moving real money. Execution is delegated to the existing
ExternalEconomyGateway and therefore remains blocked until an explicit provider
is configured and an administrator approves the action.
"""
from __future__ import annotations
import json, pathlib, secrets, time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

@dataclass
class Opportunity:
    id: str
    title: str
    category: str
    description: str
    counterparty: str
    estimated_revenue: float
    estimated_cost: float
    estimated_margin: float
    estimated_time_days: int
    risk: str
    confidence: float
    required_approval: bool = True
    status: str = "identified"
    source: str = "AI Earth Opportunity Scanner"
    execution_plan: List[str] = field(default_factory=list)
    external_record_id: str = ""
    actual_revenue: float = 0.0
    actual_cost: float = 0.0
    actual_profit: float = 0.0
    outcome: str = ""
    created_at: float = field(default_factory=time.time)
    approved_at: float = 0.0
    completed_at: float = 0.0

class OpportunityEngine:
    def __init__(self, storage_path="data/opportunities.json"):
        self.storage_path=storage_path
        self.opportunities: Dict[str,Opportunity]={}
        self.learning: List[dict]=[]
        self._load()
        if not self.opportunities:
            self.seed()

    def _load(self):
        try:
            raw=json.loads(pathlib.Path(self.storage_path).read_text(encoding="utf-8"))
            self.opportunities={k:Opportunity(**v) for k,v in raw.get("opportunities",{}).items()}
            self.learning=raw.get("learning",[])
        except (FileNotFoundError,ValueError,TypeError):
            self.opportunities={}; self.learning=[]

    def _save(self):
        p=pathlib.Path(self.storage_path); p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps({"opportunities":{k:asdict(v) for k,v in self.opportunities.items()},
                                 "learning":self.learning[-500:]},indent=2),encoding="utf-8")

    def seed(self):
        examples=[
            ("SME AI Content Pack","Digital services","Create a monthly content and product-description package for a small business.",
             "Local SME",18000,5500,7,"low",0.82),
            ("Fibre Installation Lead","Connectivity","Qualify and prepare a fibre installation lead for a licensed connectivity partner.",
             "Connectivity partner",32000,9000,14,"medium",0.74),
            ("Data Analysis Service","Professional services","Deliver a scoped data-cleaning and management-reporting service using AI Earth tooling.",
             "South African SME",24000,7000,10,"low",0.79),
            ("Digital Product Bundle","Digital products","Package reusable templates, guides and business assets for lawful online sale.",
             "Online marketplace",12500,2200,5,"low",0.86),
        ]
        for t,c,d,cp,rev,cost,days,risk,conf in examples:
            self.create(t,c,d,cp,rev,cost,days,risk,conf,seeded=True)
        self._save()

    def create(self,title,category,description,counterparty,revenue,cost,time_days,risk,confidence,seeded=False):
        revenue=round(float(revenue),2); cost=round(float(cost),2)
        if revenue<=0 or cost<0: raise ValueError("Revenue must be positive and cost cannot be negative")
        oid="opp_"+secrets.token_hex(6)
        o=Opportunity(oid,title,category,description,counterparty,revenue,cost,round(revenue-cost,2),
                      max(1,int(time_days)),risk,float(confidence),
                      source="Seeded example" if seeded else "AI Earth Opportunity Scanner",
                      execution_plan=["Validate customer need and scope","Confirm price, cost and delivery terms",
                                      "Obtain administrator approval","Execute only through an approved provider",
                                      "Verify payment and record actual outcome"])
        self.opportunities[oid]=o; self._save(); return o

    def score(self,o:Opportunity):
        risk_factor={"low":1.0,"medium":0.75,"high":0.45}.get(o.risk,0.5)
        margin=max(0,o.estimated_margin)/max(1,o.estimated_revenue)
        time_factor=min(1,14/max(1,o.estimated_time_days))
        return round(100*(0.40*o.confidence+0.30*margin+0.20*risk_factor+0.10*time_factor),1)

    def scan(self, world=None):
        # Deterministic scan signals from the current simulated economy.
        if world and len(self.opportunities)<12:
            active=len([o for o in self.opportunities.values() if o.status in ("identified","approved")])
            already_scanned = any(o.title == "Enterprise Research Brief" for o in self.opportunities.values())
            if active<8 and not already_scanned:
                self.create("Enterprise Research Brief","Research","Produce a paid research brief from validated public/owned data.",
                            "Enterprise client",28000,8000,12,"medium",0.77)
        return sorted(self.opportunities.values(),key=self.score,reverse=True)

    def approve(self,oid,actor):
        o=self.opportunities[oid]
        if o.status!="identified": raise ValueError(f"Opportunity is {o.status}")
        o.status="approved"; o.approved_at=time.time(); self._save(); return o

    def link_execution(self,oid,record_id):
        o=self.opportunities[oid]; o.external_record_id=record_id; self._save(); return o

    def complete(self,oid,revenue,cost,outcome="completed"):
        o=self.opportunities[oid]
        if o.status!="approved": raise ValueError("Only approved opportunities can complete")
        o.actual_revenue=round(float(revenue),2); o.actual_cost=round(float(cost),2)
        o.actual_profit=round(o.actual_revenue-o.actual_cost,2); o.outcome=outcome
        o.status="completed"; o.completed_at=time.time()
        self.learning.append({"opportunity_id":oid,"estimated_revenue":o.estimated_revenue,
                              "actual_revenue":o.actual_revenue,"estimated_cost":o.estimated_cost,
                              "actual_cost":o.actual_cost,"profit":o.actual_profit,
                              "success":o.actual_profit>0,"recorded_at":time.time()})
        self._save(); return o

    def dashboard(self):
        vals=list(self.opportunities.values())
        return {
            "opportunities":[{**asdict(o),"score":self.score(o)} for o in sorted(vals,key=self.score,reverse=True)],
            "counts":{s:sum(o.status==s for o in vals) for s in ("identified","approved","completed","rejected")},
            "estimated_revenue":round(sum(o.estimated_revenue for o in vals if o.status in ("identified","approved")),2),
            "estimated_profit":round(sum(o.estimated_margin for o in vals if o.status in ("identified","approved")),2),
            "realized_revenue":round(sum(o.actual_revenue for o in vals),2),
            "realized_profit":round(sum(o.actual_profit for o in vals),2),
            "learning_events":len(self.learning),
        }
