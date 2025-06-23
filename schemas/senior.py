from typing import Optional

from pydantic import BaseModel, constr


class SeniorBase(BaseModel):
    name: str
    birth_date: str


class SeniorCreate(SeniorBase):
    id: str  # CPF string de 11 dígitos
    device_id: str

    @classmethod
    def validate_id(cls, value):
        if not (isinstance(value, str) and value.isdigit() and len(value) == 11):
            raise ValueError("O ID deve ser um CPF válido (11 dígitos numéricos)")
        return value

    def __init__(self, **data):
        data["id"] = self.validate_id(data.get("id", ""))
        super().__init__(**data)


class SeniorRead(SeniorBase):
    id: str
    device_id: str | None = None
    birth_date: str
    created_at: str
