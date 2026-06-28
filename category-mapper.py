"""
app/services/category_mapper.py
 
Rule-based category suggestion from vendor name and line item descriptions.
Runs before any LLM is considered — cheap, fast, and good enough for the
common cases (utilities, insurance, known property management vendors, etc.).
 
Extend VENDOR_RULES and KEYWORD_RULES as you learn your users' vendor patterns.
If confidence here is low, the caller can optionally escalate to an LLM.
"""
 
from __future__ import annotations
 
import re
 
from app.database.models.expense import ExpenseCategory
 
 
# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------
 
# Vendor substrings → category. Matched case-insensitively against vendor name.
# More specific patterns should come first within each list.
VENDOR_RULES: list[tuple[str, ExpenseCategory]] = [
    # Utilities
    ("electric", ExpenseCategory.UTILITIES),
    ("gas company", ExpenseCategory.UTILITIES),
    ("atmos", ExpenseCategory.UTILITIES),
    ("water", ExpenseCategory.UTILITIES),
    ("internet", ExpenseCategory.UTILITIES),
    ("comcast", ExpenseCategory.UTILITIES),
    ("at&t", ExpenseCategory.UTILITIES),
    ("spectrum", ExpenseCategory.UTILITIES),
    # Insurance
    ("insurance", ExpenseCategory.INSURANCE),
    ("allstate", ExpenseCategory.INSURANCE),
    ("state farm", ExpenseCategory.INSURANCE),
    ("farmers", ExpenseCategory.INSURANCE),
    ("liberty mutual", ExpenseCategory.INSURANCE),
    # Property tax
    ("tax collector", ExpenseCategory.PROPERTY_TAX),
    ("county tax", ExpenseCategory.PROPERTY_TAX),
    ("assessor", ExpenseCategory.PROPERTY_TAX),
    # Management fees
    ("management", ExpenseCategory.MANAGEMENT_FEE),
    ("property mgmt", ExpenseCategory.MANAGEMENT_FEE),
    # Landscaping
    ("lawn", ExpenseCategory.LANDSCAPING),
    ("landscape", ExpenseCategory.LANDSCAPING),
    ("mowing", ExpenseCategory.LANDSCAPING),
    ("tree service", ExpenseCategory.LANDSCAPING),
    # Cleaning
    ("cleaning", ExpenseCategory.CLEANING),
    ("maid", ExpenseCategory.CLEANING),
    ("janitorial", ExpenseCategory.CLEANING),
    # Legal / professional
    ("attorney", ExpenseCategory.LEGAL_PROFESSIONAL),
    ("law office", ExpenseCategory.LEGAL_PROFESSIONAL),
    ("cpa", ExpenseCategory.LEGAL_PROFESSIONAL),
    ("accounting", ExpenseCategory.LEGAL_PROFESSIONAL),
    # Common maintenance vendors
    ("plumb", ExpenseCategory.MAINTENANCE),
    ("hvac", ExpenseCategory.MAINTENANCE),
    ("electric contractor", ExpenseCategory.MAINTENANCE),
    ("roofing", ExpenseCategory.CAPEX),
    ("roof", ExpenseCategory.CAPEX),
    ("home depot", ExpenseCategory.MAINTENANCE),
    ("lowe's", ExpenseCategory.MAINTENANCE),
    ("lowes", ExpenseCategory.MAINTENANCE),
]
 
# Line item description substrings → category.
KEYWORD_RULES: list[tuple[str, ExpenseCategory]] = [
    ("repair", ExpenseCategory.MAINTENANCE),
    ("replace", ExpenseCategory.CAPEX),
    ("install", ExpenseCategory.CAPEX),
    ("labor", ExpenseCategory.MAINTENANCE),
    ("parts", ExpenseCategory.MAINTENANCE),
    ("inspection", ExpenseCategory.MAINTENANCE),
    ("pest control", ExpenseCategory.MAINTENANCE),
    ("electric", ExpenseCategory.UTILITIES),
    ("gas", ExpenseCategory.UTILITIES),
    ("water", ExpenseCategory.UTILITIES),
    ("insurance premium", ExpenseCategory.INSURANCE),
    ("mow", ExpenseCategory.LANDSCAPING),
    ("trim", ExpenseCategory.LANDSCAPING),
    ("clean", ExpenseCategory.CLEANING),
    ("legal", ExpenseCategory.LEGAL_PROFESSIONAL),
    ("attorney", ExpenseCategory.LEGAL_PROFESSIONAL),
    ("management fee", ExpenseCategory.MANAGEMENT_FEE),
    ("roof", ExpenseCategory.CAPEX),
    ("hvac", ExpenseCategory.MAINTENANCE),
    ("plumb", ExpenseCategory.MAINTENANCE),
]
 
 
# ---------------------------------------------------------------------------
# Mapper
# ---------------------------------------------------------------------------
 
class CategoryMapper:
    """
    Suggests an ExpenseCategory given a vendor name and/or line items.
 
    Returns None if no rule matches — the caller decides whether to fall
    back to an LLM, default to OTHER, or leave it for human review.
    """
 
    def suggest(
        self,
        vendor: str | None,
        line_items: list[dict] | None = None,
    ) -> str | None:
        # 1. Try vendor name first — usually the most reliable signal.
        if vendor:
            category = self._match_vendor(vendor)
            if category:
                return category.value
 
        # 2. Fall back to scanning line item descriptions.
        if line_items:
            category = self._match_line_items(line_items)
            if category:
                return category.value
 
        return None  # caller can escalate to LLM or default to OTHER
 
    @staticmethod
    def _match_vendor(vendor: str) -> ExpenseCategory | None:
        normalized = vendor.lower()
        for pattern, category in VENDOR_RULES:
            if re.search(re.escape(pattern), normalized):
                return category
        return None
 
    @staticmethod
    def _match_line_items(line_items: list[dict]) -> ExpenseCategory | None:
        # Concatenate all text in line item dicts for a single pass.
        blob = " ".join(
            str(v) for item in line_items for v in item.values()
        ).lower()
        for pattern, category in KEYWORD_RULES:
            if re.search(re.escape(pattern), blob):
                return category
        return None
 
