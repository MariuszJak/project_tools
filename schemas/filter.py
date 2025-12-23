from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PriceRange(BaseModel):
    """Schema for price range (min and max values)"""

    min: Decimal | None = Field(None, description="Minimum price value")
    max: Decimal | None = Field(None, description="Maximum price value")

    model_config = ConfigDict(json_schema_extra={"example": {"min": 200000.00, "max": 500000.00}})


class SaveFilterRequest(BaseModel):
    """Request schema for saving search filters"""

    name: str = Field(..., min_length=1, max_length=255, description="Name of the saved filter")
    price_total: PriceRange | None = Field(None, description="Range for total price (PLN)")
    price_per_sqm: PriceRange | None = Field(
        None, description="Range for price per square meter (PLN/m²)"
    )
    rooms: list[int] | None = Field(
        None, description="List of room counts to filter (multi-select)"
    )
    city: str | None = Field(None, max_length=255, description="City name for autocomplete")
    city_district: str | None = Field(
        None, max_length=255, description="City district name for autocomplete"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "My apartment search",
                "price_total": {"min": 300000.00, "max": 600000.00},
                "price_per_sqm": {"min": 8000.00, "max": 12000.00},
                "rooms": [2, 3],
                "city": "Warszawa",
                "city_district": "Śródmieście",
            }
        }
    )

    @field_validator("rooms")
    @classmethod
    def validate_rooms(cls, v: list[int] | None) -> list[int] | None:
        """Validate that room counts are positive integers"""
        if v is not None:
            for room in v:
                if room < 1:
                    raise ValueError("Room count must be at least 1")
        return v


class SavedFilterResponse(BaseModel):
    """Response schema for saved filter"""

    filter_id: int = Field(..., description="Unique identifier for the saved filter")
    name: str = Field(..., description="Name of the saved filter")
    price_min: Decimal | None = Field(None, description="Minimum total price")
    price_max: Decimal | None = Field(None, description="Maximum total price")
    price_sqm_min: Decimal | None = Field(None, description="Minimum price per square meter")
    price_sqm_max: Decimal | None = Field(None, description="Maximum price per square meter")
    rooms: list[int] | None = Field(None, description="List of room counts")
    city: str | None = Field(None, description="City name")
    city_district: str | None = Field(None, description="City district name")
    created_at: datetime = Field(..., description="Timestamp when filter was created")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filter_id": 1,
                "name": "My apartment search",
                "price_min": 300000.00,
                "price_max": 600000.00,
                "price_sqm_min": 8000.00,
                "price_sqm_max": 12000.00,
                "rooms": [2, 3],
                "city": "Warszawa",
                "city_district": "Śródmieście",
                "created_at": "2024-01-15T10:30:00",
            }
        }
    )


class SavedFilterListResponse(BaseModel):
    """Response schema for list of saved filters"""

    filters: list[SavedFilterResponse] = Field(..., description="List of saved filters")
    total: int = Field(..., description="Total number of saved filters")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filters": [
                    {
                        "filter_id": 1,
                        "name": "My apartment search",
                        "price_min": 300000.00,
                        "price_max": 600000.00,
                        "price_sqm_min": 8000.00,
                        "price_sqm_max": 12000.00,
                        "rooms": [2, 3],
                        "city": "Warszawa",
                        "city_district": "Śródmieście",
                        "created_at": "2024-01-15T10:30:00",
                    }
                ],
                "total": 1,
            }
        }
    )


class FilterRequest(BaseModel):
    """Request schema for filtering listings"""

    name: str | None = Field(
        None, max_length=255, description="Optional name for the filter (not used in filtering)"
    )
    price_total: PriceRange | None = Field(None, description="Range for total price (PLN)")
    price_per_sqm: PriceRange | None = Field(
        None, description="Range for price per square meter (PLN/m²)"
    )
    rooms: list[int] | None = Field(
        None, description="List of room counts to filter (multi-select)"
    )
    city: str | None = Field(None, max_length=255, description="City name for filtering")
    city_district: str | None = Field(
        None, max_length=255, description="City district name for filtering"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "My apartment search",
                "price_total": {"min": 300000.00, "max": 600000.00},
                "price_per_sqm": {"min": 8000.00, "max": 12000.00},
                "rooms": [2, 3],
                "city": "Warszawa",
                "city_district": "Śródmieście",
            }
        }
    )

    @field_validator("rooms")
    @classmethod
    def validate_rooms(cls, v: list[int] | None) -> list[int] | None:
        """Validate that room counts are positive integers"""
        if v is not None:
            for room in v:
                if room < 1:
                    raise ValueError("Room count must be at least 1")
        return v


class LocationInfo(BaseModel):
    """Location information included in listing response"""

    location_id: int = Field(..., description="Unique identifier for the location")
    city: str | None = Field(None, description="City name")
    locality: str | None = Field(None, description="Locality name")
    city_district: str | None = Field(None, description="City district name")
    street: str | None = Field(None, description="Street name")
    full_address: str | None = Field(None, description="Full address string")
    latitude: Decimal | None = Field(None, description="Latitude coordinate")
    longitude: Decimal | None = Field(None, description="Longitude coordinate")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "location_id": 1,
                "city": "Warszawa",
                "locality": "Śródmieście",
                "city_district": "Centrum",
                "street": "ul. Nowy Świat",
                "full_address": "ul. Nowy Świat 1, 00-001 Warszawa",
                "latitude": 52.229676,
                "longitude": 21.012229,
            }
        }
    )


class ListingWithLocationResponse(BaseModel):
    """Response schema for listing with location information"""

    listing_id: int = Field(..., description="Unique identifier for the listing")
    rooms: int | None = Field(None, description="Number of rooms")
    area: Decimal | None = Field(None, description="Area in square meters")
    price_total_zl: Decimal | None = Field(None, description="Total price in PLN")
    price_sqm_zl: Decimal | None = Field(None, description="Price per square meter in PLN")
    price_per_sqm_detailed: Decimal | None = Field(
        None, description="Detailed price per square meter in PLN"
    )
    date_posted: date | None = Field(None, description="Date when listing was posted")
    photo_count: int | None = Field(None, description="Number of photos")
    url: str | None = Field(None, description="URL to the listing")
    image_url: str | None = Field(None, description="URL to the main image")
    description_text: str | None = Field(None, description="Listing description text")
    location: LocationInfo = Field(..., description="Location information")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "listing_id": 1,
                "rooms": 3,
                "area": 65.50,
                "price_total_zl": 450000.00,
                "price_sqm_zl": 9000.00,
                "price_per_sqm_detailed": 9000.00,
                "date_posted": "2024-01-15",
                "photo_count": 12,
                "url": "https://example.com/listing/1",
                "image_url": "https://example.com/images/1.jpg",
                "description_text": "Beautiful apartment in city center",
                "location": {
                    "location_id": 1,
                    "city": "Warszawa",
                    "locality": "Śródmieście",
                    "city_district": "Centrum",
                    "street": "ul. Nowy Świat",
                    "full_address": "ul. Nowy Świat 1, 00-001 Warszawa",
                    "latitude": 52.229676,
                    "longitude": 21.012229,
                },
            }
        }
    )


class FilteredListingsResponse(BaseModel):
    """Response schema for filtered listings"""

    listings: list[ListingWithLocationResponse] = Field(
        ..., description="List of matching listings"
    )
    total: int = Field(..., description="Total number of matching listings")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "listings": [
                    {
                        "listing_id": 1,
                        "rooms": 3,
                        "area": 65.50,
                        "price_total_zl": 450000.00,
                        "price_sqm_zl": 9000.00,
                        "price_per_sqm_detailed": 9000.00,
                        "date_posted": "2024-01-15",
                        "photo_count": 12,
                        "url": "https://example.com/listing/1",
                        "image_url": "https://example.com/images/1.jpg",
                        "description_text": "Beautiful apartment in city center",
                        "location": {
                            "location_id": 1,
                            "city": "Warszawa",
                            "locality": "Śródmieście",
                            "city_district": "Centrum",
                            "street": "ul. Nowy Świat",
                            "full_address": "ul. Nowy Świat 1, 00-001 Warszawa",
                            "latitude": 52.229676,
                            "longitude": 21.012229,
                        },
                    }
                ],
                "total": 1,
            }
        }
    )
