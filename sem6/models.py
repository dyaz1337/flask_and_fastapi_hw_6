from pydantic import BaseModel, Field, EmailStr
from datetime import date


class UserInT1(BaseModel):
    username: str = Field(max_length=32)
    email: str = Field(max_length=128)
    password: str = Field(max_length=64)


class UserT1(UserInT1):
    id: int


class UserInT2(BaseModel):
    first_name: str = Field(min_length=2, max_length=32)
    last_name: str = Field(min_length=2, max_length=32)
    birthday: date = Field(...)
    email: EmailStr = Field(max_length=90)
    address: str = Field(min_length=5, max_length=128)


class UserT2(UserInT2):
    id: int


class TaskInT3(BaseModel):
    title: str = Field(max_length=32)
    description: str = Field(max_length=128)
    done: bool = Field(...)


class TaskT3(TaskInT3):
    id: int
