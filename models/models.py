from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    pass


class Location(SQLModel, table=True):
    """Location model for storing address and geographic information"""

    __tablename__ = "location"

    location_id: int | None = Field(default=None, primary_key=True)
    city: str | None = Field(default=None, max_length=255)
    locality: str | None = Field(default=None, max_length=255)
    city_district: str | None = Field(default=None, max_length=255)
    street: str | None = Field(default=None, max_length=255)
    full_address: str | None = Field(default=None, max_length=500)
    latitude: Decimal | None = Field(default=None)
    longitude: Decimal | None = Field(default=None)

    # Relationship
    listings: list["Listing"] = Relationship(back_populates="location")


class Building(SQLModel, table=True):
    """Building model for storing building-related information"""

    __tablename__ = "building"

    building_id: int | None = Field(default=None, primary_key=True)
    year_built: int | None = Field(default=None)
    building_type: str | None = Field(default=None, max_length=100)
    floor: int | None = Field(default=None)

    # Relationship
    listings: list["Listing"] = Relationship(back_populates="building")


class Owner(SQLModel, table=True):
    """Owner model for storing owner contact information"""

    __tablename__ = "owner"

    owner_id: int | None = Field(default=None, primary_key=True)
    owner_type: str | None = Field(default=None, max_length=50)
    contact_name: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=50)
    contact_email: str | None = Field(default=None, max_length=255)

    # Relationship
    listings: list["Listing"] = Relationship(back_populates="owner")


class Features(SQLModel, table=True):
    """Features model for storing property features"""

    __tablename__ = "features"

    features_id: int | None = Field(default=None, primary_key=True)
    has_basement: bool | None = Field(default=None)
    has_parking: bool | None = Field(default=None)
    kitchen_type: str | None = Field(default=None, max_length=100)
    window_type: str | None = Field(default=None, max_length=100)
    ownership_type: str | None = Field(default=None, max_length=100)
    equipment: str | None = Field(default=None)

    # Relationship
    listings: list["Listing"] = Relationship(back_populates="features")


class Listing(SQLModel, table=True):
    """Listing model for storing property listing information"""

    __tablename__ = "listing"

    listing_id: int | None = Field(default=None, primary_key=True)
    location_id: int = Field(foreign_key="location.location_id")
    building_id: int = Field(foreign_key="building.building_id")
    owner_id: int = Field(foreign_key="owner.owner_id")
    features_id: int = Field(foreign_key="features.features_id")
    rooms: int | None = Field(default=None)
    area: Decimal | None = Field(default=None)
    price_total_zl: Decimal | None = Field(default=None)
    price_sqm_zl: Decimal | None = Field(default=None)
    price_per_sqm_detailed: Decimal | None = Field(default=None)
    date_posted: date | None = Field(default=None)
    photo_count: int | None = Field(default=None)
    url: str | None = Field(default=None)
    image_url: str | None = Field(default=None)
    description_text: str | None = Field(default=None)

    # Relationships
    location: Location = Relationship(back_populates="listings")
    building: Building = Relationship(back_populates="listings")
    owner: Owner = Relationship(back_populates="listings")
    features: Features = Relationship(back_populates="listings")


class SavedFilter(SQLModel, table=True):
    """Saved filter model for storing user search filters"""

    __tablename__ = "saved_filters"

    filter_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    price_min: Decimal | None = Field(default=None)
    price_max: Decimal | None = Field(default=None)
    price_sqm_min: Decimal | None = Field(default=None)
    price_sqm_max: Decimal | None = Field(default=None)
    rooms: str | None = Field(default=None)  # JSON array stored as text
    city: str | None = Field(default=None, max_length=255)
    city_district: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(
        sa_column=Column(DateTime, server_default=func.now(), nullable=False)
    )
