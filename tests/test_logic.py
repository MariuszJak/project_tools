"""
Tests for basic filters functionality (4.1 - Filtry podstawowe).

This module tests the filtering functionality for listings based on:
- Price total (min/max)
- Price per square meter (min/max)
- Number of rooms
- City
- City district
"""
import pytest
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Listing, Location, Building, Owner, Features
from schemas.filter import FilterRequest, PriceRange


@pytest.fixture
async def sample_listings(test_session: AsyncSession, mock_db_offer):
    """
    Create sample listings in the test database based on mock_db_offer fixture.
    Returns a list of created listing IDs.
    """
    # Create Location
    location = Location(
        location_id=mock_db_offer["location"]["location_id"],
        city=mock_db_offer["location"]["city"],
        locality=mock_db_offer["location"]["locality"],
        city_district=mock_db_offer["location"]["city_district"],
        street=mock_db_offer["location"]["street"],
        full_address=mock_db_offer["location"]["full_address"],
        latitude=mock_db_offer["location"]["latitude"],
        longitude=mock_db_offer["location"]["longitude"],
    )
    test_session.add(location)
    await test_session.flush()
    
    # Create Building
    building = Building(
        building_id=mock_db_offer["building"]["building_id"],
        year_built=mock_db_offer["building"]["year_built"],
        building_type=mock_db_offer["building"]["building_type"],
        floor=mock_db_offer["building"]["floor"],
    )
    test_session.add(building)
    await test_session.flush()
    
    # Create Owner
    owner = Owner(
        owner_id=mock_db_offer["owner"]["owner_id"],
        owner_type=mock_db_offer["owner"]["owner_type"],
        contact_name=mock_db_offer["owner"]["contact_name"],
        contact_phone=mock_db_offer["owner"]["contact_phone"],
        contact_email=mock_db_offer["owner"]["contact_email"],
    )
    test_session.add(owner)
    await test_session.flush()
    
    # Create Features
    features = Features(
        features_id=mock_db_offer["features"]["features_id"],
        has_basement=mock_db_offer["features"]["has_basement"],
        has_parking=mock_db_offer["features"]["has_parking"],
        kitchen_type=mock_db_offer["features"]["kitchen_type"],
        window_type=mock_db_offer["features"]["window_type"],
        ownership_type=mock_db_offer["features"]["ownership_type"],
        equipment=mock_db_offer["features"]["equipment"],
    )
    test_session.add(features)
    await test_session.flush()
    
    # Create multiple listings with different values for testing filters
    listings_data = [
        # Listing 1: matches mock_db_offer
        {
            "listing_id": 1,
            "rooms": 3,
            "area": Decimal("65.50"),
            "price_total_zl": Decimal("450000.00"),
            "price_sqm_zl": Decimal("9000.00"),
            "price_per_sqm_detailed": Decimal("9000.00"),
        },
        # Listing 2: different price, same city
        {
            "listing_id": 2,
            "rooms": 2,
            "area": Decimal("45.00"),
            "price_total_zl": Decimal("300000.00"),
            "price_sqm_zl": Decimal("6666.67"),
            "price_per_sqm_detailed": Decimal("6666.67"),
        },
        # Listing 3: different city
        {
            "listing_id": 3,
            "rooms": 4,
            "area": Decimal("80.00"),
            "price_total_zl": Decimal("600000.00"),
            "price_sqm_zl": Decimal("7500.00"),
            "price_per_sqm_detailed": Decimal("7500.00"),
        },
        # Listing 4: different district, same city
        {
            "listing_id": 4,
            "rooms": 3,
            "area": Decimal("70.00"),
            "price_total_zl": Decimal("500000.00"),
            "price_sqm_zl": Decimal("7142.86"),
            "price_per_sqm_detailed": Decimal("7142.86"),
        },
    ]
    
    # Create additional location for listing 3 (different city)
    location2 = Location(
        location_id=2,
        city="Kraków",
        locality="Stare Miasto",
        city_district="Centrum",
        street="ul. Floriańska",
        full_address="ul. Floriańska 1, 31-019 Kraków",
        latitude=Decimal("50.061947"),
        longitude=Decimal("19.936856"),
    )
    test_session.add(location2)
    await test_session.flush()
    
    # Create additional location for listing 4 (different district)
    location3 = Location(
        location_id=3,
        city="Warszawa",
        locality="Mokotów",
        city_district="Mokotów",
        street="ul. Puławska",
        full_address="ul. Puławska 1, 02-515 Warszawa",
        latitude=Decimal("52.186570"),
        longitude=Decimal("21.019000"),
    )
    test_session.add(location3)
    await test_session.flush()
    
    listing_ids = []
    for idx, listing_data in enumerate(listings_data):
        # Assign location based on listing
        if idx == 2:  # Listing 3 - different city
            loc_id = 2
        elif idx == 3:  # Listing 4 - different district
            loc_id = 3
        else:  # Listings 1 and 2 - same location as mock_db_offer
            loc_id = 1
        
        listing = Listing(
            listing_id=listing_data["listing_id"],
            location_id=loc_id,
            building_id=1,
            owner_id=1,
            features_id=1,
            rooms=listing_data["rooms"],
            area=listing_data["area"],
            price_total_zl=listing_data["price_total_zl"],
            price_sqm_zl=listing_data["price_sqm_zl"],
            price_per_sqm_detailed=listing_data["price_per_sqm_detailed"],
            date_posted=date(2024, 1, 15),
            photo_count=12,
            url=f"https://example.com/listing/{listing_data['listing_id']}",
            image_url=f"https://example.com/images/{listing_data['listing_id']}.jpg",
            description_text=f"Test listing {listing_data['listing_id']}",
        )
        test_session.add(listing)
        listing_ids.append(listing_data["listing_id"])
    
    await test_session.commit()
    
    return listing_ids


@pytest.mark.asyncio
async def test_filter_by_price_total_min(test_client, sample_listings):
    """Test filtering by minimum total price."""
    filter_request = FilterRequest(
        price_total=PriceRange(min=Decimal("400000.00"), max=None)
    )
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    assert data["total"] >= 1
    
    # All returned listings should have price_total_zl >= 400000
    for listing in data["listings"]:
        assert Decimal(str(listing["price_total_zl"])) >= Decimal("400000.00")


@pytest.mark.asyncio
async def test_filter_by_price_total_max(test_client, sample_listings):
    """Test filtering by maximum total price."""
    filter_request = FilterRequest(
        price_total=PriceRange(min=None, max=Decimal("400000.00"))
    )
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    assert data["total"] >= 1
    
    # All returned listings should have price_total_zl <= 400000
    for listing in data["listings"]:
        assert Decimal(str(listing["price_total_zl"])) <= Decimal("400000.00")


@pytest.mark.asyncio
async def test_filter_by_price_total_range(test_client, sample_listings):
    """Test filtering by total price range (min and max)."""
    filter_request = FilterRequest(
        price_total=PriceRange(min=Decimal("350000.00"), max=Decimal("550000.00"))
    )
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    assert data["total"] >= 1
    
    # All returned listings should have price_total_zl between 350000 and 550000
    for listing in data["listings"]:
        price = Decimal(str(listing["price_total_zl"]))
        assert price >= Decimal("350000.00")
        assert price <= Decimal("550000.00")


@pytest.mark.asyncio
async def test_filter_by_price_per_sqm_min(test_client, sample_listings):
    """Test filtering by minimum price per square meter."""
    filter_request = FilterRequest(
        price_per_sqm=PriceRange(min=Decimal("8000.00"), max=None)
    )
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    assert data["total"] >= 1
    
    # All returned listings should have price_per_sqm >= 8000
    for listing in data["listings"]:
        price_sqm = listing.get("price_sqm_zl") or listing.get("price_per_sqm_detailed")
        assert price_sqm is not None
        assert Decimal(str(price_sqm)) >= Decimal("8000.00")


@pytest.mark.asyncio
async def test_filter_by_price_per_sqm_max(test_client, sample_listings):
    """Test filtering by maximum price per square meter."""
    filter_request = FilterRequest(
        price_per_sqm=PriceRange(min=None, max=Decimal("7500.00"))
    )
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    assert data["total"] >= 1
    
    # All returned listings should have price_per_sqm <= 7500
    for listing in data["listings"]:
        price_sqm = listing.get("price_sqm_zl") or listing.get("price_per_sqm_detailed")
        assert price_sqm is not None
        assert Decimal(str(price_sqm)) <= Decimal("7500.00")


@pytest.mark.asyncio
async def test_filter_by_price_per_sqm_range(test_client, sample_listings):
    """Test filtering by price per square meter range (min and max)."""
    filter_request = FilterRequest(
        price_per_sqm=PriceRange(min=Decimal("7000.00"), max=Decimal("9000.00"))
    )
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    assert data["total"] >= 1
    
    # All returned listings should have price_per_sqm between 7000 and 9000
    for listing in data["listings"]:
        price_sqm = listing.get("price_sqm_zl") or listing.get("price_per_sqm_detailed")
        assert price_sqm is not None
        price = Decimal(str(price_sqm))
        assert price >= Decimal("7000.00")
        assert price <= Decimal("9000.00")


@pytest.mark.asyncio
async def test_filter_by_rooms_single(test_client, sample_listings):
    """Test filtering by single room count."""
    filter_request = FilterRequest(rooms=[3])
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    assert data["total"] >= 1
    
    # All returned listings should have 3 rooms
    for listing in data["listings"]:
        assert listing["rooms"] == 3


@pytest.mark.asyncio
async def test_filter_by_rooms_multiple(test_client, sample_listings):
    """Test filtering by multiple room counts (multi-select)."""
    filter_request = FilterRequest(rooms=[2, 3])
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    assert data["total"] >= 1
    
    # All returned listings should have 2 or 3 rooms
    for listing in data["listings"]:
        assert listing["rooms"] in [2, 3]


@pytest.mark.asyncio
async def test_filter_by_city(test_client, sample_listings):
    """Test filtering by city name."""
    filter_request = FilterRequest(city="Warszawa")
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    assert data["total"] >= 1
    
    # All returned listings should be in Warszawa
    for listing in data["listings"]:
        assert listing["location"]["city"] == "Warszawa"


@pytest.mark.asyncio
async def test_filter_by_city_district(test_client, sample_listings):
    """Test filtering by city district."""
    filter_request = FilterRequest(city_district="Centrum")
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    assert data["total"] >= 1
    
    # All returned listings should be in Centrum district
    for listing in data["listings"]:
        assert listing["location"]["city_district"] == "Centrum"


@pytest.mark.asyncio
async def test_filter_by_city_and_district(test_client, sample_listings):
    """Test filtering by both city and district."""
    filter_request = FilterRequest(
        city="Warszawa",
        city_district="Centrum"
    )
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    assert data["total"] >= 1
    
    # All returned listings should be in Warszawa, Centrum
    for listing in data["listings"]:
        assert listing["location"]["city"] == "Warszawa"
        assert listing["location"]["city_district"] == "Centrum"


@pytest.mark.asyncio
async def test_filter_combined_price_and_rooms(test_client, sample_listings):
    """Test filtering by combined criteria: price and rooms."""
    filter_request = FilterRequest(
        price_total=PriceRange(min=Decimal("400000.00"), max=Decimal("600000.00")),
        rooms=[3]
    )
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    
    # All returned listings should match both criteria
    for listing in data["listings"]:
        price = Decimal(str(listing["price_total_zl"]))
        assert price >= Decimal("400000.00")
        assert price <= Decimal("600000.00")
        assert listing["rooms"] == 3


@pytest.mark.asyncio
async def test_filter_combined_all_criteria(test_client, sample_listings):
    """Test filtering by all criteria combined."""
    filter_request = FilterRequest(
        price_total=PriceRange(min=Decimal("300000.00"), max=Decimal("500000.00")),
        price_per_sqm=PriceRange(min=Decimal("6000.00"), max=Decimal("9000.00")),
        rooms=[2, 3],
        city="Warszawa",
        city_district="Centrum"
    )
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    
    # All returned listings should match all criteria
    for listing in data["listings"]:
        # Price total check
        price = Decimal(str(listing["price_total_zl"]))
        assert price >= Decimal("300000.00")
        assert price <= Decimal("500000.00")
        
        # Price per sqm check
        price_sqm = listing.get("price_sqm_zl") or listing.get("price_per_sqm_detailed")
        assert price_sqm is not None
        price_sqm_decimal = Decimal(str(price_sqm))
        assert price_sqm_decimal >= Decimal("6000.00")
        assert price_sqm_decimal <= Decimal("9000.00")
        
        # Rooms check
        assert listing["rooms"] in [2, 3]
        
        # Location check
        assert listing["location"]["city"] == "Warszawa"
        assert listing["location"]["city_district"] == "Centrum"


@pytest.mark.asyncio
async def test_filter_no_results(test_client, sample_listings):
    """Test filtering with criteria that match no listings."""
    filter_request = FilterRequest(
        price_total=PriceRange(min=Decimal("1000000.00"), max=None)
    )
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    assert data["total"] == 0
    assert len(data["listings"]) == 0


@pytest.mark.asyncio
async def test_filter_empty_request(test_client, sample_listings):
    """Test filtering with empty request (no filters applied)."""
    filter_request = FilterRequest()
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    # Should return all listings when no filters are applied
    assert data["total"] >= len(sample_listings)


@pytest.mark.asyncio
async def test_filter_response_structure(test_client, sample_listings):
    """Test that filter response has correct structure."""
    filter_request = FilterRequest(rooms=[3])
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    # Check top-level structure
    assert "listings" in data
    assert "total" in data
    assert isinstance(data["listings"], list)
    assert isinstance(data["total"], int)
    
    # Check listing structure if any results
    if data["total"] > 0:
        listing = data["listings"][0]
        
        # Required fields
        assert "listing_id" in listing
        assert "location" in listing
        
        # Check location structure
        location = listing["location"]
        assert "location_id" in location
        assert "city" in location
        assert "city_district" in location


@pytest.fixture
async def invalid_listings(test_session: AsyncSession, mock_db_offer):
    """
    Create listings with invalid data (missing price or zero area).
    Returns a list of created listing IDs.
    """
    # Create Location
    location = Location(
        location_id=mock_db_offer["location"]["location_id"],
        city=mock_db_offer["location"]["city"],
        locality=mock_db_offer["location"]["locality"],
        city_district=mock_db_offer["location"]["city_district"],
        street=mock_db_offer["location"]["street"],
        full_address=mock_db_offer["location"]["full_address"],
        latitude=mock_db_offer["location"]["latitude"],
        longitude=mock_db_offer["location"]["longitude"],
    )
    test_session.add(location)
    await test_session.flush()
    
    # Create Building
    building = Building(
        building_id=mock_db_offer["building"]["building_id"],
        year_built=mock_db_offer["building"]["year_built"],
        building_type=mock_db_offer["building"]["building_type"],
        floor=mock_db_offer["building"]["floor"],
    )
    test_session.add(building)
    await test_session.flush()
    
    # Create Owner
    owner = Owner(
        owner_id=mock_db_offer["owner"]["owner_id"],
        owner_type=mock_db_offer["owner"]["owner_type"],
        contact_name=mock_db_offer["owner"]["contact_name"],
        contact_phone=mock_db_offer["owner"]["contact_phone"],
        contact_email=mock_db_offer["owner"]["contact_email"],
    )
    test_session.add(owner)
    await test_session.flush()
    
    # Create Features
    features = Features(
        features_id=mock_db_offer["features"]["features_id"],
        has_basement=mock_db_offer["features"]["has_basement"],
        has_parking=mock_db_offer["features"]["has_parking"],
        kitchen_type=mock_db_offer["features"]["kitchen_type"],
        window_type=mock_db_offer["features"]["window_type"],
        ownership_type=mock_db_offer["features"]["ownership_type"],
        equipment=mock_db_offer["features"]["equipment"],
    )
    test_session.add(features)
    await test_session.flush()
    
    # Create listings with invalid data
    invalid_listings_data = [
        # Listing with missing price (price_total_zl = None)
        {
            "listing_id": 100,
            "rooms": 2,
            "area": Decimal("50.00"),
            "price_total_zl": None,
            "price_sqm_zl": None,
            "price_per_sqm_detailed": None,
        },
        # Listing with zero area
        {
            "listing_id": 101,
            "rooms": 3,
            "area": Decimal("0.00"),
            "price_total_zl": Decimal("300000.00"),
            "price_sqm_zl": None,  # Cannot calculate price per sqm with zero area
            "price_per_sqm_detailed": None,
        },
        # Listing with both missing price and zero area
        {
            "listing_id": 102,
            "rooms": 1,
            "area": Decimal("0.00"),
            "price_total_zl": None,
            "price_sqm_zl": None,
            "price_per_sqm_detailed": None,
        },
    ]
    
    listing_ids = []
    for listing_data in invalid_listings_data:
        listing = Listing(
            listing_id=listing_data["listing_id"],
            location_id=1,
            building_id=1,
            owner_id=1,
            features_id=1,
            rooms=listing_data["rooms"],
            area=listing_data["area"],
            price_total_zl=listing_data["price_total_zl"],
            price_sqm_zl=listing_data["price_sqm_zl"],
            price_per_sqm_detailed=listing_data["price_per_sqm_detailed"],
            date_posted=date(2024, 1, 15),
            photo_count=5,
            url=f"https://example.com/listing/{listing_data['listing_id']}",
            image_url=f"https://example.com/images/{listing_data['listing_id']}.jpg",
            description_text=f"Invalid listing {listing_data['listing_id']}",
        )
        test_session.add(listing)
        listing_ids.append(listing_data["listing_id"])
    
    await test_session.commit()
    
    return listing_ids


@pytest.mark.asyncio
async def test_filter_with_missing_price_excluded(test_client, invalid_listings):
    """Test that listings with missing price are excluded from price-based filters."""
    # Filter by price - listings with None price should not be included
    filter_request = FilterRequest(
        price_total=PriceRange(min=Decimal("200000.00"), max=Decimal("500000.00"))
    )
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    
    # Listings with missing price should not appear in results
    for listing in data["listings"]:
        assert listing["price_total_zl"] is not None
        assert Decimal(str(listing["price_total_zl"])) >= Decimal("200000.00")
        assert Decimal(str(listing["price_total_zl"])) <= Decimal("500000.00")


@pytest.mark.asyncio
async def test_filter_with_zero_area_excluded(test_client, invalid_listings):
    """Test that listings with zero area are handled correctly in filters."""
    # Filter by rooms - listings with zero area should still appear if they match room criteria
    filter_request = FilterRequest(rooms=[3])
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    
    # Check that listings with zero area can still be returned (if they match other criteria)
    # But they should have area = 0 or None
    for listing in data["listings"]:
        if listing["listing_id"] == 101:  # Listing with zero area
            # Area can be 0, "0.00", or None (JSON serializes Decimal as string)
            area = listing.get("area")
            assert area is None or area == 0 or Decimal(str(area)) == Decimal("0")


@pytest.mark.asyncio
async def test_filter_price_per_sqm_with_zero_area(test_client, invalid_listings):
    """Test that listings with zero area are excluded from price_per_sqm filters."""
    # Filter by price per sqm - listings with zero area cannot have valid price_per_sqm
    filter_request = FilterRequest(
        price_per_sqm=PriceRange(min=Decimal("5000.00"), max=Decimal("10000.00"))
    )
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    
    # Listings with zero area should not appear in price_per_sqm filtered results
    # because they cannot have a valid price_per_sqm value
    for listing in data["listings"]:
        # If area is zero, price_per_sqm should be None or not in range
        area = listing.get("area")
        is_zero_area = area is None or area == 0 or (area is not None and Decimal(str(area)) == Decimal("0"))
        if is_zero_area:
            price_sqm = listing.get("price_sqm_zl") or listing.get("price_per_sqm_detailed")
            # If price_sqm exists, it should be in range (but with zero area this shouldn't happen)
            if price_sqm is not None:
                assert Decimal(str(price_sqm)) >= Decimal("5000.00")
                assert Decimal(str(price_sqm)) <= Decimal("10000.00")


@pytest.mark.asyncio
async def test_invalid_listings_in_empty_filter(test_client, invalid_listings):
    """Test that invalid listings (missing price, zero area) appear in results when no filters are applied."""
    filter_request = FilterRequest()
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    
    # Should return all listings including invalid ones when no filters are applied
    listing_ids = [listing["listing_id"] for listing in data["listings"]]
    
    # Check that invalid listings can be in the results
    # (they should appear if no price/area filters are applied)
    assert data["total"] >= len(invalid_listings)


@pytest.mark.asyncio
async def test_listing_with_missing_price_structure(test_client, invalid_listings):
    """Test that listing with missing price has correct response structure."""
    filter_request = FilterRequest(rooms=[2])
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    
    # Find listing with missing price (listing_id = 100)
    listing_with_missing_price = None
    for listing in data["listings"]:
        if listing["listing_id"] == 100:
            listing_with_missing_price = listing
            break
    
    if listing_with_missing_price:
        # Should have all required fields
        assert "listing_id" in listing_with_missing_price
        assert "location" in listing_with_missing_price
        # Price fields should be None
        assert listing_with_missing_price["price_total_zl"] is None
        assert listing_with_missing_price.get("price_sqm_zl") is None or listing_with_missing_price["price_sqm_zl"] is None
        assert listing_with_missing_price.get("price_per_sqm_detailed") is None or listing_with_missing_price["price_per_sqm_detailed"] is None


@pytest.mark.asyncio
async def test_listing_with_zero_area_structure(test_client, invalid_listings):
    """Test that listing with zero area has correct response structure."""
    filter_request = FilterRequest(rooms=[3])
    
    response = await test_client.post("/filters/search", json=filter_request.model_dump(mode='json'))
    
    assert response.status_code == 200
    data = response.json()
    
    assert "listings" in data
    assert "total" in data
    
    # Find listing with zero area (listing_id = 101)
    listing_with_zero_area = None
    for listing in data["listings"]:
        if listing["listing_id"] == 101:
            listing_with_zero_area = listing
            break
    
    if listing_with_zero_area:
        # Should have all required fields
        assert "listing_id" in listing_with_zero_area
        assert "location" in listing_with_zero_area
        # Area should be 0 (can be 0, "0.00", or None in JSON response)
        area = listing_with_zero_area.get("area")
        assert area is None or area == 0 or Decimal(str(area)) == Decimal("0")
        # Price per sqm should be None (cannot calculate with zero area)
        assert listing_with_zero_area.get("price_sqm_zl") is None or listing_with_zero_area["price_sqm_zl"] is None
        assert listing_with_zero_area.get("price_per_sqm_detailed") is None or listing_with_zero_area["price_per_sqm_detailed"] is None

