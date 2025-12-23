"""
Tests for sorting functionality (4.3 - Sortowanie wyników).

This module tests the OfferSorter class for sorting listings based on:
- Price total (ascending/descending)
- Price per square meter (ascending/descending)
- Date posted (newest first)
- Area (ascending/descending)
"""

from datetime import date
from decimal import Decimal

import pytest

from logic.sorting import OfferSorter


@pytest.fixture
def mock_offers():
    """
    Create mock offer data for testing sorting functionality.
    Returns a list of dictionaries representing offers with different values.
    """
    return [
        {
            "listing_id": 1,
            "price_total_zl": Decimal("450000.00"),
            "price_sqm_zl": Decimal("9000.00"),
            "price_per_sqm_detailed": Decimal("9000.00"),
            "area": Decimal("50.00"),
            "date_posted": date(2024, 1, 15),
        },
        {
            "listing_id": 2,
            "price_total_zl": Decimal("300000.00"),
            "price_sqm_zl": Decimal("6666.67"),
            "price_per_sqm_detailed": Decimal("6666.67"),
            "area": Decimal("45.00"),
            "date_posted": date(2024, 2, 20),
        },
        {
            "listing_id": 3,
            "price_total_zl": Decimal("600000.00"),
            "price_sqm_zl": Decimal("7500.00"),
            "price_per_sqm_detailed": Decimal("7500.00"),
            "area": Decimal("80.00"),
            "date_posted": date(2024, 1, 10),
        },
        {
            "listing_id": 4,
            "price_total_zl": Decimal("500000.00"),
            "price_sqm_zl": Decimal("7142.86"),
            "price_per_sqm_detailed": Decimal("7142.86"),
            "area": Decimal("70.00"),
            "date_posted": date(2024, 3, 5),
        },
    ]


def test_sort_by_price_ascending(mock_offers):
    """Test sorting offers by total price in ascending order."""
    sorter = OfferSorter()
    sorted_offers = sorter.sort(mock_offers, sort_by="price", order="asc")

    assert len(sorted_offers) == 4
    assert sorted_offers[0]["listing_id"] == 2  # 300000 - lowest
    assert sorted_offers[1]["listing_id"] == 1  # 450000
    assert sorted_offers[2]["listing_id"] == 4  # 500000
    assert sorted_offers[3]["listing_id"] == 3  # 600000 - highest


def test_sort_by_price_descending(mock_offers):
    """Test sorting offers by total price in descending order."""
    sorter = OfferSorter()
    sorted_offers = sorter.sort(mock_offers, sort_by="price", order="desc")

    assert len(sorted_offers) == 4
    assert sorted_offers[0]["listing_id"] == 3  # 600000 - highest
    assert sorted_offers[1]["listing_id"] == 4  # 500000
    assert sorted_offers[2]["listing_id"] == 1  # 450000
    assert sorted_offers[3]["listing_id"] == 2  # 300000 - lowest


def test_sort_by_price_per_sqm_ascending(mock_offers):
    """Test sorting offers by price per square meter in ascending order."""
    sorter = OfferSorter()
    sorted_offers = sorter.sort(mock_offers, sort_by="price_per_sqm", order="asc")

    assert len(sorted_offers) == 4
    assert sorted_offers[0]["listing_id"] == 2  # 6666.67 - lowest
    assert sorted_offers[1]["listing_id"] == 4  # 7142.86
    assert sorted_offers[2]["listing_id"] == 3  # 7500.00
    assert sorted_offers[3]["listing_id"] == 1  # 9000.00 - highest


def test_sort_by_price_per_sqm_descending(mock_offers):
    """Test sorting offers by price per square meter in descending order."""
    sorter = OfferSorter()
    sorted_offers = sorter.sort(mock_offers, sort_by="price_per_sqm", order="desc")

    assert len(sorted_offers) == 4
    assert sorted_offers[0]["listing_id"] == 1  # 9000.00 - highest
    assert sorted_offers[1]["listing_id"] == 3  # 7500.00
    assert sorted_offers[2]["listing_id"] == 4  # 7142.86
    assert sorted_offers[3]["listing_id"] == 2  # 6666.67 - lowest


def test_sort_by_date_posted_newest(mock_offers):
    """Test sorting offers by date posted (newest first)."""
    sorter = OfferSorter()
    sorted_offers = sorter.sort(mock_offers, sort_by="date_posted", order="desc")

    assert len(sorted_offers) == 4
    assert sorted_offers[0]["listing_id"] == 4  # 2024-03-05 - newest
    assert sorted_offers[1]["listing_id"] == 2  # 2024-02-20
    assert sorted_offers[2]["listing_id"] == 1  # 2024-01-15
    assert sorted_offers[3]["listing_id"] == 3  # 2024-01-10 - oldest


def test_sort_by_area_ascending(mock_offers):
    """Test sorting offers by area in ascending order."""
    sorter = OfferSorter()
    sorted_offers = sorter.sort(mock_offers, sort_by="area", order="asc")

    assert len(sorted_offers) == 4
    assert sorted_offers[0]["listing_id"] == 2  # 45.00 - smallest
    assert sorted_offers[1]["listing_id"] == 1  # 50.00
    assert sorted_offers[2]["listing_id"] == 4  # 70.00
    assert sorted_offers[3]["listing_id"] == 3  # 80.00 - largest


def test_sort_by_area_descending(mock_offers):
    """Test sorting offers by area in descending order."""
    sorter = OfferSorter()
    sorted_offers = sorter.sort(mock_offers, sort_by="area", order="desc")

    assert len(sorted_offers) == 4
    assert sorted_offers[0]["listing_id"] == 3  # 80.00 - largest
    assert sorted_offers[1]["listing_id"] == 4  # 70.00
    assert sorted_offers[2]["listing_id"] == 1  # 50.00
    assert sorted_offers[3]["listing_id"] == 2  # 45.00 - smallest


def test_sort_empty_list():
    """Test sorting an empty list of offers."""
    sorter = OfferSorter()
    sorted_offers = sorter.sort([], sort_by="price", order="asc")

    assert len(sorted_offers) == 0
    assert sorted_offers == []


def test_sort_single_offer(mock_offers):
    """Test sorting a list with a single offer."""
    sorter = OfferSorter()
    single_offer = [mock_offers[0]]
    sorted_offers = sorter.sort(single_offer, sort_by="price", order="asc")

    assert len(sorted_offers) == 1
    assert sorted_offers[0]["listing_id"] == 1


def test_sort_with_none_values():
    """Test sorting offers that contain None values (edge case)."""
    offers_with_none = [
        {
            "listing_id": 1,
            "price_total_zl": Decimal("450000.00"),
            "price_sqm_zl": Decimal("9000.00"),
            "price_per_sqm_detailed": Decimal("9000.00"),
            "area": Decimal("50.00"),
            "date_posted": date(2024, 1, 15),
        },
        {
            "listing_id": 2,
            "price_total_zl": None,  # Missing price
            "price_sqm_zl": None,
            "price_per_sqm_detailed": None,
            "area": Decimal("45.00"),
            "date_posted": date(2024, 2, 20),
        },
        {
            "listing_id": 3,
            "price_total_zl": Decimal("300000.00"),
            "price_sqm_zl": Decimal("6666.67"),
            "price_per_sqm_detailed": Decimal("6666.67"),
            "area": None,  # Missing area
            "date_posted": date(2024, 1, 10),
        },
    ]

    sorter = OfferSorter()
    # Offers with None values should be handled gracefully
    # (placed at the end when sorting ascending, or at the beginning when descending)
    sorted_offers = sorter.sort(offers_with_none, sort_by="price", order="asc")

    assert len(sorted_offers) == 3
    # Offers with valid prices should come first
    assert sorted_offers[0]["listing_id"] == 3  # 300000
    assert sorted_offers[1]["listing_id"] == 1  # 450000
    # Offer with None price should be last
    assert sorted_offers[2]["listing_id"] == 2  # None


def test_sort_preserves_original_list(mock_offers):
    """Test that sorting does not modify the original list."""
    sorter = OfferSorter()
    original_list = mock_offers.copy()
    sorted_offers = sorter.sort(mock_offers, sort_by="price", order="asc")

    # Original list should remain unchanged
    assert mock_offers == original_list
    # Sorted list should be different
    assert sorted_offers != original_list
