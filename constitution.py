class Constitution:
    MIN_QUALITY = 62
    MIN_SAFETY = 72
    MIN_SECURITY = 72
    MIN_CASH_BUFFER = 100

    def allows_business(self, business) -> bool:
        return (business.quality_score >= self.MIN_QUALITY and
                business.safety_score >= self.MIN_SAFETY and
                business.security_score >= self.MIN_SECURITY)

    def allows_spending(self, business, amount: float) -> bool:
        return business.cash - amount >= self.MIN_CASH_BUFFER
