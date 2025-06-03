from pydantic import BaseModel


class UserSeniorBase(BaseModel):
    user_id: str
    senior_id: str


class UserSeniorCreate(UserSeniorBase):
    pass


class UserSeniorRead(UserSeniorBase):
    pass
