"""
Pytest configuration and fixtures for the project.

This module provides shared test fixtures for:
- Test database setup and teardown
- FastAPI test client
- Database session management
"""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from sqlmodel import SQLModel

from main import app
from models.database import get_db

# Test database URL - using in-memory SQLite for faster tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_engine():
    """
    Create a test database engine with in-memory SQLite.
    Each test function gets a fresh database.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # Set to True for SQL query debugging
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Cleanup
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.
    Each test gets a fresh session that is rolled back after the test.
    """
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def test_session_with_commit(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session that commits changes.
    Use this when you need to test committed transactions.
    """
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.commit()


@pytest.fixture(scope="function")
def override_get_db(test_session):
    """
    Override the get_db dependency to use the test session.
    This allows tests to use the FastAPI dependency injection system.
    """

    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_session

    return _get_test_db


@pytest.fixture(scope="function")
async def test_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a FastAPI test client with overridden database dependency.
    Use this for testing API endpoints.
    """
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Cleanup: remove dependency override after test
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_client_no_db() -> AsyncGenerator[AsyncClient, None]:
    """
    Create a FastAPI test client without database dependency override.
    Use this for testing endpoints that don't require database access.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_db_offer():
    """
    Fixture that returns a dictionary with complete offer data.
    Contains all fields from Listing model and related tables (Location, Building, Owner, Features).
    """
    return {
        # Listing fields
        "listing_id": 1,
        "location_id": 1,
        "building_id": 1,
        "owner_id": 1,
        "features_id": 1,
        "rooms": 3,
        "area": 65.50,
        "price_total_zl": 450000.00,
        "price_sqm_zl": 9000.00,
        "price_per_sqm_detailed": 9000.00,
        "date_posted": "2024-01-15",
        "photo_count": 12,
        "url": "https://example.com/listing/1",
        "image_url": "https://example.com/images/1.jpg",
        "description_text": "Beautiful apartment in city center with modern amenities",
        # Location fields
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
        # Building fields
        "building": {
            "building_id": 1,
            "year_built": 2010,
            "building_type": "blok",
            "floor": 5,
        },
        # Owner fields
        "owner": {
            "owner_id": 1,
            "owner_type": "Bez pośredników",
            "contact_name": "Jan Kowalski",
            "contact_phone": "+48123456789",
            "contact_email": "jan.kowalski@example.com",
        },
        # Features fields
        "features": {
            "features_id": 1,
            "has_basement": True,
            "has_parking": True,
            "kitchen_type": "osobna",
            "window_type": "plastikowe",
            "ownership_type": "własność",
            "equipment": "Wyposażenie: kuchenka, lodówka, piekarnik, pralka, zmywarka",
        },
    }
