from pydantic import Field


class AuthPydantic:
    from pydantic import BaseModel

    class AuthRequest(BaseModel):
        username: str = Field(..., example="user123")
        password: str = Field(..., example="strong_password")
    
    class AuthResponse(BaseModel):
        access_token: str
        token_type: str = "bearer"
        user_type: str
        user_id: int