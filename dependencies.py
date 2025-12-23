from typing import Annotated

from fastapi import Query


def get_pagination_params(
    skip: Annotated[int, Query(ge=0, description="Number of records to skip for pagination")] = 0,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Maximum number of records to return")
    ] = 100,
) -> tuple[int, int]:
    """
    Common dependency for pagination query parameters.

    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 100)

    Returns:
        tuple[int, int]: Tuple of (skip, limit) values
    """
    return skip, limit
