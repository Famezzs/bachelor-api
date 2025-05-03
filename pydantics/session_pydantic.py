from datetime import datetime
from pydantic import Field

class SessionPydantic:
    from pydantic import BaseModel

    class SessionRequest(BaseModel):
        student_id: int = Field(..., example=1)
        length_minutes: int = Field(..., example=60)
        reactions_total: int = Field(..., example=60)

    class SessionResponse(BaseModel):
        session_id: int

    class SessionFilter(BaseModel):
        student_id: int | None = Field(None, example=1, description="Filter by specific student")
        start_date: datetime | None = Field(None, example="2025-01-01T00:00:00Z", description="Start date filter")
        end_date: datetime | None = Field(None, example="2025-12-31T23:59:59Z", description="End date filter")
        min_duration: int | None = Field(None, example=30, ge=1, description="Minimum session duration in minutes")
        max_duration: int | None = Field(None, example=120, ge=1, description="Maximum session duration in minutes")

    class SessionResponseExtended(SessionResponse):
        student_name: str = Field(..., example="John Doe")
        student_id: int = Field(..., example=1) 