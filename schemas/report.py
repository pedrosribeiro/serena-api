from typing import Optional

from pydantic import BaseModel


class ReportBase(BaseModel):
    content: str
    created_at: str


class ReportCreate(ReportBase):
    pass


class ReportRead(ReportBase):
    id: int
    user_id: int
