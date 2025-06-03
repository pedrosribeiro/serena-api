import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .compartment import Compartment
    from .device import Device


class Dispenser(SQLModel, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )
    device_id: str = Field(foreign_key="device.id")
    device: Optional["Device"] = Relationship(back_populates="dispenser")
    compartments: List["Compartment"] = Relationship(back_populates="dispenser")
