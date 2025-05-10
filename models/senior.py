import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .medication import Prescription, Symptom
    from .user import User


class Senior(SQLModel, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )
    name: str
    birth_date: datetime
    identifier: str = Field(unique=True, index=True)
    symptoms: List["Symptom"] = Relationship(back_populates="senior")
    prescriptions: List["Prescription"] = Relationship(back_populates="senior")
    created_at: datetime = Field(default_factory=datetime.utcnow)
