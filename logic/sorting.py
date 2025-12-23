"""
Sorting functionality for offers/listings.

This module provides the OfferSorter class for sorting listings based on various criteria:
- Price total (ascending/descending)
- Price per square meter (ascending/descending)
- Date posted (newest first)
- Area (ascending/descending)
"""

from copy import deepcopy
from decimal import Decimal
from enum import Enum
from typing import Any, Optional


class SortType(Enum):
    """Sort criteria for offers."""
    PRICE = "price"
    PRICE_PER_SQM = "price_per_sqm"
    DATE_POSTED = "date_posted"
    AREA = "area"
    BEST_MATCH = "najtrafniejsze"


class OfferSorter:
    """
    Class for sorting offers/listings based on various criteria.
    Uses Enum for sort_by parameter for better readability and type safety.
    """

    def __init__(self):
        """Initialize the OfferSorter."""
        pass

    def _get_price_per_sqm(self, offer: dict[str, Any]) -> Optional[Decimal]:
        """
        Retrieve or compute price per square meter.
        - Prefer "price_per_sqm_detailed"
        - Fallback to "price_sqm_zl"
        - If missing, try to compute from price_total_zl and area
        """
        price_per_sqm = offer.get("price_per_sqm_detailed")
        if price_per_sqm is not None:
            return price_per_sqm

        # Use backup field if available
        price_sqm_zl = offer.get("price_sqm_zl")
        if price_sqm_zl is not None:
            return price_sqm_zl

        # Compute from total price and area if possible
        price_total_zl = offer.get("price_total_zl")
        area = offer.get("area")
        if price_total_zl is not None and area not in (None, Decimal("0")):
            try:
                return price_total_zl / area
            except Exception:
                return None

        return None

    def sort(
        self,
        offers: list[dict[str, Any]],
        sort_by: str | None = None,
        order: str = "asc",
    ) -> list[dict[str, Any]]:
        """
        Sort offers based on the specified criteria.

        Args:
            offers: List of offer dictionaries to sort
            sort_by: Sort criterion ("price", "price_per_sqm", "date_posted", "area", or None/"najtrafniejsze")
            order: Sort order ("asc" for ascending, "desc" for descending)

        Returns:
            Sorted list of offers (new list, original is not modified)
        """
        # Default sorting ("najtrafniejsze") returns list unchanged
        if sort_by is None or sort_by == SortType.BEST_MATCH.value:
            return deepcopy(offers)

        sorted_offers = deepcopy(offers)

        try:
            sort_type = SortType(sort_by)
        except ValueError:
            # Unknown sort_by, return unchanged
            return sorted_offers

        reverse = order == "desc"

        def sort_key(offer: dict[str, Any]) -> tuple[bool, Any]:
            """
            Return a tuple for sorting; (is_missing, value).
            None values are sorted to end for asc, start for desc.
            """
            if sort_type == SortType.PRICE:
                value = offer.get("price_total_zl")
            elif sort_type == SortType.AREA:
                value = offer.get("area")
            elif sort_type == SortType.DATE_POSTED:
                value = offer.get("date_posted")
            elif sort_type == SortType.PRICE_PER_SQM:
                value = self._get_price_per_sqm(offer)
            else:
                value = None

            is_missing = value is None
            return (is_missing, value)

        sorted_offers.sort(key=sort_key, reverse=reverse)
        return sorted_offers

