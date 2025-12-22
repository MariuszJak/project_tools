from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class LocationDetailResponse(BaseModel):
    """Response schema for location details"""
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
    
    location_id: int = Field(..., description="Unique identifier for the location")
    city: Optional[str] = Field(None, description="City name")
    locality: Optional[str] = Field(None, description="Locality name")
    city_district: Optional[str] = Field(None, description="City district name")
    street: Optional[str] = Field(None, description="Street name")
    full_address: Optional[str] = Field(None, description="Full address string")
    latitude: Optional[Decimal] = Field(None, description="Latitude coordinate")
    longitude: Optional[Decimal] = Field(None, description="Longitude coordinate")


class LocationListResponse(BaseModel):
    """Response schema for list of locations"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "locations": [
                    {
                        "location_id": 1,
                        "city": "Warszawa",
                        "locality": "Śródmieście",
                        "city_district": "Centrum",
                        "street": "ul. Nowy Świat",
                        "full_address": "ul. Nowy Świat 1, 00-001 Warszawa",
                        "latitude": 52.229676,
                        "longitude": 21.012229,
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 100,
            }
        }
    )
    
    locations: List[LocationDetailResponse] = Field(..., description="List of locations")
    total: int = Field(..., description="Total number of locations available")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")

