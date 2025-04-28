from enum import Enum

class UserType(str, Enum):
    UNDEFINED = "undefined"
    STUDENT = "student"
    TEACHER = "teacher"