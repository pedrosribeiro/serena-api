from pydantic import BaseModel

from .user import UserRead


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserRead


class TokenData(BaseModel):
    username: str | None = None
