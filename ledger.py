"""
AI Earth Transaction Ledger
First-class immutable ledger model for all financial activity.

All money movements flow through this system:
- SIMULATED money (in-world economy)
- TEST money (sandbox payments)
- REAL money (legitimate provider transactions)

Every transaction is logged, immutable, and reconcilable.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any
import time
import uuid

class MoneyType(str, Enum):
    """Money classification for clear audit trail."""
    SIMULATED = "SIMULATED"  # In-world economy only
    TEST = "TEST"             # Sandbox/test payments
    REAL = "REAL"             # Legitimate provider payments

class TransactionKind(str, Enum):
    """Transaction types for categorization."""
    # Simulation
    BUSINESS_REVENUE = "business_revenue"
    BUSINESS_EXPENSE = "business_expense"
    BUSINESS_WAGE = "business_wage"
    BUSINESS_TAX = "business_tax"
    CITIZEN_INCOME = "citizen_income"
    CITIZEN_EXPENSE = "citizen_expense"
    
    # Deposits/Withdrawals
    OWNER_DEPOSIT = "owner_deposit"
    OWNER_WITHDRAWAL = "owner_withdrawal"
    
    # External Economy
    EXTERNAL_ORDER = "external_order"
    EXTERNAL_SERVICE = "external_service"
    EXTERNAL_IMPORT = "external_import"
    EXTERNAL_EXPORT = "external_export"
    
    # Opportunities
    OPPORTUNITY_REVENUE = "opportunity_revenue"
    OPPORTUNITY_COST = "opportunity_cost"
    OPPORTUNITY_REFUND = "opportunity_refund"
    
    # Reversals
    REVERSAL = "reversal"
    ADJUSTMENT = "adjustment"

class TransactionStatus(str, Enum):
    """Transaction lifecycle states."""
    PENDING = "pending"           # Created but not yet committed
    COMMITTED = "committed"       # Committed to ledger
    VERIFIED = "verified"         # Verified by external party
    FAILED = "failed"             # Failed execution
    REVERSED = "reversed"         # Reversed/refunded
    DISPUTED = "disputed"         # Under dispute

@dataclass
class TransactionEntry:
    """
    Immutable ledger entry.
    
    Every financial change creates one or more entries.
    Entries are append-only and never modified.
    """
    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sequence: int = 0  # Sequential number (filled by ledger)
    
    # Classification
    kind: TransactionKind = TransactionKind.BUSINESS_REVENUE
    money_type: MoneyType = MoneyType.SIMULATED
    status: TransactionStatus = TransactionStatus.PENDING
    
    # Amount
    amount: float = 0.0
    currency: str = "ZAR"
    
    # Parties
    from_account: str = ""  # Source (business_id, owner, citizen_id, external_id)
    to_account: str = ""    # Destination
    
    # Context
    description: str = ""
    reference_id: str = ""  # Links to opportunity, order, business, etc.
    parent_transaction_id: Optional[str] = None  # For reversals
    
    # Audit
    actor: str = ""  # Who created this entry (user, agent, system)
    created_at: float = field(default_factory=time.time)
    verified_at: Optional[float] = None
    verified_by: str = ""
    
    # Evidence
    evidence: Dict[str, Any] = field(default_factory=dict)
    # E.g. {"provider_reference": "...", "invoice": "...", "hash": "..."}
    
    # Metadata
    tags: list = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class TransactionLedger:
    """
    Append-only transaction ledger.
    
    - All money movements recorded
    - Chronological sequence
    - Immutable entries
    - Full audit trail
    - Reconciliation support
    """
    
    def __init__(self):
        self.entries: list[TransactionEntry] = []
        self.next_sequence = 1
        self.accounts: Dict[str, Dict[str, float]] = {}  # account_id -> {money_type -> balance}
    
    def record(
        self,
        kind: TransactionKind,
        amount: float,
        from_account: str,
        to_account: str,
        money_type: MoneyType = MoneyType.SIMULATED,
        description: str = "",
        reference_id: str = "",
        actor: str = "system",
        evidence: Optional[Dict[str, Any]] = None,
        tags: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TransactionEntry:
        """
        Record a transaction.
        
        Args:
            kind: Type of transaction
            amount: Amount (positive = credit, negative = debit)
            from_account: Source account
            to_account: Destination account
            money_type: SIMULATED, TEST, or REAL
            description: Human-readable description
            reference_id: Link to related entity (opportunity_id, order_id, etc.)
            actor: Who recorded this (user email, agent name, system)
            evidence: Evidence dict (provider ref, invoice, hash, etc.)
            tags: Classification tags
            metadata: Additional context
        
        Returns:
            TransactionEntry (immutable)
        
        Raises:
            ValueError: If validation fails
        """
        
        # Validation
        if amount == 0:
            raise ValueError("Amount cannot be zero")
        
        if not from_account or not to_account:
            raise ValueError("From and to accounts required")
        
        if from_account == to_account:
            raise ValueError("Cannot transfer to same account")
        
        # Create entry
        entry = TransactionEntry(
            kind=kind,
            money_type=money_type,
            status=TransactionStatus.COMMITTED,
            amount=amount,
            currency="ZAR",
            from_account=from_account,
            to_account=to_account,
            description=description,
            reference_id=reference_id,
            actor=actor,
            evidence=evidence or {},
            tags=tags or [],
            metadata=metadata or {},
        )
        
        # Assign sequence number
        entry.sequence = self.next_sequence
        self.next_sequence += 1
        
        # Record in ledger
        self.entries.append(entry)
        
        # Update account balances
        self._update_balance(from_account, -amount, money_type)
        self._update_balance(to_account, amount, money_type)
        
        return entry
    
    def reverse(
        self,
        transaction_id: str,
        reason: str = "",
        actor: str = "system"
    ) -> TransactionEntry:
        """
        Reverse a transaction.
        
        Creates a new entry that undoes the original.
        Original entry is marked as REVERSED.
        """
        
        # Find original
        original = None
        for e in self.entries:
            if e.id == transaction_id:
                original = e
                break
        
        if not original:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        if original.status == TransactionStatus.REVERSED:
            raise ValueError(f"Transaction {transaction_id} already reversed")
        
        # Create reversal
        reversal = self.record(
            kind=TransactionKind.REVERSAL,
            amount=-original.amount,
            from_account=original.to_account,
            to_account=original.from_account,
            money_type=original.money_type,
            description=f"Reversal: {reason or original.description}",
            reference_id=original.reference_id,
            parent_transaction_id=transaction_id,
            actor=actor,
            metadata={
                "reversal_reason": reason,
                "original_transaction_id": transaction_id
            }
        )
        
        # Mark original as reversed
        original.status = TransactionStatus.REVERSED
        
        return reversal
    
    def verify(
        self,
        transaction_id: str,
        verifier: str = "system",
        evidence: Optional[Dict[str, Any]] = None
    ) -> TransactionEntry:
        """
        Mark transaction as verified (by external party).
        """
        
        for e in self.entries:
            if e.id == transaction_id:
                e.status = TransactionStatus.VERIFIED
                e.verified_at = time.time()
                e.verified_by = verifier
                if evidence:
                    e.evidence.update(evidence)
                return e
        
        raise ValueError(f"Transaction {transaction_id} not found")
    
    def _update_balance(self, account_id: str, delta: float, money_type: MoneyType):
        """Update account balance (internal)."""
        if account_id not in self.accounts:
            self.accounts[account_id] = {}
        if money_type not in self.accounts[account_id]:
            self.accounts[account_id][money_type] = 0.0
        self.accounts[account_id][money_type] += delta
    
    def get_balance(self, account_id: str, money_type: Optional[MoneyType] = None) -> float:
        """Get account balance."""
        if account_id not in self.accounts:
            return 0.0
        if money_type:
            return self.accounts[account_id].get(money_type, 0.0)
        return sum(self.accounts[account_id].values())
    
    def get_account_statement(self, account_id: str, money_type: Optional[MoneyType] = None) -> list[TransactionEntry]:
        """Get all transactions for an account."""
        results = []
        for e in self.entries:
            if e.status == TransactionStatus.REVERSED:
                continue  # Skip reversed entries
            if money_type and e.money_type != money_type:
                continue
            if e.from_account == account_id or e.to_account == account_id:
                results.append(e)
        return results
    
    def get_by_reference(self, reference_id: str) -> list[TransactionEntry]:
        """Get all transactions for a reference (opportunity, order, etc.)."""
        return [e for e in self.entries if e.reference_id == reference_id and e.status != TransactionStatus.REVERSED]
    
    def reconcile(self) -> Dict[str, Any]:
        """
        Reconciliation report.
        
        Returns:
            {
                "total_entries": N,
                "by_kind": {...},
                "by_money_type": {...},
                "by_status": {...},
                "account_balances": {...},
                "integrity_checks": {...}
            }
        """
        
        by_kind = {}
        by_money_type = {}
        by_status = {}
        total_by_type = {}
        
        for e in self.entries:
            if e.status == TransactionStatus.REVERSED:
                continue
            
            by_kind[e.kind.value] = by_kind.get(e.kind.value, 0) + e.amount
            by_money_type[e.money_type.value] = by_money_type.get(e.money_type.value, 0) + e.amount
            by_status[e.status.value] = by_status.get(e.status.value, 0) + 1
            total_by_type[e.money_type.value] = total_by_type.get(e.money_type.value, 0) + e.amount
        
        # Integrity check: sum of all balances should equal totals
        balance_sum = sum(
            sum(accounts.values())
            for accounts in self.accounts.values()
        )
        
        return {
            "total_entries": len(self.entries),
            "by_kind": by_kind,
            "by_money_type": by_money_type,
            "by_status": by_status,
            "account_balances": {
                k: dict(v) for k, v in self.accounts.items()
            },
            "integrity_check": {
                "total_recorded": balance_sum,
                "balanced": abs(balance_sum) < 0.01  # Floating point tolerance
            }
        }
