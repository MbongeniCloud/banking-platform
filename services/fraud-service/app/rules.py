from decimal import Decimal

RULES = [
    {
        "name": "large_transaction",
        "description": "Transaction exceeds R50,000",
        "check": lambda t: Decimal(t["amount"]) > Decimal("50000")
    },
    {
        "name": "round_amount",
        "description": "Suspiciously round large amount",
        "check": lambda t: Decimal(t["amount"]) % 10000 == 0 and Decimal(t["amount"]) >= 10000
    },
    {
        "name": "rapid_withdrawal",
        "description": "Multiple withdrawals flagged",
        "check": lambda t: t["transaction_type"] == "withdrawal" and Decimal(t["amount"]) > 20000
    }
]

def evaluate(transaction: dict) -> dict:
    triggered = [r for r in RULES if r["check"](transaction)]
    score = len(triggered) * 33
    return {
        "transaction_id": transaction["id"],
        "account_id": transaction["account_id"],
        "fraud_score": min(score, 99),
        "is_flagged": len(triggered) > 0,
        "triggered_rules": [r["name"] for r in triggered]
    }