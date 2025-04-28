from pydantic import Field
from constants.user_type import UserType

class UserPydantic:
    from pydantic import BaseModel

    class UserCreate(BaseModel):
        first_name: str = Field(..., example="Alice")
        last_name: str = Field(..., example="Smith")
        username: str = Field(..., example="alice.smith")
        password: str = Field(..., example="securePassword123")
        user_type: str = Field(..., example=UserType.STUDENT)

    class UserResponse(BaseModel):
        id: int
        first_name: str
        last_name: str
        user_type: str