import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .dispenser import Dispenser
    from .senior import Senior


class Device(SQLModel, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )
    senior_id: str = Field(foreign_key="senior.id")  # CPF string de 11 dígitos
    status: str
    last_sync: datetime = Field(default_factory=datetime.utcnow)
    senior: Optional["Senior"] = Relationship()
    dispenser: Optional["Dispenser"] = Relationship(back_populates="device")
