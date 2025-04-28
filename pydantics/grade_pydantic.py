from datetime import datetime
from pydantic import Field

class GradePydantic:
    from pydantic import BaseModel
    
    class GradeCreate(BaseModel):
        student_id: int = Field(..., example=1)
        date: datetime = Field(..., example="2025-04-27T12:34:56Z")
        score: float = Field(..., example=95.5, ge=0, le=100)
        comments: str | None = Field(None, example="Excellent work!")

    class GradeResponse(BaseModel):
        id: int
        date: datetime
        student_id: int
        teacher_id: int
        score: float
        comments: str | None

    class GradeFilter(BaseModel):
        student_id: int | None = Field(None, example=1, description="Filter by specific student")
        start_date: datetime | None = Field(None, example="2025-01-01T00:00:00Z", description="Start date filter")
        end_date: datetime | None = Field(None, example="2025-12-31T23:59:59Z", description="End date filter")
        min_score: float | None = Field(None, example=70.0, ge=0, le=100, description="Minimum score filter")
        max_score: float | None = Field(None, example=100.0, ge=0, le=100, description="Maximum score filter")