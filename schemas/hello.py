from pydantic import BaseModel, ConfigDict, Field


class HelloResponse(BaseModel):
    """Odpowiedź z endpointu hello"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Hello John",
            }
        }
    )

    message: str = Field(..., description="Spersonalizowany komunikat powitalny")
