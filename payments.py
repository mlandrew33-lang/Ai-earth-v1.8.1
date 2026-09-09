"""AI Earth payment gateway.

Default mode is ``sandbox`` and uses an internal test/voucher rail.  This rail
never moves real money and intentionally requires no merchant verification.
For production, a licensed/legitimate provider can be connected through the
provider-neutral interface; AI Earth never stores card numbers, CVVs or PINs.
"""
import hashlib, json, os, time, urllib.parse
from dataclasses import dataclass, asdict
from typing import Dict, Any
from .owner_finance import OwnerFinance
from .marketplace import Marketplace

@dataclass
class Deposit:
    id: str
    amount: float
    currency: str
    status: str = "pending"
    provider: str = "sandbox"
    provider_payment_id: str = ""
    created_at: float = 0.0

class PaymentManager:
    def __init__(self, storage_path="data/payments.json"):
        self.storage_path = storage_path
        self.deposits: Dict[str, Deposit] = {}
        self._load()
        self.owner_finance = OwnerFinance()
        self.marketplace = Marketplace(self.owner_finance)

    @property
    def mode(self):
        return os.getenv("AI_EARTH_PAYMENT_MODE", "sandbox").lower()

    def _load(self):
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self.deposits = {k: Deposit(**v) for k, v in raw.items()}
        except (FileNotFoundError, ValueError, TypeError):
            self.deposits = {}

    def _save(self):
        import pathlib
        pathlib.Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump({k: asdict(v) for k, v in self.deposits.items()}, f, indent=2)

    @staticmethod
    def _signature(data: Dict[str, Any], secret: str = "") -> str:
        parts = []
        for key, value in data.items():
            if value != "":
                parts.append(f"{key}={urllib.parse.quote_plus(str(value).strip())}")
        if secret:
            parts.append(f"secret={urllib.parse.quote_plus(secret.strip())}")
        return hashlib.sha256("&".join(parts).encode()).hexdigest()

    def create_checkout(self, amount: float, email: str = "", return_url: str = "", cancel_url: str = "", notify_url: str = ""):
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero")
        deposit_id = f"dep_{int(time.time()*1000)}"
        d = Deposit(deposit_id, round(amount, 2), "ZAR", provider=self.mode, created_at=time.time())
        self.deposits[deposit_id] = d
        self._save()

        if self.mode in {"sandbox", "voucher", "test"}:
            # A local test/voucher checkout. No real funds are moved.
            html = (
                f'<form action="{urllib.parse.quote(return_url or "/api/payments/test-complete")}" method="post">'
                f'<input type="hidden" name="m_payment_id" value="{deposit_id}">'
                f'<input type="hidden" name="amount" value="{d.amount:.2f}">'
                f'<input type="hidden" name="email" value="{urllib.parse.quote(email)}">'
                '<button type="submit">Complete test payment</button></form>'
            )
            return d, html

        raise RuntimeError("No live payment provider is configured. Use sandbox/voucher/test for no-verification testing, or connect a legitimate provider for real money.")

    def create_product_checkout(self, listing_id: str, email: str = "", return_url: str = "", cancel_url: str = "", notify_url: str = ""):
        sale = self.marketplace.create_sale(listing_id, email)
        if self.mode in {"sandbox", "voucher", "test"}:
            html = (
                f'<form action="{urllib.parse.quote(return_url or "/api/payments/test-complete")}" method="post">'
                f'<input type="hidden" name="m_payment_id" value="{sale.id}">'
                f'<input type="hidden" name="amount" value="{sale.amount:.2f}">'
                '<button type="submit">Complete test purchase</button></form>'
            )
            return sale, html
        raise RuntimeError("No live payment provider is configured.")

    def complete_test_payment(self, payment_id: str):
        d = self.deposits.get(payment_id)
        if not d:
            return None
        if d.status == "completed":
            return d
        d.status = "completed"
        d.provider_payment_id = f"test_{payment_id}"
        self.owner_finance.add("deposit", d.amount, "completed", f"Sandbox test payment {d.provider_payment_id}")
        self._save()
        return d

    def verify_and_apply_itn(self, payload: Dict[str, Any]):
        """Compatibility hook for a future legitimate provider webhook."""
        payment_id = str(payload.get("m_payment_id", ""))
        d = self.deposits.get(payment_id)
        if not d:
            return None
        if payload.get("payment_status") != "COMPLETE":
            d.status = str(payload.get("payment_status", "failed")).lower()
            self._save()
            return d
        if round(float(payload.get("amount_gross", payload.get("amount", 0))), 2) != d.amount:
            raise ValueError("Payment amount mismatch")
        d.status = "completed"
        d.provider_payment_id = str(payload.get("pf_payment_id", payload.get("provider_payment_id", "")))
        self.owner_finance.add("deposit", d.amount, "completed", f"Payment {d.provider_payment_id}")
        self._save()
        return d
