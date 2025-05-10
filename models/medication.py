import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .prescription import Prescription
    from .senior import Senior


class Medication(SQLModel, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )
    name: str
    description: Optional[str] = None
    prescriptions: List["Prescription"] = Relationship(back_populates="medication")
