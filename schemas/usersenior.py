from pydantic import BaseModel


class UserSeniorBase(BaseModel):
    user_id: str
    senior_id: str  # CPF string de 11 dígitos


class UserSeniorCreate(UserSeniorBase):
    pass


class UserSeniorRead(UserSeniorBase):
    pass
