"""Owner capital and profit-withdrawal ledger.

This module deliberately separates deposited principal from realized profit.
It records withdrawal requests; the actual bank payout is performed by the
configured payment provider/merchant account, not by AI Earth itself.
"""
import json, pathlib, time
from dataclasses import dataclass, asdict

@dataclass
class LedgerEntry:
    id: str
    kind: str  # deposit, profit, withdrawal_request, withdrawal_completed
    amount: float
    status: str = "completed"
    note: str = ""
    created_at: float = 0.0

class OwnerFinance:
    def __init__(self, path="data/owner_finance.json", starting_capital=10000.0):
        self.path = path
        self.starting_capital = float(starting_capital)
        self.entries = []
        self._load()

    def _load(self):
        try:
            raw = json.loads(pathlib.Path(self.path).read_text(encoding="utf-8"))
            self.entries = [LedgerEntry(**x) for x in raw.get("entries", [])]
        except (FileNotFoundError, ValueError, TypeError):
            self.entries = []

    def _save(self):
        p = pathlib.Path(self.path); p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"entries": [asdict(x) for x in self.entries]}, indent=2), encoding="utf-8")

    def add(self, kind, amount, status="completed", note=""):
        e = LedgerEntry(f"own_{int(time.time()*1000)}_{len(self.entries)}", kind, round(float(amount),2), status, note, time.time())
        self.entries.append(e); self._save(); return e

    @property
    def deposited_principal(self):
        return sum(e.amount for e in self.entries if e.kind == "deposit" and e.status == "completed") + self.starting_capital

    @property
    def realized_profit(self):
        return sum(e.amount for e in self.entries if e.kind == "profit" and e.status == "completed")

    @property
    def withdrawn_profit(self):
        return sum(e.amount for e in self.entries if e.kind == "withdrawal_completed" and e.status == "completed")

    @property
    def available_profit(self):
        pending = sum(e.amount for e in self.entries if e.kind == "withdrawal_request" and e.status == "pending")
        return max(0.0, self.realized_profit - self.withdrawn_profit - pending)

    def request_profit_withdrawal(self, amount, note=""):
        amount = round(float(amount), 2)
        if amount <= 0: raise ValueError("Withdrawal must be greater than zero")
        if amount > self.available_profit:
            raise ValueError(f"Only R{self.available_profit:,.2f} of realized profit is available")
        return self.add("withdrawal_request", amount, "pending", note)
