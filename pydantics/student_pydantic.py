from pydantic import Field

class StudentPydantic:
    from pydantics.user_pydantic import UserPydantic

    class StudentCreate(UserPydantic.UserCreate):
        assigned_teacher_id: int | None = Field(None, example=2)

    class StudentResponse(UserPydantic.UserResponse):
        assigned_teacher_id: int | None