from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from models.database import get_db
from models.models import Location
from schemas.location import LocationDetailResponse, LocationListResponse
from dependencies import get_pagination_params

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get(
    "/",
    response_model=LocationListResponse,
    summary="Get list of locations",
    description="Retrieve a paginated list of all locations in the system",
)
async def get_locations(
    db: Annotated[AsyncSession, Depends(get_db)],
    pagination: Annotated[tuple[int, int], Depends(get_pagination_params)],
) -> LocationListResponse:
    """
    Endpoint to retrieve a paginated list of all locations.
    
    Args:
        db: Database session dependency
        pagination: Pagination parameters (skip, limit)
    
    Returns:
        LocationListResponse: Paginated list of locations with metadata
    """
    skip, limit = pagination
    
    # Get total count of locations
    count_result = await db.execute(select(func.count(Location.location_id)))
    total = count_result.scalar_one()
    
    # Query locations with pagination
    result = await db.execute(
        select(Location)
        .offset(skip)
        .limit(limit)
        .order_by(Location.location_id)
    )
    locations = result.scalars().all()
    
    # Convert to response models
    location_list = [
        LocationDetailResponse(
            location_id=location.location_id,
            city=location.city,
            locality=location.locality,
            city_district=location.city_district,
            street=location.street,
            full_address=location.full_address,
            latitude=location.latitude,
            longitude=location.longitude,
        )
        for location in locations
    ]
    
    return LocationListResponse(
        locations=location_list,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{location_id}",
    response_model=LocationDetailResponse,
    summary="Get location details",
    description="Retrieve full information about a specific location by its ID",
)
async def get_location_details(
    location_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> LocationDetailResponse:
    """
    Endpoint to retrieve detailed information about a specific location.
    
    Args:
        location_id: Unique identifier of the location to retrieve
        db: Database session dependency
    
    Returns:
        LocationDetailResponse: Full location details including address and coordinates
    
    Raises:
        HTTPException: 404 if location not found
    """
    # Query the database for the location
    result = await db.execute(
        select(Location).where(Location.location_id == location_id)
    )
    location = result.scalar_one_or_none()
    
    # Return 404 if location not found
    if location is None:
        raise HTTPException(
            status_code=404,
            detail=f"Location with ID {location_id} not found"
        )
    
    # Return location details
    return LocationDetailResponse(
        location_id=location.location_id,
        city=location.city,
        locality=location.locality,
        city_district=location.city_district,
        street=location.street,
        full_address=location.full_address,
        latitude=location.latitude,
        longitude=location.longitude,
    )

