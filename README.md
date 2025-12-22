# Project Tools API

API for managing real estate listings and locations built with FastAPI, SQLAlchemy, and SQLite.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Database](#database)
- [Data Import](#data-import)
- [Testing](#testing)
- [Development](#development)
- [Using Search Filters](#using-search-filters)

## ✨ Features

- **RESTful API** built with FastAPI
- **Asynchronous database operations** using SQLAlchemy 2.0 with async support
- **SQLite database** with Alembic migrations
- **Data validation** with Pydantic v2
- **Health check endpoint** for monitoring
- **CSV data import** functionality for real estate listings
- **Saved search filters** for quick property searches
- **Comprehensive test suite** using pytest
- **API documentation** with automatic Swagger UI and ReDoc

## 🛠 Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: SQLite with aiosqlite
- **ORM**: SQLAlchemy 2.0 (async)
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **Testing**: pytest with pytest-asyncio
- **Server**: Uvicorn

## 📦 Requirements

- Python 3.8+
- pip

## 🚀 Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd project_tools
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

The application uses SQLite by default with the following configuration:

- **Database URL**: `sqlite+aiosqlite:///./sql_app.db`
- **Database file**: `sql_app.db` (created automatically in project root)

### Database Configuration

The database configuration is located in `models/database.py`:
- Async engine with `check_same_thread=False` for SQLite
- Echo mode enabled for SQL query logging (can be disabled in production)

## 🏃 Running the Application

### Development Mode

Using the new FastAPI CLI (recommended):
```bash
fastapi dev main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

### Production Mode

```bash
fastapi run
```

Or with uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📁 Project Structure

```
project_tools/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files
│   └── env.py                  # Alembic environment config
├── data/                       # Data files
│   └── ogloszenia_warszawa_detailed.csv
├── models/                     # SQLAlchemy models
│   ├── base.py                 # Base model class
│   ├── database.py             # Database connection and session
│   └── models.py               # Data models (Location, Building, Owner, Features, Listing)
├── routers/                    # API route handlers
│   ├── health.py               # Health check endpoint
│   ├── hello.py                # Hello world endpoints
│   ├── location.py             # Location endpoints
│   └── filters.py              # Search filters endpoints
├── schemas/                    # Pydantic schemas
│   ├── health.py               # Health check response schemas
│   ├── hello.py                # Hello response schemas
│   ├── location.py             # Location response schemas
│   └── filter.py               # Filter request/response schemas
├── tests/                      # Test suite
│   ├── conftest.py             # pytest configuration and fixtures
│   └── test_health.py          # Health endpoint tests
├── alembic.ini                 # Alembic configuration
├── import_listings.py          # CSV import script
├── main.py                     # FastAPI application entry point
├── pytest.ini                  # pytest configuration
└── requirements.txt            # Python dependencies
```

## 🔌 API Endpoints

### Root
- **GET /** - API information and available endpoints

### Health Check
- **GET /health/** - Check API and database health status

### Hello
- **GET /hello** - Returns "Hello World" message
- **GET /hello/{name}** - Returns personalized greeting

### Locations
- **GET /locations/** - Get paginated list of all locations
  - Query parameters:
    - `skip` (optional, default: 0) - Number of records to skip for pagination
    - `limit` (optional, default: 100, max: 100) - Maximum number of records to return
  - Returns: List of locations with pagination metadata (total, skip, limit)
  - Example: `/locations/?skip=0&limit=50`
- **GET /locations/{location_id}** - Get detailed information about a specific location
  - Path parameter: `location_id` (integer) - Unique identifier of the location
  - Returns: Full location details including address and coordinates
  - Example: `/locations/1`

### Filters
- **POST /filters/** - Save a search filter
  - Request body: Filter configuration with price ranges, rooms, and location
  - Returns: Saved filter with generated ID and timestamp
  - Example: See [Using Search Filters](#using-search-filters) section below
- **GET /filters/** - Get paginated list of all saved filters
  - Query parameters:
    - `skip` (optional, default: 0) - Number of records to skip for pagination
    - `limit` (optional, default: 100, max: 100) - Maximum number of records to return
  - Returns: List of saved filters with pagination metadata
  - Example: `/filters/?skip=0&limit=10`
- **GET /filters/{filter_id}** - Get detailed information about a specific saved filter
  - Path parameter: `filter_id` (integer) - Unique identifier of the filter
  - Returns: Full filter details including all search criteria
  - Example: `/filters/1`

### Documentation
- **GET /docs** - Interactive API documentation (Swagger UI)
- **GET /redoc** - Alternative API documentation (ReDoc)

## 🗄 Database

### Database Models

The application uses the following database models:

1. **Location** - Geographic information
   - city, locality, city_district, street
   - full_address, latitude, longitude

2. **Building** - Building details
   - year_built, building_type, floor

3. **Owner** - Owner information
   - owner_type, contact details

4. **Features** - Property features
   - has_basement, has_parking
   - kitchen_type, window_type
   - ownership_type, equipment

5. **Listing** - Real estate listings
   - rooms, area, price information
   - date_posted, photo_count
   - url, image_url, description
   - Foreign keys to Location, Building, Owner, Features

6. **SavedFilter** - Saved search filters
   - name, price ranges (min/max for total and per m²)
   - rooms (JSON array), city, city_district
   - created_at timestamp

### Migrations

The project uses Alembic for database migrations.

**Create a new migration**:
```bash
alembic revision --autogenerate -m "Description of changes"
```

**Apply migrations**:
```bash
alembic upgrade head
```

**Rollback migrations**:
```bash
alembic downgrade -1
```

**View migration history**:
```bash
alembic history
```

### Database Initialization

The database tables are automatically created on application startup using the lifespan context manager in `main.py`.

## 📥 Data Import

The project includes a script to import real estate listings from CSV files.

**Run the import script**:
```bash
python import_listings.py
```

The script:
- Reads data from `data/ogloszenia_warszawa_detailed.csv`
- Cleans and validates all data
- Creates or updates Location, Building, Owner, and Features records
- Imports listings with proper relationships
- Handles duplicates and data integrity

### Import Features

- Data cleaning and validation
- Decimal and integer parsing
- Date parsing with multiple formats
- Boolean field conversion
- Duplicate detection based on URL
- Transaction-based processing for data integrity
- Detailed logging of import process

## 🧪 Testing

The project uses pytest with async support for testing.

**Run all tests**:
```bash
pytest
```

**Run with verbose output**:
```bash
pytest -v
```

**Run specific test file**:
```bash
pytest tests/test_health.py
```

**Run with coverage**:
```bash
pytest --cov=.
```

### Test Configuration

- Test configuration in `pytest.ini`
- Fixtures and test database setup in `tests/conftest.py`
- Async test support via `pytest-asyncio`

## 🔍 Using Search Filters

The API allows you to save search filters for quick property searches. Filters support price ranges, room counts, and location criteria.

### Filter Features

- **Price Range Sliders**: Filter by total price and price per square meter
  - `price_total`: Range for total price in PLN (min/max)
  - `price_per_sqm`: Range for price per square meter in PLN/m² (min/max)
- **Multi-select Rooms**: Filter by multiple room counts simultaneously
  - `rooms`: Array of integers (e.g., `[2, 3]` for 2 and 3 room apartments)
- **Location Autocomplete**: Filter by city and district
  - `city`: City name (e.g., "Warszawa")
  - `city_district`: District name (e.g., "Śródmieście")

### Saving a Filter

**Endpoint**: `POST /filters/`

**Request Body**:
```json
{
  "name": "My apartment search",
  "price_total": {
    "min": 300000.00,
    "max": 600000.00
  },
  "price_per_sqm": {
    "min": 8000.00,
    "max": 12000.00
  },
  "rooms": [2, 3],
  "city": "Warszawa",
  "city_district": "Śródmieście"
}
```

**Response** (201 Created):
```json
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
  "created_at": "2024-01-15T10:30:00"
}
```

### Example: Using cURL

**Save a filter**:
```bash
curl -X POST "http://localhost:8000/filters/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Budget apartments in Warsaw",
    "price_total": {
      "min": 200000.00,
      "max": 400000.00
    },
    "rooms": [1, 2],
    "city": "Warszawa"
  }'
```

**Get all saved filters**:
```bash
curl "http://localhost:8000/filters/?skip=0&limit=10"
```

**Get specific filter**:
```bash
curl "http://localhost:8000/filters/1"
```

### Example: Using Python

```python
import requests

# Save a filter
filter_data = {
    "name": "Luxury apartments",
    "price_total": {
        "min": 500000.00,
        "max": 1000000.00
    },
    "price_per_sqm": {
        "min": 10000.00,
        "max": 15000.00
    },
    "rooms": [3, 4],
    "city": "Warszawa",
    "city_district": "Mokotów"
}

response = requests.post("http://localhost:8000/filters/", json=filter_data)
saved_filter = response.json()
print(f"Saved filter ID: {saved_filter['filter_id']}")

# Get all filters
response = requests.get("http://localhost:8000/filters/")
filters = response.json()
print(f"Total saved filters: {filters['total']}")
```

### Filter Validation

- **name**: Required, 1-255 characters
- **price_total**: Optional, both min and max are optional
- **price_per_sqm**: Optional, both min and max are optional
- **rooms**: Optional, array of positive integers (minimum 1)
- **city**: Optional, max 255 characters
- **city_district**: Optional, max 255 characters

All price values are in PLN (Polish Złoty) and can include decimal places.

## 👨‍💻 Development

### Code Style

The project follows these conventions:
- **Async operations**: Use `async def` for all database operations
- **Type hints**: All functions have type annotations
- **Dependency Injection**: Use `Annotated` with FastAPI `Depends`
- **Response models**: All endpoints have defined `response_model`
- **File naming**: Lowercase with underscores (snake_case)
- **Comments**: Written in English

### Adding New Endpoints

1. Create a Pydantic schema in `schemas/`
2. Create a router in `routers/`
3. Include the router in `main.py`
4. Add tests in `tests/`

### Adding New Models

1. Define SQLAlchemy model in `models/models.py`
2. Create migration: `alembic revision --autogenerate -m "Add model"`
3. Apply migration: `alembic upgrade head`
4. Create corresponding Pydantic schemas in `schemas/`

## 📝 Environment Variables

Currently, the application uses default configuration. For production, consider adding:

- `DATABASE_URL` - Custom database connection string
- `DEBUG` - Debug mode toggle
- `LOG_LEVEL` - Logging level configuration

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

[Add your license information here]

## 👥 Authors

[Add author information here]

---

**API Version**: 1.0.0

For more information, visit the [interactive API documentation](http://localhost:8000/docs) after starting the server.

