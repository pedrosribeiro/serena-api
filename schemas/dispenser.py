from typing import List

from pydantic import BaseModel

from .compartment import CompartmentRead


class DispenserBase(BaseModel):
    device_id: str


class DispenserCreate(DispenserBase):
    pass


class DispenserRead(DispenserBase):
    id: str
    compartments: List[CompartmentRead] = []
