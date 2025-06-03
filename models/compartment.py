import uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .dispenser import Dispenser
    from .medication import Medication


class Compartment(SQLModel, table=True):
    compartment_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )
    dispenser_id: str = Field(foreign_key="dispenser.id")
    medication_id: str = Field(foreign_key="medication.id")
    quantity: int
    dispenser: Optional["Dispenser"] = Relationship(back_populates="compartments")
    medication: Optional["Medication"] = Relationship()
