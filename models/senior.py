import re
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .device import Device
    from .medication import Prescription, Symptom
    from .user import User


class Senior(SQLModel, table=True):
    id: str = Field(primary_key=True, index=True, regex=r"^\d{11}$")
    name: str
    birth_date: str = Field()
    symptoms: List["Symptom"] = Relationship(back_populates="senior")
    prescriptions: List["Prescription"] = Relationship(back_populates="senior")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    device: Optional["Device"] = Relationship(back_populates="senior")
