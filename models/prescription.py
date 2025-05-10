import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .medication import Medication
    from .senior import Senior


class Prescription(SQLModel, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )
    senior_id: str = Field(foreign_key="senior.id")
    medication_id: str = Field(foreign_key="medication.id")
    dosage: str
    frequency: str
    start_date: datetime
    end_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    senior: Optional["Senior"] = Relationship(back_populates="prescriptions")
    medication: Optional["Medication"] = Relationship(back_populates="prescriptions")
