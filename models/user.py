import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .senior import Senior


class UserRole(str, enum.Enum):
    caregiver = "caregiver"
    doctor = "doctor"


class User(SQLModel, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )
    name: str
    email: str = Field(unique=True, index=True)
    password: str
    role: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
