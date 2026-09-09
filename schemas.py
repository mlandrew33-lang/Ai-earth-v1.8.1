"""
Pydantic schemas for AI Earth API validation.

All API inputs validated against these schemas before processing.
Ensures data integrity and prevents malicious/malformed requests.
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any
from enum import Enum

# ============================================================================
# SIMULATION OPERATIONS
# ============================================================================

class AdvanceSimulationRequest(BaseModel):
    """Advance simulation N days."""
    days: int = Field(1, ge=1, le=30, description="Number of days to simulate (1-30)")
    
    class Config:
        example = {"days": 5}

class AdvanceSimulationResponse(BaseModel):
    """Simulation advancement result."""
    ok: bool
    day: int
    message: Optional[str] = None
    error: Optional[str] = None

# ============================================================================
# EXTERNAL ECONOMY
# ============================================================================

class CreateOrderRequest(BaseModel):
    """Create external supplier order."""
    supplier: str = Field(..., min_length=1, max_length=200)
    item: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0, le=1000000)
    details: str = Field("", max_length=1000)
    
    @validator("amount")
    def amount_precision(cls, v):
        # Max 2 decimal places
        if len(str(v).split('.')[-1]) > 2:
            raise ValueError("Amount must have max 2 decimal places")
        return round(v, 2)
    
    class Config:
        example = {
            "supplier": "Tech Supplies Inc",
            "item": "Server infrastructure",
            "amount": 45000.00,
            "details": "Production environment setup"
        }

class CreateServiceRequest(BaseModel):
    """Create external service request."""
    service: str = Field(..., min_length=1, max_length=200)
    details: str = Field("", max_length=1000)
    
    class Config:
        example = {
            "service": "Data analysis",
            "details": "Customer database analysis and reporting"
        }

class ApproveTransactionRequest(BaseModel):
    """Approve external transaction."""
    id: str = Field(..., min_length=1, max_length=100)
    note: Optional[str] = Field(None, max_length=500)
    
    class Config:
        example = {"id": "ord_abc123", "note": "Approved for execution"}

class RejectTransactionRequest(BaseModel):
    """Reject external transaction."""
    id: str = Field(..., min_length=1, max_length=100)
    reason: Optional[str] = Field(None, max_length=500)
    
    class Config:
        example = {"id": "ord_abc123", "reason": "Budget constraint"}

class ExecuteTransactionRequest(BaseModel):
    """Execute approved transaction."""
    id: str = Field(..., min_length=1, max_length=100)
    
    class Config:
        example = {"id": "ord_abc123"}

class TransactionResponse(BaseModel):
    """Generic transaction response."""
    ok: bool
    message: Optional[str] = None
    error: Optional[str] = None
    record: Optional[Dict[str, Any]] = None

# ============================================================================
# OPPORTUNITIES
# ============================================================================

class ScanOpportunitiesRequest(BaseModel):
    """Scan for opportunities."""
    # Currently no parameters, but framework ready for filters
    pass

class ScanOpportunitiesResponse(BaseModel):
    """Opportunity scan result."""
    ok: bool
    message: str
    opportunities: int
    error: Optional[str] = None

class ApproveOpportunityRequest(BaseModel):
    """Approve opportunity."""
    id: str = Field(..., min_length=1, max_length=100)
    
    class Config:
        example = {"id": "opp_xyz789"}

class ExecuteOpportunityRequest(BaseModel):
    """Execute approved opportunity."""
    id: str = Field(..., min_length=1, max_length=100)
    
    class Config:
        example = {"id": "opp_xyz789"}

class CompleteOpportunityRequest(BaseModel):
    """Mark opportunity complete with actual results."""
    id: str = Field(..., min_length=1, max_length=100)
    revenue: float = Field(..., ge=0, le=10000000)
    cost: float = Field(..., ge=0, le=10000000)
    outcome: str = Field("completed", max_length=50)
    
    @validator("revenue", "cost")
    def amount_precision(cls, v):
        return round(v, 2)
    
    @root_validator
    def revenue_exceeds_cost(cls, values):
        # Optional: Only valid if revenue >= cost
        # Relaxed for now to allow recording losses
        return values
    
    class Config:
        example = {
            "id": "opp_xyz789",
            "revenue": 24000.00,
            "cost": 6500.00,
            "outcome": "completed"
        }

class OpportunityResponse(BaseModel):
    """Opportunity operation response."""
    ok: bool
    message: Optional[str] = None
    error: Optional[str] = None
    record: Optional[Dict[str, Any]] = None

# ============================================================================
# PAYMENTS
# ============================================================================

class CreateDepositRequest(BaseModel):
    """Create deposit for owner capital injection."""
    amount: float = Field(..., gt=0, le=10000000)
    email: str = Field(..., max_length=200)
    base_url: Optional[str] = Field(None, max_length=500)
    
    @validator("amount")
    def amount_precision(cls, v):
        return round(v, 2)
    
    @validator("email")
    def email_valid(cls, v):
        # Basic email validation
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email")
        return v.lower()
    
    class Config:
        example = {
            "amount": 50000.00,
            "email": "owner@company.com",
            "base_url": "https://aiearth.example.com"
        }

class DepositResponse(BaseModel):
    """Deposit creation response."""
    ok: bool
    deposit_id: Optional[str] = None
    status: Optional[str] = None
    mode: Optional[str] = None
    checkout_html: Optional[str] = None
    error: Optional[str] = None

class CompletePaymentRequest(BaseModel):
    """Complete test/sandbox payment."""
    payment_id: str = Field(..., min_length=1, max_length=100)
    
    class Config:
        example = {"payment_id": "dep_1234567890"}

class PaymentResponse(BaseModel):
    """Payment operation response."""
    ok: bool
    status: Optional[str] = None
    payment_id: Optional[str] = None
    error: Optional[str] = None

# ============================================================================
# ASSET TRANSFER (IMPORT/EXPORT)
# ============================================================================

class ImportAssetRequest(BaseModel):
    """Register imported asset."""
    asset: str = Field(..., min_length=1, max_length=200)
    party: str = Field(..., min_length=1, max_length=200)
    value: float = Field(0, ge=0, le=10000000)
    filename: Optional[str] = Field(None, max_length=500)
    content_b64: Optional[str] = Field(None, max_length=50000000)
    
    @validator("value")
    def amount_precision(cls, v):
        return round(v, 2)
    
    class Config:
        example = {
            "asset": "Research dataset",
            "party": "External research partner",
            "value": 5000.00,
            "filename": "dataset_2026_q3.csv"
        }

class ExportAssetRequest(BaseModel):
    """Register exported asset."""
    asset: str = Field(..., min_length=1, max_length=200)
    party: str = Field(..., min_length=1, max_length=200)
    value: float = Field(0, ge=0, le=10000000)
    filename: Optional[str] = Field(None, max_length=500)
    content_b64: Optional[str] = Field(None, max_length=50000000)
    
    @validator("value")
    def amount_precision(cls, v):
        return round(v, 2)
    
    class Config:
        example = {
            "asset": "Analysis report",
            "party": "Client",
            "value": 8000.00,
            "filename": "analysis_report_2026.pdf"
        }

class AssetTransferResponse(BaseModel):
    """Asset transfer response."""
    ok: bool
    message: Optional[str] = None
    error: Optional[str] = None
    record: Optional[Dict[str, Any]] = None

# ============================================================================
# AUTHENTICATION
# ============================================================================

class AdminLoginRequest(BaseModel):
    """Admin authentication."""
    token: str = Field(..., min_length=10, max_length=500)
    
    class Config:
        example = {"token": "your-secure-token-here"}

class AdminLoginResponse(BaseModel):
    """Login response."""
    ok: bool
    message: Optional[str] = None
    error: Optional[str] = None

# ============================================================================
# ERROR RESPONSES
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    ok: bool = False
    error: str
    request_id: Optional[str] = None
    timestamp: Optional[float] = None
    
    class Config:
        example = {
            "ok": False,
            "error": "Invalid amount: must be positive",
            "request_id": "req_abc123xyz",
            "timestamp": 1694270970.123
        }

# ============================================================================
# DASHBOARD RESPONSE
# ============================================================================

class DashboardResponse(BaseModel):
    """Full dashboard state response."""
    version: str
    day: int
    economy_value: float
    owner_capital: float
    treasury: float
    external_revenue: float
    citizens: int
    business_count: int
    flags: List[str]
    education: Dict[str, Any]
    institutions: Dict[str, Any]
    minerals: Dict[str, Any]
    industry: Dict[str, Any]
    citizen_profiles: List[Dict[str, Any]]
    businesses: List[Dict[str, Any]]
    listings: List[Dict[str, Any]]
    sales: List[Dict[str, Any]]
    finance: Dict[str, Any]
    events: List[Dict[str, Any]]
    
    class Config:
        example = {
            "version": "1.1",
            "day": 42,
            "economy_value": 250000.0,
            "owner_capital": 10000.0,
            "treasury": 85000.0,
            "external_revenue": 0.0,
            "citizens": 50,
            "business_count": 8,
            "flags": ["Oversight clear"],
            "education": {},
            "institutions": {},
            "minerals": {},
            "industry": {},
            "citizen_profiles": [],
            "businesses": [],
            "listings": [],
            "sales": [],
            "finance": {"entries": []},
            "events": []
        }

# ============================================================================
# HEALTH CHECK
# ============================================================================

class HealthResponse(BaseModel):
    """Service health response."""
    ok: bool
    service: str
    external_execution_configured: bool
    payment_mode: str
    live: int  # Current simulation day
    
    class Config:
        example = {
            "ok": True,
            "service": "ai-earth-economic-engine",
            "external_execution_configured": False,
            "payment_mode": "sandbox",
            "live": 42
        }
