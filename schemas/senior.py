from typing import Optional

from pydantic import BaseModel


class SeniorBase(BaseModel):
    name: str
    birth_date: str


class SeniorCreate(SeniorBase):
    device_id: str


class SeniorRead(SeniorBase):
    id: str
    device_id: str | None = None
    birth_date: str
    created_at: str
