import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .senior import Senior


class Symptom(SQLModel, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )
    senior_id: str = Field(foreign_key="senior.id")
    description: str
    pain_level: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    senior: Optional["Senior"] = Relationship(back_populates="symptoms")
