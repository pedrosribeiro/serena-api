from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str


class UserRead(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str
