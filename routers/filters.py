import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from dependencies import get_pagination_params
from models.database import get_db
from models.models import Listing, Location, SavedFilter
from schemas.filter import (
    FilteredListingsResponse,
    FilterRequest,
    ListingWithLocationResponse,
    LocationInfo,
    SavedFilterListResponse,
    SavedFilterResponse,
    SaveFilterRequest,
)

router = APIRouter(prefix="/filters", tags=["Filters"])


@router.post(
    "/",
    response_model=SavedFilterResponse,
    status_code=201,
    summary="Save search filters",
    description="Save a set of search filters for later use",
)
async def save_filter(
    filter_data: SaveFilterRequest, db: Annotated[AsyncSession, Depends(get_db)]
) -> SavedFilterResponse:
    """
    Endpoint to save search filters.

    Args:
        filter_data: Filter data including price ranges, rooms, and location
        db: Database session dependency

    Returns:
        SavedFilterResponse: Saved filter with generated ID and timestamp

    Raises:
        HTTPException: 400 if validation fails
    """
    # Convert rooms list to JSON string for storage
    rooms_json = None
    if filter_data.rooms is not None:
        rooms_json = json.dumps(filter_data.rooms)

    # Extract price ranges
    price_min = filter_data.price_total.min if filter_data.price_total else None
    price_max = filter_data.price_total.max if filter_data.price_total else None
    price_sqm_min = filter_data.price_per_sqm.min if filter_data.price_per_sqm else None
    price_sqm_max = filter_data.price_per_sqm.max if filter_data.price_per_sqm else None

    # Create new saved filter
    new_filter = SavedFilter(
        name=filter_data.name,
        price_min=price_min,
        price_max=price_max,
        price_sqm_min=price_sqm_min,
        price_sqm_max=price_sqm_max,
        rooms=rooms_json,
        city=filter_data.city,
        city_district=filter_data.city_district,
    )

    # Save to database
    db.add(new_filter)
    await db.commit()
    await db.refresh(new_filter)

    def parse_rooms_json(rooms_json: str | None) -> list[int] | None:
        """Parse rooms JSON string back to list."""
        if not rooms_json:
            return None
        try:
            return json.loads(rooms_json)
        except json.JSONDecodeError:
            return None

    # Use the new function
    rooms_list = parse_rooms_json(new_filter.rooms)

    # Return response
    return SavedFilterResponse(
        filter_id=new_filter.filter_id,
        name=new_filter.name,
        price_min=new_filter.price_min,
        price_max=new_filter.price_max,
        price_sqm_min=new_filter.price_sqm_min,
        price_sqm_max=new_filter.price_sqm_max,
        rooms=rooms_list,
        city=new_filter.city,
        city_district=new_filter.city_district,
        created_at=new_filter.created_at,
    )


@router.get(
    "/",
    response_model=SavedFilterListResponse,
    summary="Get list of saved filters",
    description="Retrieve a paginated list of all saved filters",
)
async def get_saved_filters(
    db: Annotated[AsyncSession, Depends(get_db)],
    pagination: Annotated[tuple[int, int], Depends(get_pagination_params)],
) -> SavedFilterListResponse:
    """
    Endpoint to retrieve a paginated list of all saved filters.

    Args:
        db: Database session dependency
        pagination: Pagination parameters (skip, limit)

    Returns:
        SavedFilterListResponse: Paginated list of saved filters with metadata
    """
    skip, limit = pagination

    # Get total count of filters
    count_result = await db.execute(select(func.count(SavedFilter.filter_id)))
    total = count_result.scalar_one()

    # Query filters with pagination
    result = await db.execute(
        select(SavedFilter).offset(skip).limit(limit).order_by(SavedFilter.created_at.desc())
    )
    filters = result.scalars().all()

    # Convert to response models
    filter_list = []
    for filter_item in filters:
        # Parse rooms JSON back to list
        rooms_list = None
        if filter_item.rooms:
            try:
                rooms_list = json.loads(filter_item.rooms)
            except json.JSONDecodeError:
                rooms_list = None

        filter_list.append(
            SavedFilterResponse(
                filter_id=filter_item.filter_id,
                name=filter_item.name,
                price_min=filter_item.price_min,
                price_max=filter_item.price_max,
                price_sqm_min=filter_item.price_sqm_min,
                price_sqm_max=filter_item.price_sqm_max,
                rooms=rooms_list,
                city=filter_item.city,
                city_district=filter_item.city_district,
                created_at=filter_item.created_at,
            )
        )

    return SavedFilterListResponse(
        filters=filter_list,
        total=total,
    )


@router.get(
    "/{filter_id}",
    response_model=SavedFilterResponse,
    summary="Get saved filter details",
    description="Retrieve full information about a specific saved filter by its ID",
)
async def get_saved_filter_details(
    filter_id: int, db: Annotated[AsyncSession, Depends(get_db)]
) -> SavedFilterResponse:
    """
    Endpoint to retrieve detailed information about a specific saved filter.

    Args:
        filter_id: Unique identifier of the filter to retrieve
        db: Database session dependency

    Returns:
        SavedFilterResponse: Full filter details

    Raises:
        HTTPException: 404 if filter not found
    """
    # Query the database for the filter
    result = await db.execute(select(SavedFilter).where(SavedFilter.filter_id == filter_id))
    filter_item = result.scalar_one_or_none()

    # Return 404 if filter not found
    if filter_item is None:
        raise HTTPException(status_code=404, detail=f"Filter with ID {filter_id} not found")

    # Parse rooms JSON back to list
    rooms_list = None
    if filter_item.rooms:
        try:
            rooms_list = json.loads(filter_item.rooms)
        except json.JSONDecodeError:
            rooms_list = None

    # Return filter details
    return SavedFilterResponse(
        filter_id=filter_item.filter_id,
        name=filter_item.name,
        price_min=filter_item.price_min,
        price_max=filter_item.price_max,
        price_sqm_min=filter_item.price_sqm_min,
        price_sqm_max=filter_item.price_sqm_max,
        rooms=rooms_list,
        city=filter_item.city,
        city_district=filter_item.city_district,
        created_at=filter_item.created_at,
    )


@router.post(
    "/search",
    response_model=FilteredListingsResponse,
    summary="Filter listings",
    description="Search and filter listings based on criteria (price, rooms, location, etc.)",
)
async def filter_listings(
    filter_data: FilterRequest, db: Annotated[AsyncSession, Depends(get_db)]
) -> FilteredListingsResponse:
    """
    Endpoint to filter listings based on various criteria.

    Args:
        filter_data: Filter criteria including price ranges, rooms, and location
        db: Database session dependency

    Returns:
        FilteredListingsResponse: List of matching listings with location information
    """
    # Build filter conditions
    conditions = []

    # Filter by price_total range
    if filter_data.price_total is not None:
        if filter_data.price_total.min is not None:
            conditions.append(Listing.price_total_zl >= filter_data.price_total.min)
        if filter_data.price_total.max is not None:
            conditions.append(Listing.price_total_zl <= filter_data.price_total.max)

    # Filter by price_per_sqm range (check both price_sqm_zl and price_per_sqm_detailed)
    if filter_data.price_per_sqm is not None:
        price_min = filter_data.price_per_sqm.min
        price_max = filter_data.price_per_sqm.max

        # Build conditions: match if either price_sqm_zl or price_per_sqm_detailed is within range
        price_sqm_match = None
        price_detailed_match = None

        if price_min is not None and price_max is not None:
            # Both min and max specified
            price_sqm_match = and_(
                Listing.price_sqm_zl.isnot(None),
                Listing.price_sqm_zl >= price_min,
                Listing.price_sqm_zl <= price_max,
            )
            price_detailed_match = and_(
                Listing.price_per_sqm_detailed.isnot(None),
                Listing.price_per_sqm_detailed >= price_min,
                Listing.price_per_sqm_detailed <= price_max,
            )
        elif price_min is not None:
            # Only min specified
            price_sqm_match = and_(
                Listing.price_sqm_zl.isnot(None), Listing.price_sqm_zl >= price_min
            )
            price_detailed_match = and_(
                Listing.price_per_sqm_detailed.isnot(None),
                Listing.price_per_sqm_detailed >= price_min,
            )
        elif price_max is not None:
            # Only max specified
            price_sqm_match = and_(
                Listing.price_sqm_zl.isnot(None), Listing.price_sqm_zl <= price_max
            )
            price_detailed_match = and_(
                Listing.price_per_sqm_detailed.isnot(None),
                Listing.price_per_sqm_detailed <= price_max,
            )

        if price_sqm_match is not None or price_detailed_match is not None:
            # Match if either field is within range
            or_conditions = []
            if price_sqm_match is not None:
                or_conditions.append(price_sqm_match)
            if price_detailed_match is not None:
                or_conditions.append(price_detailed_match)
            if or_conditions:
                conditions.append(or_(*or_conditions))

    # Filter by rooms (IN clause)
    if filter_data.rooms is not None and len(filter_data.rooms) > 0:
        conditions.append(Listing.rooms.in_(filter_data.rooms))

    # Filter by city
    if filter_data.city is not None and filter_data.city.strip():
        conditions.append(Location.city == filter_data.city.strip())

    # Filter by city_district
    if filter_data.city_district is not None and filter_data.city_district.strip():
        conditions.append(Location.city_district == filter_data.city_district.strip())

    # Build base query with join to Location
    query = select(Listing).join(Location, Listing.location_id == Location.location_id)

    # Apply all conditions - if no conditions, return empty result (or all if that's desired)
    if conditions:
        query = query.where(and_(*conditions))

    # Get total count with same conditions
    count_query = select(func.count(Listing.listing_id)).join(
        Location, Listing.location_id == Location.location_id
    )
    if conditions:
        count_query = count_query.where(and_(*conditions))
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # Execute query with eager loading of location
    query = query.options(joinedload(Listing.location))
    result = await db.execute(query)
    listings = result.unique().scalars().all()

    # Convert to response models
    listing_list = []
    for listing in listings:
        location_info = LocationInfo(
            location_id=listing.location.location_id,
            city=listing.location.city,
            locality=listing.location.locality,
            city_district=listing.location.city_district,
            street=listing.location.street,
            full_address=listing.location.full_address,
            latitude=listing.location.latitude,
            longitude=listing.location.longitude,
        )

        listing_list.append(
            ListingWithLocationResponse(
                listing_id=listing.listing_id,
                rooms=listing.rooms,
                area=listing.area,
                price_total_zl=listing.price_total_zl,
                price_sqm_zl=listing.price_sqm_zl,
                price_per_sqm_detailed=listing.price_per_sqm_detailed,
                date_posted=listing.date_posted,
                photo_count=listing.photo_count,
                url=listing.url,
                image_url=listing.image_url,
                description_text=listing.description_text,
                location=location_info,
            )
        )

    return FilteredListingsResponse(
        listings=listing_list,
        total=total,
    )
