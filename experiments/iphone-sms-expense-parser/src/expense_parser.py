import re
from datetime import datetime
from typing import Dict, List, Optional, Any

DEFAULT_CATEGORIES = {
    "food": ["starbucks", "mcdonalds", "restaurant", "cafe", "uber eats", "doordash", "grocery", "supermarket"],
    "transport": ["uber", "lyft", "shell", "chevron", "gas", "metro", "transit", "parking"],
    "utilities": ["electric", "water", "gas bill", "internet", "verizon", "att", "t-mobile"],
    "shopping": ["amazon", "apple", "target", "walmart", "nike", "store"]
}

class ExpenseParser:
    def __init__(self, category_rules: Optional[Dict[str, List[str]]] = None):
        self.categories = category_rules or DEFAULT_CATEGORIES

    def parse_sms(self, sms_text: str) -> Optional[Dict[str, Any]]:
        if not sms_text or not isinstance(sms_text, str):
            return None

        # Match amount like $45.50, USD 45.50, 45.50 USD, or 45.50
        amount_match = re.search(r'(?:[\$€£]|USD|EUR|GBP)?\s*(\d+(?:\.\d{2})?)', sms_text, re.IGNORECASE)
        if not amount_match:
            return None
        
        try:
            amount = float(amount_match.group(1))
        except ValueError:
            return None

        # Determine transaction type
        lower_text = sms_text.lower()
        if any(w in lower_text for w in ["credited", "deposit", "received", "refund"]):
            tx_type = "credit"
        elif any(w in lower_text for w in ["spent", "debited", "paid", "purchase", "card"]):
            tx_type = "debit"
        else:
            tx_type = "debit" # default assumption for expense trackers

        # Extract merchant heuristic: look for words after 'at' or 'to'
        merchant = "Unknown"
        at_match = re.search(r'\b(?:at|to|parser)\s+([A-Za-z0-9\s]+?)(?:\s+on|\s+via|\.|$)', sms_text, re.IGNORECASE)
        if at_match:
            merchant = at_match.group(1).strip()
        else:
            # Fallback: find first capitalized word or known keyword
            for cat, keywords in self.categories.items():
                for kw in keywords:
                    if kw in lower_text:
                        merchant = kw.title()
                        break
                if merchant != "Unknown":
                    break

        category = self.categorize_merchant(merchant)

        return {
            "amount": amount,
            "type": tx_type,
            "merchant": merchant,
            "category": category,
            "raw_text": sms_text.strip(),
            "timestamp": datetime.utcnow().isoformat()
        }

    def categorize_merchant(self, merchant: str) -> str:
        m_lower = merchant.lower()
        for category, keywords in self.categories.items():
            for kw in keywords:
                if kw in m_lower:
                    return category
        return "general"

    def summarize(self, parsed_expenses: List[Dict[str, Any]]) -> Dict[str, float]:
        summary = {}
        for exp in parsed_expenses:
            if exp.get("type") == "debit":
                cat = exp.get("category", "general")
                summary[cat] = summary.get(cat, 0.0) + exp.get("amount", 0.0)
        return summary
