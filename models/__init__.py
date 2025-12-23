from .base import Base
from .models import (
    Building,
    Features,
    Listing,
    Location,
    Owner,
)


# Lazy import for database to avoid loading async engine during Alembic migrations
def _get_database():
    from .database import engine, get_db

    return engine, get_db


__all__ = [
    "Base",
    "Location",
    "Building",
    "Owner",
    "Features",
    "Listing",
    "_get_database",
]
