from sqlmodel import Field, SQLModel


class UserSenior(SQLModel, table=True):
    user_id: str = Field(foreign_key="user.id", primary_key=True)
    senior_id: str = Field(foreign_key="senior.id", primary_key=True)
